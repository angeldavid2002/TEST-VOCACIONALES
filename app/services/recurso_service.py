from fastapi import HTTPException
from sqlalchemy import func
from ..db.database import get_db_session
from ..schemas.sch_recurso import Recurso
from ..models.mdl_recurso import RecursoCreate, RecursoUpdate


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

def edit_recurso_service(recurso_id: int, recurso_data: RecursoUpdate, current_user):
    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para editar recursos.",
        )

    db = next(get_db_session())
    try:
        recurso = db.query(Recurso).filter(Recurso.id == recurso_id).first()
        if not recurso:
            raise HTTPException(status_code=404, detail="Recurso no encontrado.")

        # Actualizar campos del recurso si están presentes en recurso_data
        recurso.nombre = recurso_data.nombre if recurso_data.nombre is not None else recurso.nombre
        recurso.tipo = recurso_data.tipo if recurso_data.tipo is not None else recurso.tipo
        recurso.autor = recurso_data.autor if recurso_data.autor is not None else recurso.autor
        recurso.plataforma = recurso_data.plataforma if recurso_data.plataforma is not None else recurso.plataforma
        recurso.enlace = recurso_data.enlace if recurso_data.enlace is not None else recurso.enlace

        db.commit()
        db.refresh(recurso)

        return {"message": "Recurso actualizado exitosamente", "id": recurso.id}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()

def delete_recurso_service(recurso_id: int, current_user):
    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para eliminar recursos.",
        )

    db = next(get_db_session())
    try:
        recurso = db.query(Recurso).filter(Recurso.id == recurso_id).first()
        if not recurso:
            raise HTTPException(status_code=404, detail="Recurso no encontrado.")

        db.delete(recurso)
        db.commit()
        return {"message": "Recurso eliminado exitosamente", "id": recurso_id}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()

def list_recursos_service():
    db = next(get_db_session())
    try:
        recursos = db.query(Recurso).all()
        return recursos
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()

def get_total_recursos():
    db = next(get_db_session())
    try:
        # Contar el total de recursos en la base de datos
        total_recursos = db.query(func.count(Recurso.id)).scalar()
        return {"total_recursos": total_recursos}
    except HTTPException as http_ex:
        db.rollback()
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()