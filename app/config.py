# config.py
from dotenv import load_dotenv
import os

# Cargar variables desde .env
load_dotenv('.env')

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
    
    #configuración para el envío de correos
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    FRONTEND_URL = os.getenv("FRONTEND_URL")

    
config = Config()
