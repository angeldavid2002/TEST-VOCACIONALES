from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..schemas.sch_pregunta import Pregunta
from ..schemas.sch_respuesta import Respuesta
from ..schemas.sch_test import Test
from ..db.database import get_db_session
from ..models.mdl_pregunta import PreguntaCreate, PreguntaUpdate


# Listar preguntas por Test_ID
def list_preguntas_by_test(test_id: int, page: int, current_user):
    if not current_user:
        raise HTTPException(status_code=401, detail="No está autorizado.")

    db = next(get_db_session())
    try:
        # Verificar que el test existe
        test = db.query(Test).filter(Test.id == test_id).first()
        if not test:
            raise HTTPException(
                status_code=404, detail="El test especificado no existe."
            )

        # Paginación
        page_size = 5
        offset = (page - 1) * page_size

        preguntas = (
            db.query(Pregunta)
            .filter(Pregunta.test_id == test_id)
            .offset(offset)
            .limit(page_size)
            .all()
        )
        total_preguntas = db.query(Pregunta).filter(Pregunta.test_id == test_id).count()

        return {
            "data": [{"id": p.id, "enunciado": p.enunciado} for p in preguntas],
            "pagination": {
                "total": total_preguntas,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_preguntas + page_size - 1) // page_size,
            },
        }
    except HTTPException as http_ex:
        # Propagar excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Manejar excepciones no controladas
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()


# Buscar pregunta por ID
def search_pregunta_by_id(pregunta_id: int, current_user):
    if not current_user:
        raise HTTPException(status_code=401, detail="No está autorizado.")

    db = next(get_db_session())
    try:
        pregunta = db.query(Pregunta).filter(Pregunta.id == pregunta_id).first()
        if not pregunta:
            raise HTTPException(
                status_code=404, detail="La pregunta especificada no existe."
            )

        return {
            "data": {
                "id": pregunta.id,
                "test_id": pregunta.test_id,
                "enunciado": pregunta.enunciado,
            }
        }
    except HTTPException as http_ex:
        # Propagar excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Manejar excepciones no controladas
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()


# Crear pregunta
def create_pregunta_service(pregunta: PreguntaCreate, current_user):
    if not current_user or current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para crear una pregunta.",
        )

    db = next(get_db_session())
    try:
        # Verificar que el test existe
        test = db.query(Test).filter(Test.id == pregunta.test_id).first()
        if not test:
            raise HTTPException(
                status_code=404, detail="El test especificado no existe."
            )

        # Crear pregunta
        nueva_pregunta = Pregunta(
            test_id=pregunta.test_id, enunciado=pregunta.enunciado
        )
        db.add(nueva_pregunta)
        db.commit()

        return {
            "message": "Pregunta creada exitosamente.",
            "data": {"id": nueva_pregunta.id},
        }
    except HTTPException as http_ex:
        # Propagar excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Manejar excepciones no controladas
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()


# Editar pregunta
def update_pregunta_service(pregunta_r: PreguntaUpdate, current_user):
    if not current_user or current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para editar una pregunta.",
        )

    db = next(get_db_session())
    try:
        # Verificar que la pregunta existe
        pregunta = (
            db.query(Pregunta).filter(Pregunta.id == pregunta_r.pregunta_id).first()
        )
        if not pregunta:
            raise HTTPException(
                status_code=404, detail="La pregunta especificada no existe."
            )

        # Actualizar enunciado
        pregunta.enunciado = pregunta_r.enunciado
        db.commit()

        return {"message": "Pregunta actualizada exitosamente."}
    except HTTPException as http_ex:
        # Propagar excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Manejar excepciones no controladas
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()


# Eliminar pregunta
def delete_pregunta_service(pregunta_id: int, current_user):
    if not current_user or current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para eliminar una pregunta.",
        )

    db = next(get_db_session())
    try:
        # Verificar que la pregunta existe
        pregunta = db.query(Pregunta).filter(Pregunta.id == pregunta_id).first()
        if not pregunta:
            raise HTTPException(
                status_code=404, detail="La pregunta especificada no existe."
            )

        # Verificar si tiene respuestas asociadas
        if pregunta.respuestas:  # Aquí usas el backref para acceder a las respuestas
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar la pregunta porque tiene respuestas asociadas.",
            )

        db.delete(pregunta)
        db.commit()

        return {"message": "Pregunta eliminada exitosamente."}
    except HTTPException as http_ex:
        # Propagar excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Manejar excepciones no controladas
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()
