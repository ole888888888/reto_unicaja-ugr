# This program fills up our database with the mock banking information.
import json
import os
from decimal import Decimal

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from sqlmodel import Session, SQLModel, create_engine, select
from src.models import FAQ, Cliente, Contacto, Transaccion
from src.services.categorizador import obtener_categoria

# We load the postgresql database information.
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# This creates the database tables taking the models into account
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Deletes all tables, it's just used to restart the tables.
def drop_all_tables():
    SQLModel.metadata.drop_all(engine)

# Function that actually fills the database with the information.
def populate_banking_system():   
    with Session(engine) as session:
        print("Leyendo archivo datos_banco.json...")
        with open("data/datos_banco.json", "r", encoding="utf-8") as f:
            datos_origen = json.load(f)

        print("Insertando clientes en la nube...")
        mapa_clientes = {}  # It will store the relationship to map the IDs.

        # To avoid duplication if there is already users in the database we just skip the inserting.
        if session.exec(select(Cliente)).first():
                return

        # We start inserting the data.
        for c in datos_origen["clientes"]:

            nuevo_cliente = Cliente(
                nombre=c["nombre"],
                email=c["email"],
                saldo_actual=Decimal(str(c["saldo_actual"])),
                telefono=c["telefono"],
                ciudad=c["ciudad"]
            )

            session.add(nuevo_cliente)
            print(f"Cliente '{nuevo_cliente.nombre}' insertado con ID {nuevo_cliente.id}.")
            session.flush()  # Force Postgres to generate the automatic user ID.
            mapa_clientes[c["id"]] = nuevo_cliente.id # Map the user id in the database to the one in the json file.

        # Add the user's transactions.
        print("Vinculando e insertando historial de transacciones...")
        for t in datos_origen["transacciones"]:
            # Use out ID map to ensure the transaction is asigned to the correct client.
            new_id_client = mapa_clientes.get(t["cliente_id"])
            
            new_transaccion = Transaccion(
                tipo=t["tipo"],
                monto=Decimal(str(t["monto"])),
                detalles=t["detalles"],
                categoria=obtener_categoria(t["detalles"]), # Obtain the category of the transaction.
                cliente_id = new_id_client
            )
            session.add(new_transaccion)
            print(f"Transacción '{new_transaccion.detalles}' introducida con id '{new_transaccion.id}'")

        # Add the user's contacts.
        print("Vinculando los contactos de los clientes.")
        for c in datos_origen["contactos"]:
            # Check if the contact already exists.
            contact_existence = session.exec(
                select(Contacto).where((Contacto.tel == c["tel"]) & (Contacto.cliente_id == mapa_clientes.get(c["cliente_id"])))
            ).first()

            if contact_existence:
                continue

            new_id_client = mapa_clientes.get(c["cliente_id"])
            nuevo_contacto = Contacto(
                nombre = c["nombre"],
                tel = c["tel"],
                cliente_id = new_id_client
            )

            session.add(nuevo_contacto)
            print(f"Se ha añadido el contacto '{nuevo_contacto.tel}' con id '{nuevo_contacto.id}'")

        # Confirmation that everyhing works properly.
        session.commit()
        print("El entorno bancario simulado está operativo.")

def populate_faq():
    # Initialize the embedder.
    embedder = OpenAIEmbeddings(model="text-embedding-3-small") 

    # Open the file with the FAQs.
    with open("data/datos_banco.json", "r", encoding="utf-8") as f:
        datos_origen = json.load(f)

    with Session(engine) as session:
        print("Vinculando las preguntas y respuestas más frecuentes.")

        for f in datos_origen["FAQ"]:
            # Avoid repetition of questions.
            faq_existence = session.exec(
                select(FAQ).where(FAQ.pregunta == f["pregunta"])
            ).first()

            if faq_existence:
                continue

            # Put together the final text, with question and answer.
            texto_completo = f"Pregunta: {f["pregunta"]} | Respuesta: {f["respuesta"]}"
            # Calculate the embedding related to that text.
            vector_calculado = embedder.embed_query(texto_completo)

            # Make the final FAQ object and add it to the database.
            new_FAQ = FAQ(
                pregunta = f["pregunta"],
                respuesta = f["respuesta"],
                embedding = vector_calculado
            )
            session.add(new_FAQ)
            print(f"Pregunta con id '{new_FAQ.id}' se ha añadido con éxito.")
        
        session.commit()
        print("Se han introducido todoas las preguntas y respuestas.")

if __name__ == "__main__":
    create_db_and_tables()
    populate_banking_system()
    populate_faq()

    