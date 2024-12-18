from datetime import date
from fastapi import HTTPException
from ..db.database import get_db_session
from ..models.mdl_user import UsuarioCreate
from ..schemas.sch_usuario import Usuario


def register_user(user: UsuarioCreate):
    db = next(get_db_session())
    try:
        # Validar si el email ya existe
        if db.query(Usuario).filter(Usuario.email == user.email).first():
            raise HTTPException(status_code=400, detail="El email ya está registrado.")

        # Crear usuario
        nuevo_usuario = Usuario(
            email=user.email,
            nombre=user.nombre,
            contrasena=user.contrasena,
            tipo_usuario="comun",
            id_ciudad=user.id_ciudad,
            id_institucion=user.id_institucion,
            fecha_registro=date.today(),
        )

        # Guardar en la base de datos
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return {"message": "Usuario registrado exitosamente"}
    except Exception as ex:
        db.rollback()  # Revertir cambios si ocurre un error
        raise HTTPException(status_code=500, detail=str(ex))
