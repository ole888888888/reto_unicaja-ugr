import json
from datetime import datetime
from decimal import Decimal

from sqlmodel import select

from src.database import get_session
from src.models import Transaccion


def read_transactions_info (client_id: int|None, start_date: str|None = None, end_date: str|None = None,
                             min_amount: float|None = None, max_amount: float|None = None, category:str|None = None) -> str:
    if not client_id:
        return "Can't continue without a client id."

    with next(get_session()) as session:
        # Ponemos el enunciado básico.
        statement = (
            select(Transaccion)
            .where(Transaccion.cliente_id == client_id)
        )

        # Vamos añadiendo partes al enunciado dependiendo de si lo necesitamos.
        if start_date:
            compared_date = datetime.fromisoformat(start_date)
            statement = statement.where(Transaccion.fecha >= compared_date)

        if end_date:
            compared_date = datetime.fromisoformat(end_date)
            # Colocamos el punto del tiempo a comparar al final del día.
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

        # Order y limit vienen de sqlalchemy, order es de la columna y limit es para el select.
        statement = statement.order_by(Transaccion.fecha.desc()).limit(20) #type: ignore

        # Finalmente ejecutamos la query, sacando exclusivamente las que cumplan las condiciones impuestas.
        result = session.exec(statement).all()

        # Devolvemos la salida.
        if result:
            transacciones_json = [
                {
                    "fecha": tx.fecha.strftime('%Y-%m-%d'),
                    "cantidad": tx.monto,
                    "tipo": tx.tipo,
                    "descripcion": tx.detalles,
                    "categoria": tx.categoria
                }
                for tx in result
            ]
            return json.dumps(transacciones_json, ensure_ascii=False)

        else:
            return "Transaction not found."