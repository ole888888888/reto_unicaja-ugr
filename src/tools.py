import datetime
import json
import re
from decimal import Decimal

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from sqlmodel import select

from src.database import get_session
from src.models import FAQ, Cliente, Contacto, Transaccion
from src.services.categorizador import obtener_categoria
from src.services.client import read_client_info
from src.services.transactions import read_transactions_info


@tool
def read_client_information(config: RunnableConfig) -> str:
    """
    Utiliza esta herrmienta si necesitas algo de información del usuario, ya sea porque te lo ha pedido,
    o porque lo consideras necesario para responder. 
    Lee la información del usuario conectado, la información incluye el id de usuario, su nombre, su email, su saldo, su teléfono y su ciudad.
    """
    client_id = config.get("configurable", {}).get("user_id")

    if not client_id:
        return "Cliente no autentificado, no se pude continuar."

    return read_client_info(client_id)

@tool
def get_current_date_and_time():
    """Devuelve la fecha y la hora actual en formato ISO 8601"""
    return datetime.datetime.now(tz=datetime.UTC).isoformat()
    
@tool
def read_transactions_information(config: RunnableConfig, start_date: str|None = None, end_date: str|None = None, min_amount: float|None = None, max_amount: float|None = None, category:str|None = None) -> str:
    """
    Devuelve las transacciones filtradas del usuario activo, puedes clasificar por fechas, cantidad de transaccion o categoría.
    Las fechas están en formato 'YYYY-MM-DD' y el dinero en euros.
    """

    # Esto lo hacemos para la selección del usuario que tiene la sesión iniciada
    client_id = config.get("configurable", {}).get("user_id")

    # Si no encontramos un usuario no podemos continuar.
    if not client_id:
        return "Cliente no autetificado, no se puede continuar."

    return read_transactions_info(client_id,start_date,end_date,min_amount,max_amount,category)

@tool
def make_transfer(config: RunnableConfig, cantidad: float, concepto: str, tel: str) -> str:
    """
    Hace una transferencia para un cierto número de teléfono, el cual debe estar en los contactos, una cierta cantidad y un concepto.
    Usa la misma herramienta si tuvieses que hacer un bizum.
    """

    client_id = config.get("configurable", {}).get("user_id")

    if not client_id:
        return "Cliente no autentificado, no se puede continuar"
    
    if cantidad <= 0:
        return "El importe debe ser positivo"
    
    # Validamos los números de teléfono introducidos.
    # ^ inicio de regex
    # \+? 1 o 0 mases
    # \d{9,15} 9 a 15 dígitos
    if not tel or not re.match(r"^\+?\d{9,15}$", tel):
        return "número de teléfono introducido es incorrecto"

    with next(get_session()) as session:
        amount:Decimal = Decimal(str(cantidad))
        statement = select(Cliente).where(Cliente.id == client_id)
        result = session.exec(statement).first()

        if result:
            # Buscamos el contacto.
            contacto_destino = next((c for c in result.contactos if c.tel == tel), None)
            if result.saldo_actual >= amount and contacto_destino:
                result.saldo_actual -= amount

                # Añadimos el movimiento a la base de datos.
                nueva_trans = Transaccion(
                    tipo="transferencia_enviada",
                    monto=amount,
                    detalles=concepto,
                    categoria=obtener_categoria(concepto),
                    cliente_id=client_id,
                )

                session.add(nueva_trans)
                session.commit()
                return f"Transfer successful. New balance for client {client_id}: {result.saldo_actual}"
            else:
                return "Fondos insuficientes."
        else:
            return "No se encontró el contacto."


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
    make_transfer,
    get_bank_faqs,
    get_contacts,
    delete_contact,
    add_contact,
]
