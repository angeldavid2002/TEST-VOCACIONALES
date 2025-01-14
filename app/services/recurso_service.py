from fastapi import HTTPException
from ..db.database import get_db_session
from ..schemas.sch_recurso import Recurso
from ..models.mdl_recurso import RecursoCreate


def register_recurso_service(recurso: RecursoCreate, current_user):
    # Verificar si el usuario tiene privilegios de administrador
    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para registrar recursos.",
        )

    db = next(get_db_session())
    try:

        # Crear nuevo recurso
        nuevo_recurso = Recurso(
            nombre=recurso.nombre,
            tipo=recurso.tipo,
            autor=recurso.autor,
            plataforma=recurso.plataforma,
            enlace=recurso.enlace,
        )

        # Guardar en la base de datos
        db.add(nuevo_recurso)
        db.commit()
        db.refresh(nuevo_recurso)

        return {"message": "Recurso registrado exitosamente", "id": nuevo_recurso.id}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()
