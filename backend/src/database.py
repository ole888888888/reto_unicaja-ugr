import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

# Función que nos devuelve un engine con el que trabajar.
# Un engine solo hace falta inicializarlo una vez al principio de la ejecución para evitar problemas.
def get_engine():
    connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    return create_engine(DATABASE_URL, connect_args=connect_args)

# Función que inicializa la base de datos y crea las tablas.
def init_db(drop_tables: bool = False):
    engine = get_engine()
    if drop_tables:
        SQLModel.metadata.drop_all(engine)    
    SQLModel.metadata.create_all(engine)

# Creamos un generador, que crea sesiones las cuales se usan y se descartan.
# Esto nos permite usar next(get_session()) para conseguir una sesión y que se cierre automaticamente una vez hechos todos los cambios.
def get_session():
    engine = get_engine()
    with Session(engine) as session:
        yield session

# Básicamente tenemos que asegurarnos de que solo se inicie una vez la base de datos.
# Y que sea la sesión lo que vaya cambiando cada vez.