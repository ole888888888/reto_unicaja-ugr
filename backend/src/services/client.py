import json

from sqlmodel import select
from src.database import get_session
from src.models import Cliente


# This file contains all logic regarding client information.
# In this way we can separate the logic from the tools the agent calls.
def read_client_info(client_id: int) -> str:
    with next(get_session()) as session:
        statement = select(Cliente).where(Cliente.id == client_id)
        result = session.exec(statement).first()

        # We return the information retrieved in json format.
        if result:
            cliente_res = {
                "id": result.id,
                "nombre": result.nombre,
                "email": result.email,
                "saldo_actual": float(result.saldo_actual),
                "telefono": result.telefono,
                "ciudad": result.ciudad,  
            }

            return json.dumps(cliente_res, ensure_ascii=False)

        else:
            return "Could not find the client."