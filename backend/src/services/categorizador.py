import json
from enum import Enum

from langchain.agents import create_agent
from pydantic import BaseModel, Field

with open("data/datos_banco.json", mode="r", encoding="utf-8") as f:
    MAPA_CATEGORIAS = json.load(f)

# This is a list of all the categories as to not give the ai the liberty to choose its own categories.
class categoria_enum(str, Enum):
    SUPERMERCADO = "Supermercado"
    HOSTELERIA = "Hostelería"
    TRANSPORTE = "Transporte"
    SUSCRIPCIONES = "Suscripciones"
    SALUD_DEPORTE = "Salud/Deporte"
    OCIO = "Ocio"
    HOGAR_SERVICIOS = "Hogar/Servicios"
    TECNOLOGIA = "Tecnología"
    CULTURA = "Cultura"
    EDUCACION = "Educación"
    ROPA_CALZADO = "Ropa/Calzado"
    GASTOS_FINANCIEROS = "Gastos Financieros"
    VIAJES = "Viajes"
    MASCOTAS = "Mascotas"
    IMPUESTOS = "Impuestos/Administración"
    DONACIONES = "Donaciones/ONG"
    BELLEZA = "Belleza/Estética"
    MANTENIMIENTO = "Mantenimiento/Reparaciones"
    ELECTRONICA = "Electrónica/Informática"
    BANCARIO = "Bancario"
    TRABAJO = "Trabajo"
    OTROS = "Otros"

# We create a pydantic BaseModel to structure the output of the ai properly.
class ClasificacionTransaccion (BaseModel):
    categoria: categoria_enum = Field(description="Es la categoría de la transacción, que se debe rellenar.")

# Function that creates the agent which manages the categories.
def obtener_categoria_agente(concepto:str) -> str:
    concepto = concepto.lower()

    instructions = (
        "Te ocupas de asignarle una categoría de transacción partiendo del concepto de la transacción,"
        "debes seleccionarlo de las opciones descritas en tu formato de respuesta,"
        "Si no encuentras ninguna alternativa que te cuadre no dudes en poner una transaccion en otro."
    )

    agent = create_agent(
        model = "gpt-4o-mini",
        response_format = ClasificacionTransaccion, # Make sure it follows the pydantic BaseModel.
        system_prompt=instructions,
        )

    salida = agent.invoke({
    "messages": [{"role": "user", "content": f"Extrae la categoría de la siguiente transacción {concepto}"}]
    })

    return salida["structured_response"].categoria.value

# This function allows for token optimization by getting the categories from a list with common transaction names.
# If it doesn't find anything it does use the above function.
def obtener_categoria(concepto: str) -> str:
    concepto = concepto.lower()

    for palabra_clave,cat in MAPA_CATEGORIAS.items():
        if palabra_clave in concepto:
            return cat

    return obtener_categoria_agente(concepto)

    
    