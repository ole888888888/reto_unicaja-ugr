import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

# Function that returns the engine to work with.
# You just have to initialize the engine once at the start of execution.
def get_engine():
    connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    return create_engine(DATABASE_URL, connect_args=connect_args)

# Function that initializes the database and tables.
def init_db(drop_tables: bool = False):
    engine = get_engine()
    if drop_tables:
        SQLModel.metadata.drop_all(engine)    
    SQLModel.metadata.create_all(engine)

# Create generator, which allows to create sessions which are used and discarted.
# This structure enables us to use next(get_session()) to get a session that closes automatically after all the changes are made.
def get_session():
    engine = get_engine()
    with Session(engine) as session:
        yield session

# We have to make sure that the database is initialized just once.
# The session is what changes between query and query.