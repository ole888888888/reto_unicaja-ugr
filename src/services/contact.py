import json

from sqlmodel import func, select

from src.database import get_session
from src.models import Contacto


def get_contacts_info (client_id: int, name: str|None = None) -> str:
    """
    Retrieves contact information for a specific client from the database.

    Fetches all contacts belonging to `client_id`. If a `name` is provided, 
    it performs a fuzzy similarity search (requiring PostgreSQL's `pg_trgm` 
    extension) to filter and rank contacts by how closely their name matches 
    the search query.

    Args:
        client_id (int): The unique identifier of the client owning the contacts.
        name (str | None, optional): Name or keyword to search for. If None, 
            retrieves all contacts for the client. Defaults to None.

    Returns:
        str: A JSON-formatted string array containing the contacts' names and 
            phone numbers (`[{"nombre": ..., "tel": ...}]`), or a message 
            indicating no contacts were found.
    """

    with next(get_session()) as session:
        statement = select(Contacto).where(Contacto.cliente_id == client_id)

        if name:
            # We take the similarity of every name in the contact list and compare it with the name provided.
            # Have to add pg_trgm extension to the postgresql database.
            similarity = func.similarity(name, Contacto.nombre)

            # We add the similarity condition to the sql query.
            statement = (
                statement.
                where(similarity > 0.3).
                order_by(similarity.desc())
            )

        results = session.exec(statement).all()

        # Return the information as json.
        if results:
            contacts_json = [
                {
                    "nombre": result.nombre,
                    "tel": result.tel
                }
                for result in results
            ]

            return json.dumps(contacts_json, ensure_ascii=False)

        else:
            return "Could not find any contact with the information provided."