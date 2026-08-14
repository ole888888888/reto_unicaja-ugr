# Functions for future authentication use.
import os

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data:dict, expires_delta: int = 900) -> str:
    """
    Generates a signed JSON Web Token (JWT) with an expiration timestamp.

    Args:
        data (dict): The payload claims to be encoded into the token.
        expires_delta (int, optional): The token's lifespan in seconds from the
            current UTC time. Defaults to 900 (15 minutes).

    Returns:
        str: The encoded and signed JWT string.
    """
    from datetime import UTC, datetime, timedelta
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    to_encode.update({"exp":expire}) # We add the expiry date.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM) # Encoding the dict.
    return encoded_jwt

def decode_access_token(token: str) -> dict|None:
    """
    Verifies and decodes a JSON Web Token (JWT).

    Args:
        token (str): The encoded JWT string to be verified and decoded.

    Returns:
        dict | None: The decoded token payload if valid and unexpired; 
            None if the token is invalid, tampered with, or expired.
    """
    try:
        payload = jwt.decode(token,SECRET_KEY,[ALGORITHM])
        return payload
    except (ExpiredSignatureError, InvalidTokenError):
        return None