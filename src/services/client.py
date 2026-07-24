import json

from sqlmodel import select

from src.database import get_session
from src.models import Cliente

# Este archivo contiene toda la lógica de la información de cliente.
# De esta manera separamos la lógica como tal de las herrmientas a las que llama la IA.

def read_client_info(client_id: int|None) -> str:
    # Simple medidad de seguridad, para que no se llame sin un cliente.
    if not client_id:
        return "No se puede continuar sin un cliente"

    with next(get_session()) as session:
        statement = select(Cliente).where(Cliente.id == client_id)
        result = session.exec(statement).first()

        if result:
            cliente_res = {
                "id": result.id,
                "nombre": result.nombre,
                "email": result.email,
                "saldo_actual": result.saldo_actual,
                "telefono": result.telefono,
                "ciudad": result.ciudad,  
            }

            return json.dumps(cliente_res, ensure_ascii=False)

        else:
            return "No se encontró el cliente."