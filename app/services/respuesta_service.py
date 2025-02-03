from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..schemas.sch_respuesta import Respuesta
from ..schemas.sch_pregunta import Pregunta
from ..schemas.sch_respuesta_usuario import RespuestaDeUsuario
from ..db.database import get_db_session
from ..models.mdl_respuesta import RespuestaCreate, RespuestaUpdate


# Listar respuestas por pregunta_id
def list_respuestas_by_pregunta(pregunta_id: int, current_user):
    if not current_user:
        raise HTTPException(status_code=401, detail="No está autorizado.")

    db = next(get_db_session())
    try:
        # Verificar que la pregunta existe
        pregunta = db.query(Pregunta).filter(Pregunta.id == pregunta_id).first()
        if not pregunta:
            raise HTTPException(
                status_code=404, detail="La pregunta especificada no existe."
            )


        respuestas = (
            db.query(Respuesta)
            .filter(Respuesta.pregunta_id == pregunta_id)
            .all()
        )
        total_respuestas = (
            db.query(Respuesta).filter(Respuesta.pregunta_id == pregunta_id).count()
        )

        return {
            "data": [
                {"id": r.id, "respuesta": r.respuesta, "vocacion": r.vocacion}
                for r in respuestas
            ]
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

# Buscar respuesta por ID
def search_respuesta_by_id(respuesta_id: int, current_user):
    if not current_user:
        raise HTTPException(status_code=401, detail="No está autorizado.")

    db = next(get_db_session())
    try:
        respuesta = db.query(Respuesta).filter(Respuesta.id == respuesta_id).first()
        if not respuesta:
            raise HTTPException(
                status_code=404, detail="La respuesta especificada no existe."
            )

        return {
            "data": {
                "id": respuesta.id,
                "pregunta_id": respuesta.pregunta_id,
                "respuesta": respuesta.respuesta,
            }
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

# Crear respuesta
def create_respuesta_service(respuesta: RespuestaCreate, current_user):
    if not current_user or current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para crear una respuesta.",
        )

    db = next(get_db_session())
    try:
        # Verificar que la pregunta existe
        pregunta = (
            db.query(Pregunta).filter(Pregunta.id == respuesta.pregunta_id).first()
        )
        if not pregunta:
            raise HTTPException(
                status_code=404, detail="La pregunta especificada no existe."
            )

        # Crear respuesta
        nueva_respuesta = Respuesta(
            pregunta_id=respuesta.pregunta_id,
            respuesta=respuesta.respuesta,
            vocacion=respuesta.vocacion,
        )
        db.add(nueva_respuesta)
        db.commit()

        return {
            "message": "Respuesta creada exitosamente.",
            "data": {"id": nueva_respuesta.id},
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

# Editar respuesta
def update_respuesta_service(respuesta: RespuestaUpdate,respuesta_id, current_user):
    if not current_user or current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para editar una respuesta.",
        )

    db = next(get_db_session())
    try:
        # Verificar que la respuesta existe
        respuesta_db = (
            db.query(Respuesta).filter(Respuesta.id == respuesta_id).first()
        )
        if not respuesta_db:
            raise HTTPException(
                status_code=404, detail="La respuesta especificada no existe."
            )

        # Actualizar campos
        respuesta_db.respuesta = respuesta.respuesta
        respuesta_db.vocacion = respuesta.vocacion
        db.commit()

        return {"message": "Respuesta actualizada exitosamente."}
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

# Eliminar respuesta
def delete_respuesta_service(respuesta_id: int, current_user):
    if not current_user or current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para eliminar una respuesta.",
        )

    db = next(get_db_session())
    try:
        # Verificar que la respuesta existe
        respuesta = db.query(Respuesta).filter(Respuesta.id == respuesta_id).first()
        if not respuesta:
            raise HTTPException(
                status_code=404, detail="La respuesta especificada no existe."
            )

        # Verificar si tiene asociaciones con respuestas_de_usuario
        if (
            respuesta.respuestas_de_usuario
        ):  # Asumiendo un backref para verificar asociaciones
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar la respuesta porque está asociada a usuarios.",
            )

        db.delete(respuesta)
        db.commit()

        return {"message": "Respuesta eliminada exitosamente."}
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
