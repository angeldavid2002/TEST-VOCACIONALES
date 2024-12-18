#2 rutas
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr, ValidationError
from datetime import datetime
import sqlite3
from ..config import config

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Modelo para el registro de usuarios
class RegisterUser(BaseModel):
    nombre: str
    email: EmailStr
    contrasena: str
    id_ciudad: int
    id_institucion: int


# Función para conexión a la base de datos
def get_db():
    conn = sqlite3.connect("database.db")
    return conn


# Función para codificar tokens
def encode_token(payload: dict) -> str:
    token = jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return token


# Función para decodificar tokens
def decode_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


# Ruta para registro de usuarios
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: RegisterUser):
    conn = get_db()
    cursor = conn.cursor()

    # Validar si el email ya existe
    cursor.execute("SELECT id FROM usuarios WHERE email = ?", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está registrado")

    # Validar si la ciudad existe
    cursor.execute("SELECT id FROM ciudades WHERE id = ?", (user.id_ciudad,))
    if not cursor.fetchone():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La ciudad no existe")

    # Validar si la institución existe
    cursor.execute("SELECT id FROM instituciones WHERE id = ?", (user.id_institucion,))
    if not cursor.fetchone():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La institución no existe")

    # Insertar el usuario en la base de datos
    cursor.execute(
        """
        INSERT INTO usuarios (nombre, email, contrasena, tipo_usuario, id_ciudad, id_institucion, fecha_registro) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user.nombre, user.email, user.contrasena, "comun", user.id_ciudad, user.id_institucion, datetime.now()),
    )
    conn.commit()
    conn.close()

    return {"message": "Usuario registrado exitosamente"}


# Ruta para inicio de sesión
@router.post("/token", status_code=status.HTTP_200_OK)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db()
    cursor = conn.cursor()

    # Verificar si el email existe
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (form_data.username,))
    user = cursor.fetchone()

    if not user or user[3] != form_data.password:  # user[3] es la columna contrasena
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario o contraseña incorrectos"
        )

    # Generar token
    payload = {"id": user[0], "email": user[2], "tipo_usuario": user[4]}  # user[0]: id, user[2]: email, user[4]: tipo_usuario
    token = encode_token(payload)
    return {"access_token": token, "token_type": "bearer"}


# Ruta protegida como ejemplo
@router.get("/users/profile", status_code=status.HTTP_200_OK)
def profile(current_user: Annotated[dict, Depends(decode_token)]):
    return {"user": current_user}
