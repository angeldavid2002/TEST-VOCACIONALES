from datetime import date
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..db.database import get_db_session
from ..models.mdl_user import UsuarioCreate
from ..schemas.sch_usuario import Usuario,Ciudad,Institucion
from .auth_service import *


def register_user(user: UsuarioCreate):
    db = next(get_db_session())
    try:
        # Validar si el email ya existe
        if db.query(Usuario).filter(Usuario.email == user.email).first():
            raise HTTPException(status_code=400, detail="El email ya está registrado.")

        # Validar si la ciudad existe
        if user.id_ciudad is not None:
            ciudad = db.query(Ciudad).filter(Ciudad.id == user.id_ciudad).first()
            if not ciudad:
                raise HTTPException(
                    status_code=400,
                    detail=f"La ciudad con id {user.id_ciudad} no existe.",
                )

        # Validar si la institución existe
        if user.id_institucion is not None:
            institucion = db.query(Institucion).filter(Institucion.id == user.id_institucion).first()
            if not institucion:
                raise HTTPException(
                    status_code=400,
                    detail=f"La institución con id {user.id_institucion} no existe.",
                )

        # Hashear la contraseña
        hashed_password = get_password_hash(user.password)

        # Crear usuario
        nuevo_usuario = Usuario(
            email=user.email,
            nombre=user.nombre,
            contrasena=hashed_password,
            tipo_usuario="comun",
            id_ciudad=user.id_ciudad,
            id_institucion=user.id_institucion,
            fecha_registro=user.fecha_registro,
        )

        # Guardar en la base de datos
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return {"message": "Usuario registrado exitosamente"}
    except HTTPException as http_ex:
        # Propagar las excepciones HTTP específicas sin hacer un rollback
        raise http_ex
    except Exception as ex:
        # Aquí atrapamos cualquier otra excepción imprevista
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))


def login_user(email: str, password: str):
    db = next(get_db_session())
    try:
        # Buscar usuario por email
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if not usuario:
            raise HTTPException(status_code=401, detail="El usuario no existe en la base de datos (Revise su correo)")

        # Verificar contraseña
        if not verify_password(password, usuario.contrasena):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        # Generar token JWT
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "user_id": usuario.id,
                "email": usuario.email,
                "tipo_usuario": usuario.tipo_usuario,
            },
            expires_delta=access_token_expires,
        )

        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as http_ex:
        # Propagar las excepciones HTTP específicas
        raise http_ex
    except Exception as ex:
        # Propagar las excepciones HTTP no manejadas
        raise HTTPException(status_code=500, detail=str(ex))
