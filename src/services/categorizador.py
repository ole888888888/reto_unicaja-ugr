from enum import Enum
from langchain.agents import create_agent
from pydantic import BaseModel, Field
import json

with open("data/datos_banco.json", mode="r", encoding="utf-8") as f:
    MAPA_CATEGORIAS = json.load(f)

# Creamos todos los tipos de categoría, para no darle libertad completa a la ia.
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

# Tenemos que crear un BaseModel de pydantic para poder darle estructura a la salida del agente.
class ClasificacionTransaccion (BaseModel):
    categoria: categoria_enum = Field(description="Es la categoría de la transacción, que se debe rellenar.")

def obtener_categoria_agente(concepto:str) -> str:
    concepto = concepto.lower()

    instructions = (
        "Te ocupas de asignarle una categoría de transacción partiendo del concepto de la transacción,"
        "debes seleccionarlo de las opciones descritas en tu formato de respuesta,"
        "Si no encuentras ninguna alternativa que te cuadre no dudes en poner una transaccion en otro."
    )

    agent = create_agent(
        model = "gpt-4o-mini",
        response_format = ClasificacionTransaccion,
        system_prompt=instructions,
        )

    salida = agent.invoke({
    "messages": [{"role": "user", "content": f"Extrae la categoría de la siguiente transacción {concepto}"}]
    })

    return salida["structured_response"].categoria.value

def obtener_categoria(concepto: str) -> str:
    concepto = concepto.lower()

    for palabra_clave,cat in MAPA_CATEGORIAS.items():
        if palabra_clave in concepto:
            return cat

    return obtener_categoria_agente(concepto)

    
    