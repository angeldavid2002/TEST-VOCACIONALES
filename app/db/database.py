from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config import config

# Creación del engine y sesión
engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea y retorna una sesión de base de datos, asegurando su cierre.
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()