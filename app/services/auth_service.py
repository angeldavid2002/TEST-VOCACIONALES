from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from ..config import config

print("JWT")
print(f"SECRET_KEY: {config.SECRET_KEY}")
print(f"ALGORITHM: {config.ALGORITHM}")
print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {config.ACCESS_TOKEN_EXPIRE_MINUTES}")
print("HASHING")
print(f"HASHING_SCHEMES: {config.HASHING_SCHEMES}")
print(f"HASHING_DEPRECATED: {config.HASHING_DEPRECATED}")
print("SQLITE")
print(f"DATABASE_URL: {config.DATABASE_URL}")

# Configuración del hashing
pwd_context = CryptContext(schemes=[config.HASHING_SCHEMES], deprecated=config.HASHING_DEPRECATED)

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    
    return encoded_jwt
