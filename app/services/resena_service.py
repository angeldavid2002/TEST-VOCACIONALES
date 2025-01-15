from sqlalchemy import func
from fastapi import HTTPException
from datetime import datetime, timezone

from ..models.mdl_resena import ResenaCreate
from ..schemas.sch_resena import Resena
from ..schemas.sch_usuario import Usuario
from ..db.database import get_db_session


# Crear reseña
def create_resena_service(resena_data: ResenaCreate, current_user):
    db = next(get_db_session())
    try:
        # Validar puntuación
        if resena_data.puntuacion < 0 or resena_data.puntuacion > 5:
            raise HTTPException(
                status_code=400, detail="La puntuación debe estar entre 0 y 5."
            )

        # Crear objeto de reseña con la fecha actual
        nueva_resena = Resena(
            id_usuario=current_user["user_id"],
            comentario=resena_data.comentario,
            puntuacion=resena_data.puntuacion,
            fecha_creacion=datetime.now(timezone.utc),  # Fecha actual
        )

        # Guardar en la base de datos
        db.add(nueva_resena)
        db.commit()
        db.refresh(nueva_resena)

        return {
            "message": "Reseña registrada exitosamente",
            "data": {"id": nueva_resena.id},
        }
    except HTTPException as http_ex:
        # Propagar las excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Propagar las excepciones HTTP no manejadas
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()


# Consultar reseñas organizadas de más reciente a más antigua
def get_resenas_paginated_desc_service(page: int, limit: int = 5):
    db = next(get_db_session())
    try:
        # Calcular el offset basado en la página
        skip = (page - 1) * limit
        resenas = (
            db.query(
                Resena.id,
                Resena.comentario,
                Resena.puntuacion,
                Resena.fecha_creacion,
                Usuario.nombre.label("nombre_usuario"),
            )
            .join(Usuario, Resena.id_usuario == Usuario.id)
            .order_by(Resena.fecha_creacion.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "comentario": r.comentario,
                "puntuacion": r.puntuacion,
                "fecha_creacion": r.fecha_creacion,
                "nombre_usuario": r.nombre_usuario,
            }
            for r in resenas
        ]
    except HTTPException as http_ex:
        # Propagar las excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Propagar las excepciones HTTP no manejadas
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()


# Consultar reseñas organizadas de más antigua a más reciente
def get_resenas_paginated_asc_service(page: int, limit: int = 5):
    db = next(get_db_session())
    try:
        # Calcular el offset basado en la página
        skip = (page - 1) * limit
        resenas = (
            db.query(
                Resena.id,
                Resena.comentario,
                Resena.puntuacion,
                Resena.fecha_creacion,
                Usuario.nombre.label("nombre_usuario"),
            )
            .join(Usuario, Resena.id_usuario == Usuario.id)
            .order_by(Resena.fecha_creacion.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "comentario": r.comentario,
                "puntuacion": r.puntuacion,
                "fecha_creacion": r.fecha_creacion,
                "nombre_usuario": r.nombre_usuario,
            }
            for r in resenas
        ]
    except HTTPException as http_ex:
        # Propagar las excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Propagar las excepciones HTTP no manejadas
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()


# Filtrar reseñas por calificación
def get_resenas_by_rating_service(rating: int, page: int, limit: int = 5):
    db = next(get_db_session())
    try:
        # Calcular el offset basado en la página
        skip = (page - 1) * limit
        resenas = (
            db.query(
                Resena.id,
                Resena.comentario,
                Resena.puntuacion,
                Resena.fecha_creacion,
                Usuario.nombre.label("nombre_usuario"),
            )
            .join(Usuario, Resena.id_usuario == Usuario.id)
            .filter(Resena.puntuacion == rating)
            .order_by(Resena.fecha_creacion.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "comentario": r.comentario,
                "puntuacion": r.puntuacion,
                "fecha_creacion": r.fecha_creacion,
                "nombre_usuario": r.nombre_usuario,
            }
            for r in resenas
        ]
    except HTTPException as http_ex:
        # Propagar las excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Propagar las excepciones HTTP no manejadas
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()


# Consultar reseñas por ID de usuario
def get_resenas_by_user_id_service(user_id: int):
    db = next(get_db_session())
    try:
        resenas = (
            db.query(
                Resena.id,
                Resena.comentario,
                Resena.puntuacion,
                Resena.fecha_creacion,
                Usuario.nombre.label("nombre_usuario"),
            )
            .join(Usuario, Resena.id_usuario == Usuario.id)
            .filter(Resena.id_usuario == user_id)
            .order_by(Resena.fecha_creacion.desc())
            .all()
        )
        return [
            {
                "id": r.id,
                "comentario": r.comentario,
                "puntuacion": r.puntuacion,
                "fecha_creacion": r.fecha_creacion,
                "nombre_usuario": r.nombre_usuario,
            }
            for r in resenas
        ]
    except HTTPException as http_ex:
        # Propagar las excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Propagar las excepciones HTTP no manejadas
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()



# Calcular el promedio de puntuaciones
def get_average_rating_service() -> float:
    db = next(get_db_session())
    try:
        avg_rating = db.query(func.avg(Resena.puntuacion)).scalar()
        return avg_rating or 0.0
    except HTTPException as http_ex:
        # Propagar las excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Propagar las excepciones HTTP no manejadas
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()


# edicion de reseñas
def edit_resena_service(resena_id: int, resena_data: ResenaCreate, current_user):
    db = next(get_db_session())
    try:
        # Obtener la reseña por ID
        resena = db.query(Resena).filter(Resena.id == resena_id).first()

        # Verificar si la reseña existe
        if not resena:
            raise HTTPException(status_code=404, detail="Reseña no encontrada.")

        # Verificar si el usuario actual es el propietario de la reseña
        if resena.id_usuario != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="No está autorizado para editar esta reseña.",
            )

        # Validar puntuación
        if resena_data.puntuacion < 1 or resena_data.puntuacion > 5:
            raise HTTPException(
                status_code=400, detail="La puntuación debe estar entre 1 y 5."
            )

        # Actualizar los campos de la reseña
        resena.comentario = resena_data.comentario
        resena.puntuacion = resena_data.puntuacion
        resena.fecha_creacion = datetime.now(timezone.utc)  # Fecha de edición

        # Guardar cambios en la base de datos
        db.commit()
        db.refresh(resena)

        return {
            "message": "Reseña actualizada exitosamente",
            "data": {
                "id": resena.id,
                "comentario": resena.comentario,
                "puntuacion": resena.puntuacion,
                "fecha_creacion": resena.fecha_creacion,
            },
        }
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()


# eliminar reseña
def delete_resena_service(resena_id: int, current_user):
    db = next(get_db_session())
    try:
        # Obtener la reseña por ID
        resena = db.query(Resena).filter(Resena.id == resena_id).first()

        # Verificar si la reseña existe
        if not resena:
            raise HTTPException(status_code=404, detail="Reseña no encontrada.")

        # Verificar si el usuario actual es el propietario de la reseña o un administrador
        if resena.id_usuario != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="No está autorizado para eliminar esta reseña o usted no es su propietario.",
            )

        # Eliminar la reseña
        db.delete(resena)
        db.commit()

        return {
            "message": "Reseña eliminada exitosamente",
            "data": {"id": resena_id},
        }
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()


# Contar el total de reseñas
def count_total_resenas_service() -> int:
    db = next(get_db_session())
    try:
        return db.query(Resena).count()
    except HTTPException as http_ex:
        # Propagar las excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Propagar las excepciones HTTP no manejadas
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()


# Contar las reseñas por puntuación específica
def count_resenas_by_rating_service(rating: int) -> int:
    db = next(get_db_session())
    try:
        if rating < 1 or rating > 5:
            raise HTTPException(
                status_code=400,
                detail="La puntuación debe estar entre 1 y 5.",
            )

        return db.query(Resena).filter(Resena.puntuacion == rating).count()
    except HTTPException as http_ex:
        # Propagar las excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Propagar las excepciones HTTP no manejadas
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()
