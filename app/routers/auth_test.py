from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..config import config
from ..models import mdl_user 
from ..schemas import sch_usuario
from ..services import auth_service
from ..db.database import SessionLocal


router = APIRouter()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=mdl_user.Usuario)
def register(usuario: mdl_user.UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar si el email ya está registrado
    if db.query(sch_usuario.Usuario).filter(sch_usuario.Usuario.email == usuario.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El email ya está registrado.")
    
    # Hashear la contraseña antes de almacenarla
    hashed_password = auth_service.get_password_hash(usuario.contrasena)
    
    new_user = sch_usuario.Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        contrasena=hashed_password,
        tipo_usuario=usuario.tipo_usuario,
        fecha_registro=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/token")
async def login(form_data: mdl_user.UsuarioCreate, db: Session = Depends(get_db)):
    user = db.query(sch_usuario.Usuario).filter(sch_usuario.Usuario.email == form_data.email).first()
    
    if not user or not auth_service.verify_password(form_data.contrasena, user.contrasena):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Credenciales incorrectas.")
    
    access_token_expires = timedelta(minutes = config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}
