from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from ..config import config

# Esquema de autenticacion
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
# Configuración del hashing
pwd_context = CryptContext(schemes=[config.HASHING_SCHEMES], deprecated=config.HASHING_DEPRECATED)

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    
    return encoded_jwt

def verify_jwt_token(token: str):
    try:
        # Decodificar el token
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        
        # Verificar si el token ha expirado
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="El token ha expirado.")

        # Extraer la información del usuario del token
        user_info = {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "tipo_usuario": payload.get("tipo_usuario"),
        }

        # Si no se encuentra el 'user_id', el token es inválido
        if not user_info["user_id"]:
            raise HTTPException(status_code=401, detail="Token inválido.")

        return user_info
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o mal formado.")