import datetime
import json

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from sqlmodel import select

from src.database import get_session
from src.models import FAQ, Contacto
from src.services.client import read_client_info
from src.services.transactions import make_transfer, read_transactions_info

#In this file we can find the tools which the llm has access to, the logic is separated in the folder services.

@tool
def read_client_information(config: RunnableConfig) -> str:
    """
    Retrieve profile information for the currently authenticated user.

    Use this tool whenever you need details about the logged-in user, either
    because they explicitly asked for it or because it is required to answer a query.
    
    The retrieved details include the user's ID, full name, email address,
    current account balance, phone number, and city.

    Args:
        config (RunnableConfig): Runtime configuration automatically injected by LangChain
            containing context metadata, such as the authenticated user ID.

    Returns:
        str: A string with the user's profile information or an error message if the
    """
    client_id = config.get("configurable", {}).get("user_id")

    if not client_id:
        return "Unauthenticated client, can't proceed."

    return read_client_info(client_id)

@tool
def get_current_date_and_time():
    """
    Retrieve the current date and time in UTC formatted as an ISO 8601 string.

    Use this tool whenever you need to know the present date, time, or year,
    especially for calculating relative dates (e.g., 'today', 'yesterday',
    'this month', or checking recent transactions).

    Returns:
        str: The current UTC timestamp in ISO 8601 format (e.g., '2026-07-24T19:23:49+00:00').
    """
    return datetime.datetime.now(tz=datetime.UTC).isoformat()
    
@tool
def read_transactions_information( config: RunnableConfig,
                                start_date: str|None = None,
                                end_date: str|None = None, 
                                min_amount: float|None = None, 
                                max_amount: float|None = None, 
                                category:str|None = None
                                ) -> str:
    """
    Retrieve and filter transaction history for the currently authenticated user.

    Use this tool whenever the user asks about their past spending, income, or transaction
    history. You can apply filters by date range, transaction amount (in Euros €),
    or category.

    Args:
        config (RunnableConfig): Runtime configuration automatically injected by LangChain
            containing context metadata, such as the authenticated user ID.
        start_date (str | None, optional): Start date for filtering in 'YYYY-MM-DD' format.
            Defaults to None.
        end_date (str | None, optional): End date for filtering in 'YYYY-MM-DD' format.
            Defaults to None.
        min_amount (float | None, optional): Minimum transaction amount in Euros (€).
            Defaults to None.
        max_amount (float | None, optional): Maximum transaction amount in Euros (€).
            Defaults to None.
        category (str | None, optional): Category name to filter transactions
            (e.g., 'supermarket', 'restaurants', 'transfers'). Defaults to None.

    Returns:
        str: A string listing the matching transactions or an error message if the
            user is not authenticated.
    """

    client_id = config.get("configurable", {}).get("user_id")

    if not client_id:
        return "Unauthenticated client, can't proceed."

    return read_transactions_info(client_id,start_date,end_date,min_amount,max_amount,category)

@tool
def make_transfer_tool(config: RunnableConfig, amount: float, concepto: str, tel: str) -> str:
    """
    Execute a money transfer or Bizum to a saved contact using their phone number.

    Use this tool whenever the user asks to send money, make a transfer, or send a 'Bizum'
    to a recipient using their phone number. The recipient must be in the user's contacts.

    Args:
        config (RunnableConfig): Runtime configuration automatically injected by LangChain
            containing context metadata, such as the authenticated user ID.
        amount (float): The amount of money to transfer in Euros (€). Must be greater than 0.
        concepto (str): The description, concept, or note for the transfer.
        tel (str): The recipient's phone number in E.164 format (e.g., '+34612345678').

    Returns:
        str: A string indicating whether the transfer was successful (including the updated balance)
            or an error message if the transaction failed.
    """

    client_id = config.get("configurable", {}).get("user_id")

    if not client_id:
        return "Unautheticated client, can't proceed."
    
    return make_transfer (client_id,amount,concepto,tel)


@tool
def get_bank_faqs(query: str) -> str:
    """
    Accede a las preguntas frecuentes del banco para el que trabajas,
    Usa esta herrmienta siempre que el usuario pregunte algo a lo que tú no puedas responder directamente,
    si tú tampoco consigues encontrar nada relevante en tu base de datos dirígelos al contacto oficial del banco,
    priorizamos esto a que estén mal las respuestas.
    """
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    try:
        vector_usuario = embedder.embed_query(query)

    except Exception:
        return "Error al procesar la consulta con el servicio de IA"

    with next(get_session()) as session:
        statement = (
            select(FAQ).order_by(FAQ.embedding.cosine_distance(vector_usuario)).limit(2)
        )

        resultados = session.exec(statement).all()

        if not resultados:
            return "No se ha encontrado información relevante en el manual del banco"

        respuesta_herramienta = (
            "Información oficial encontrada en las FAQs de Unicaja:\n"
        )
        for faq in resultados:
            respuesta_herramienta += f"\n- Pregunta frecuente: {faq.pregunta}\n Respuesta oficial: {faq.respuesta}\n"

        return respuesta_herramienta

@tool 
def get_contacts (config: RunnableConfig, name: str|None) -> str:
    """
    Devuelve todos los contactos que tiene el usuario. Si te pide los usuarios se los pasas.
    Si te pide uno solo, utiliza esta herrmienta pero extrae solo el que te pide.
    """
    
    client_id = config.get("configurable", {}).get("user_id")

    if not client_id:
        return "Unauthenticated client, can't procede."

    else:
        with next(get_session()) as session:
            statement = select(Contacto).where(Contacto.cliente_id == client_id)
            resultados = session.exec(statement).all()

            if resultados:
                contactos_json = [
                    {
                        "nombre": resultado.nombre,
                        "tel": resultado.tel
                    }
                    for resultado in resultados
                ]

                return json.dumps(contactos_json,ensure_ascii=False)
            
            else:
                return "No se encontró ningún contacto."

@tool
def add_contact (config: RunnableConfig, nombre: str|None, tel: str) -> str:
    """
    Te permite añadir un contacto, necesitarás el número de teléfono obligatoriamente, el nombre sin embargo no es necesario.
    """

    client_id = config.get("configurable", {}).get("user_id")

    if not client_id:
        return "Cliente no autentificado, no se puede continuar."

    with next(get_session()) as session:
        nuevo_contacto = Contacto (
            nombre=nombre,
            tel=tel,
            cliente_id=client_id
        )

        session.add(nuevo_contacto)
        session.commit()
        return "Contacto añadido con éxito."

@tool 
def delete_contact (config: RunnableConfig, tel: str) -> str:
    """
    Elimina un contacto dado su número de teléfono, si no proveen un número de teléfono pero un nombre, proporcionale una lista de contactos
    con nombres parecidos junto con sus números de teléfono. Solo podrás borrar si te dan el número de teléfono.
    """
    client_id = config.get("configurable", {}).get("user_id")

    if not client_id:
        return "Cliente no autentificado, no se puede continuar"
    
    with next(get_session()) as session:
        statement = select(Contacto).where(Contacto.tel == tel, Contacto.cliente_id == client_id)
        result = session.exec(statement).one()

        if not result:
            return "No se pudo encontrar el contacto con ese número de teléfono."

        session.delete(result)
        session.commit()

tools = [
    read_client_information,
    get_current_date_and_time,
    read_transactions_information,
    make_transfer_tool,
    get_bank_faqs,
    get_contacts,
    delete_contact,
    add_contact,
]
