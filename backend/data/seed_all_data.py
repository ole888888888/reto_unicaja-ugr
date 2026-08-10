# seed_all_data.py
import json
import os
from decimal import Decimal

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from sqlmodel import Session, SQLModel, create_engine, select

from src.models import FAQ, Cliente, Contacto, Transaccion
from src.services.categorizador import obtener_categoria

# 1. Conexión a la base de datos
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine) # Se ocupa de inicializar la base de datos y crear las tablas si no existen

def drop_all_tables():
    SQLModel.metadata.drop_all(engine) # Se ocupa de borrar todas las tablas, esto es para reiniciar las tablas.

def populate_banking_system():   
    with Session(engine) as session:
        # Validación de seguridad: Evitar duplicados si corres el script por error otra vez
        print("Leyendo archivo datos_banco.json...")
        with open("data/datos_banco.json", "r", encoding="utf-8") as f:
            datos_origen = json.load(f)

        print("Insertando clientes en la nube...")
        mapa_clientes = {}  # Guardará la relación temporal para mapear IDs
        
        if session.exec(select(Cliente)).first():
                return

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
            session.flush()  # Forzamos a Postgres a generar el ID automático de este cliente
            mapa_clientes[c["id"]] = nuevo_cliente.id

        print("Vinculando e insertando historial de transacciones...")
        for t in datos_origen["transacciones"]:
            # Usamos nuestro mapa de IDs para asegurar que se asigne al cliente correcto en Postgres
            nuevo_id_cliente = mapa_clientes.get(t["cliente_id"])
            
            nueva_transaccion = Transaccion(
                tipo=t["tipo"],
                monto=Decimal(str(t["monto"])),
                detalles=t["detalles"],
                categoria=obtener_categoria(t["detalles"]),
                cliente_id = nuevo_id_cliente
            )
            session.add(nueva_transaccion)
            print(f"Transacción '{nueva_transaccion.detalles}' introducida con id '{nueva_transaccion.id}'")

        print("Vinculando los contactos de los clientes.")
        for c in datos_origen["contactos"]:
            contacto_existence = session.exec(
                select(Contacto).where((Contacto.tel == c["tel"]) & (Contacto.cliente_id == mapa_clientes.get(c["cliente_id"])))
            ).first()

            if contacto_existence:
                continue

            nuevo_id_cliente = mapa_clientes.get(c["cliente_id"])
            nuevo_contacto = Contacto(
                nombre = c["nombre"],
                tel = c["tel"],
                cliente_id = nuevo_id_cliente
            )

            session.add(nuevo_contacto)
            print(f"Se ha añadido el contacto '{nuevo_contacto.tel}' con id '{nuevo_contacto.id}'")

        # Confirmación definitiva en producción
        session.commit()
        print("El entorno bancario simulado está operativo.")

def populate_faq():
        
    embedder = OpenAIEmbeddings(model="text-embedding-3-small") 

    with open("data/datos_banco.json", "r", encoding="utf-8") as f:
        datos_origen = json.load(f)

    with Session(engine) as session:
        print("Vinculando las preguntas y respuestas más frecuentes.")

        for f in datos_origen["FAQ"]:
            faq_existence = session.exec(
                select(FAQ).where(FAQ.pregunta == f["pregunta"])
            ).first()

            if faq_existence:
                continue

            texto_completo = f"Pregunta: {f["pregunta"]} | Respuesta: {f["respuesta"]}"
            vector_calculado = embedder.embed_query(texto_completo)

            nueva_FAQ = FAQ(
                pregunta = f["pregunta"],
                respuesta = f["respuesta"],
                embedding = vector_calculado
            )
            session.add(nueva_FAQ)
            print(f"Pregunta con id '{nueva_FAQ.id}' se ha añadido con éxito.")
        
        session.commit()
        print("Se han introducido todoas las preguntas y respuestas.")

if __name__ == "__main__":
    drop_all_tables()
    create_db_and_tables()
    populate_banking_system()
    populate_faq()

    