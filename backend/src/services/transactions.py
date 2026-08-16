# Have to add Human in the loop for these functions.
import json
from datetime import datetime
from decimal import Decimal

from sqlmodel import select
from src.database import get_session
from src.models import Cliente, Direction, Transaccion
from src.services.categorizador import obtener_categoria
from src.services.phone import verify_phone_number


def read_transactions_info (client_id: int,
                            start_date: str|None = None,
                            end_date: str|None = None,
                            min_amount: float|None = None,
                            max_amount: float|None = None, 
                            category:str|None = None
                            ) -> str:
    """
    Retrieve financial transaction records based on optional filtering criteria.

    Args:
        client_id (int | None): The unique identifier of the client.
        start_date (str | None, optional): Initial date for filtering (e.g., 'YYYY-MM-DD'). Defaults to None.
        end_date (str | None, optional): Final date for filtering (e.g., 'YYYY-MM-DD'). Defaults to None.
        min_amount (float | None, optional): Lower bound for the transaction amount. Defaults to None.
        max_amount (float | None, optional): Upper bound for the transaction amount. Defaults to None.
        category (str | None, optional): Category name to filter transactions (e.g., 'groceries', 'utilities'). Defaults to None.

    Returns:
        str: A formatted string or JSON representation containing the matching transaction details.
    """

    with next(get_session()) as session:
        # Base statement
        statement = (
            select(Transaccion)
            .where(Transaccion.cliente_id == client_id)
        )

        # We add information to the statement would it be necessary.
        if start_date:
            compared_date = datetime.fromisoformat(start_date)
            statement = statement.where(Transaccion.fecha >= compared_date)

        if end_date:
            compared_date = datetime.fromisoformat(end_date)
            # We compare to the end of the day, for it to properly work.
            compared_date = compared_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            statement = statement.where(Transaccion.fecha <= compared_date)

        if min_amount:
            statement = statement.where(Transaccion.monto >= Decimal(str(min_amount)))

        if max_amount:
            statement = statement.where(Transaccion.monto <= Decimal(str(max_amount)))

        if category:
            statement = statement.where(Transaccion.categoria == category)

        statement = statement.order_by(Transaccion.fecha.asc()).limit(50) # Maybe the limit should be changed for charting functions.

        # We execute the statement built from all the previous steps.
        result = session.exec(statement).all()

        # Return the output in json format.
        if result:
            transacciones_json = [
                {
                    "fecha": tx.fecha.strftime('%d-%m-%y'),
                    "cantidad": float(tx.monto),
                    "direction": tx.direction,
                    "descripcion": tx.detalles,
                    "categoria": tx.categoria
                }
                for tx in result
            ]
            return json.dumps(transacciones_json, ensure_ascii=False)

        else:
            return "Could not find the transactions."

def make_transfer(client_id: int, amount_f:float, concepto: str, tel: str) -> str:
    """
    Execute a money transfer to a saved contact identified by their phone number.

    Args:
        client_id (int): The unique identifier of the sending client.
        amount_f (float): The amount of money to transfer. Must be greater than 0.
        concepto (str): The description, concept, or note for the transaction.
        tel (str): The recipient's phone number in E.164 format (e.g., '+34612345678').

    Returns:
        str: A message indicating whether the transfer succeeded (including the new balance)
            or an error message explaining why it failed.
    """

    if amount_f <= 0:
        return "The amount must be positive."

    # We have to verify the phone number introduced before proceeding.
    if not verify_phone_number(tel):
        return "The phone number is not valid."

    with next(get_session()) as session:
        # We transform the amount to decimal for precission.
        amount_d:Decimal = Decimal(str(amount_f))
        statement = select(Cliente).where(Cliente.id == client_id)

        result = session.exec(statement).one()

        if result:
            # Before checking if the contact exists we must check whether the user has the balance.
            if result.saldo_actual < amount_d:
                return "Your balance isn't high enough to do the transfer."

            # We use a generator inside next to search for the first contact with that phone number.
            # If none is found None is asigned.
            contacto_destino = next((c for c in result.contactos if c.tel == tel), None)
            if contacto_destino:
                # We do it like this even if in a professional scenario it would look different.
                result.saldo_actual -= amount_d

                # We add the transaction to the database.
                nueva_trans = Transaccion (
                    direction = Direction.OUTFLOW,
                    monto = amount_d,
                    detalles = concepto,
                    categoria = obtener_categoria(concepto),
                    cliente_id = client_id
                )
                session.add(nueva_trans)
                session.commit()

                return f"Transfer has been completed succesfully, new balance {result.nombre}: {result.saldo_actual}."
            
            else:
                return f"Couldn't find the contact with phone number {tel} in your contacts."
            
        return f"Could not find the client with id {client_id}."
        