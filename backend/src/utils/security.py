# Functions for authentication further down the line.
from passlib.context import CryptContext

# We are going to use passlib to hash the passwords in our database,
# This way we don't store them as plain text.

pwd_context = CryptContext(
    schemes = ["bcrypt"],
    deprecated = "auto",
)

def hash_password (password: str) -> str:
    return pwd_context.hash(password)

def verify_password (plain:str, hash: str) -> bool:
    return pwd_context.verify(plain,hash)