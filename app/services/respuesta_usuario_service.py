from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..services.vocacion_usuario_service import create_or_update_vocacion_usuario_service
from ..schemas.sch_respuesta_usuario import RespuestaDeUsuario
from ..schemas.sch_test import Test
from ..schemas.sch_pregunta import Pregunta
from ..schemas.sch_respuesta import Respuesta
from ..schemas.sch_usuario import Usuario
from ..db.database import get_db_session
from ..models.mdl_respuesta_usuario import (
    RespuestaDeUsuarioCreate,
    RespuestaDeUsuarioUpdate,
)


# 1. Listar respuestas de usuario (usuarios comunes)
def list_respuestas_usuario(test_id: int, current_user):
    if not current_user:
        raise HTTPException(status_code=401, detail="No está autorizado.")

    db = next(get_db_session())
    try:
        respuestas = (
            db.query(RespuestaDeUsuario)
            .filter(
                RespuestaDeUsuario.test_id == test_id,
                RespuestaDeUsuario.usuario_id == current_user["user_id"],
            )
            .all()
        )

        if not respuestas:
            raise HTTPException(
                status_code=404, detail="No hay respuestas asociadas para este test."
            )

        return [
            {
                "id": r.id,
                "pregunta_id": r.pregunta_id,
                "enunciado_pregunta": r.pregunta.enunciado,
                "respuesta_id": r.respuesta_id,
                "respuesta_texto": r.respuesta.respuesta,
            }
            for r in respuestas
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


# 2. Listar respuestas de usuario (administradores)
""" def list_respuestas_usuario_admin(test_id: int, usuario_id: int, current_user):
    if not current_user or current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403, detail="No tiene privilegios para realizar esta acción."
        )

    db = next(get_db_session())
    try:
        respuestas = (
            db.query(RespuestaDeUsuario)
            .filter(
                RespuestaDeUsuario.test_id == test_id,
                RespuestaDeUsuario.usuario_id == usuario_id,
            )
            .all()
        )

        if not respuestas:
            raise HTTPException(
                status_code=404,
                detail="No hay respuestas asociadas para este test y usuario.",
            )

        return [{"id": r.id, "respuesta_id": r.respuesta_id} for r in respuestas]
    except HTTPException as http_ex:
        # Propagar las excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Propagar las excepciones HTTP no manejadas
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close() """


# 3. Crear respuesta de usuario
def create_respuesta_usuario_service(respuesta_data: RespuestaDeUsuarioCreate, current_user):
    db = next(get_db_session())
    try:
        # Validar entidades relacionadas
        test = db.query(Test).filter(Test.id == respuesta_data.test_id).first()
        pregunta = db.query(Pregunta).filter(Pregunta.id == respuesta_data.pregunta_id).first()
        respuesta = db.query(Respuesta).filter(Respuesta.id == respuesta_data.respuesta_id).first()

        if not (test and pregunta and respuesta):
            raise HTTPException(
                status_code=404, detail="El test, la pregunta o la respuesta no existen."
            )

        # Verificar relaciones entre test, pregunta y respuesta
        if pregunta.test_id != test.id or respuesta.pregunta_id != pregunta.id:
            raise HTTPException(
                status_code=400,
                detail="Los IDs proporcionados no están relacionados entre sí."
            )

        # Crear la nueva respuesta del usuario
        nueva_respuesta = RespuestaDeUsuario(
            test_id=respuesta_data.test_id,
            pregunta_id=respuesta_data.pregunta_id,
            respuesta_id=respuesta_data.respuesta_id,
            usuario_id=current_user["user_id"],
        )

        # Guardar en la base de datos
        db.add(nueva_respuesta)
        db.commit()
        db.refresh(nueva_respuesta)

        # Verificar si el test está completo
        total_questions = db.query(Pregunta).filter(Pregunta.test_id == respuesta_data.test_id).count()
        respuestas = db.query(RespuestaDeUsuario).filter(
            RespuestaDeUsuario.test_id == respuesta_data.test_id,
            RespuestaDeUsuario.usuario_id == current_user["user_id"]
        ).all()
        if len(respuestas) == total_questions:
            # Si el test está completo, calcular o actualizar la vocación automáticamente.
            vocacion_result = create_or_update_vocacion_usuario_service(respuesta_data.test_id, current_user)
            return {
                "message": "Respuesta creada y test completado. " + vocacion_result["message"],
                "data": {"id": nueva_respuesta.id, "vocacion": vocacion_result["data"]}
            }
        else:
            return {"message": "Respuesta creada exitosamente.", "data": {"id": nueva_respuesta.id}}
    except HTTPException as http_ex:
        db.rollback()
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()



# 4. Editar respuesta de usuario
def update_respuesta_usuario_service(respuesta_data: RespuestaDeUsuarioUpdate, test_id, current_user):
    if not current_user:
        raise HTTPException(status_code=401, detail="No está autorizado.")

    db = next(get_db_session())
    try:
        respuesta_usuario = (
            db.query(RespuestaDeUsuario)
            .filter(
                RespuestaDeUsuario.test_id == test_id,
                RespuestaDeUsuario.pregunta_id == respuesta_data.pregunta_id,
                RespuestaDeUsuario.usuario_id == current_user["user_id"],
            )
            .first()
        )

        if not respuesta_usuario:
            raise HTTPException(
                status_code=404, detail="No se encontró la respuesta de usuario."
            )

        # Actualizar respuesta
        respuesta_usuario.respuesta_id = respuesta_data.respuesta_id
        db.commit()

        # Verificar si el test está completo después de la actualización
        total_questions = db.query(Pregunta).filter(Pregunta.test_id == test_id).count()
        respuestas = db.query(RespuestaDeUsuario).filter(
            RespuestaDeUsuario.test_id == test_id,
            RespuestaDeUsuario.usuario_id == current_user["user_id"]
        ).all()
        if len(respuestas) == total_questions:
            vocacion_result = create_or_update_vocacion_usuario_service(test_id, current_user)
            return {
                "message": "Respuesta actualizada y test completado. " + vocacion_result["message"],
                "data": {"vocacion": vocacion_result["data"]}
            }
        else:
            return {"message": "Respuesta actualizada exitosamente."}
    except HTTPException as http_ex:
        db.rollback()
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()


# 5. Eliminar respuestas de usuario (administradores)
def delete_respuestas_usuario_admin_service(test_id: int, current_user):
    if not current_user or current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403, detail="No tiene privilegios para realizar esta acción."
        )

    db = next(get_db_session())
    try:
        respuestas = (
            db.query(RespuestaDeUsuario)
            .filter(RespuestaDeUsuario.test_id == test_id)
            .all()
        )

        if not respuestas:
            raise HTTPException(
                status_code=404, detail="No hay respuestas asociadas para este test."
            )

        for respuesta in respuestas:
            db.delete(respuesta)
        db.commit()

        return {"message": "Respuestas eliminadas exitosamente."}
    except HTTPException as http_ex:
        db.rollback()
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()
