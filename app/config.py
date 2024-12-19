# config.py
from dotenv import load_dotenv
import os

# Cargar variables desde .env
load_dotenv()

class Config:
    # Configuración de las variables
    # jwt
    SECRET_KEY=os.getenv("SECRET_KEY")
    ALGORITHM=os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    #hashing
    HASHING_SCHEMES=os.getenv("HASHING_SCHEMES")
    HASHING_DEPRECATED=os.getenv("HASHING_DEPRECATED")
    # sqlite
    DATABASE_URL=os.getenv("DATABASE_URL")
    #admin credentials
    ADMIN_EMAIL=os.getenv("ADMIN_EMAIL")
    ADMIN_NAME=os.getenv("ADMIN_NAME")
    ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD")
    ADMIN_USER_TYPE=os.getenv("ADMIN_USER_TYPE")
    
config = Config()
# print("JWT")
# print(f"SECRET_KEY: {config.SECRET_KEY}")
# print(f"ALGORITHM: {config.ALGORITHM}")
# print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {config.ACCESS_TOKEN_EXPIRE_MINUTES}")
# print("HASHING")
# print(f"HASHING_SCHEMES: {config.HASHING_SCHEMES}")
# print(f"HASHING_DEPRECATED: {config.HASHING_DEPRECATED}")
# print("SQLITE")
# print(f"DATABASE_URL: {config.DATABASE_URL}")
