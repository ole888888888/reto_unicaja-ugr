import json

from sqlmodel import func, select
from src.database import get_session
from src.models import Contacto
from src.services.phone import verify_phone_number


def get_contacts_logic (client_id: int, name: str|None = None) -> str:
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
            # Fuzzy search using trigram similarity.
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

def add_contact_logic (client_id: int, tel: str, name: str|None = None) -> str:
    """
    Adds a new contact to the specified client's contact list in the database.

    Validates the provided phone number before creating and persisting 
    the new contact record in the database.

    Args:
        client_id (int): The unique identifier of the client adding the contact.
        tel (str): The phone number for the new contact.
        name (str | None, optional): The name of the contact. Defaults to None.

    Returns:
        str: A message confirming successful creation, or an error message if 
            the phone number validation fails.
    """

    if not verify_phone_number(tel):
        return "Introduced phone number is not correct."

    with next(get_session()) as session:
        new_contact = Contacto(
            nombre=name,
            tel=tel,
            cliente_id=client_id
        )

        statement = select(Contacto).where(Contacto.tel == tel)
        if (session.exec(statement).first()):
            return "Contact already exists."    
        
        session.add (new_contact)
        session.commit()
        return "Contact added successfully."

def delete_contact_logic (client_id: int, tel: str) -> str:
    """
    Deletes a contact record associated with a specific client ID and phone number.

    Args:
        client_id (int): The unique identifier of the client.
        tel (str): The phone number of the contact to be deleted.

    Returns:
        str: A confirmation message indicating whether the deletion was 
            successful or if the contact was not found.
    """
    
    with next(get_session()) as session:
        statement = select(Contacto).where(Contacto.cliente_id==client_id, Contacto.tel==tel)
        # Used .one() because we are only going to delete one user, any more would be a problem.
        result = session.exec(statement).one()

        if not result:
            return "Could not find the contact with that phone number."

        session.delete(result)
        session.commit()

        return f"Succesfully deleted the user with phone number {tel}"