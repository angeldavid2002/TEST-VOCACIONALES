from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..schemas.sch_vocacion_usuario import VocacionDeUsuarioPorTest
from ..schemas.sch_respuesta_usuario import RespuestaDeUsuario
from ..schemas.sch_test import Test
from ..schemas.sch_pregunta import Pregunta
from ..schemas.sch_respuesta import Respuesta
from ..schemas.sch_usuario import Usuario
from ..db.database import get_db_session

def create_or_update_vocacion_usuario_service(id_test: int, current_user: dict):
    db = next(get_db_session())
    try:
        # Verificar si el test existe
        test = db.query(Test).filter(Test.id == id_test).first()
        if not test:
            raise HTTPException(status_code=404, detail="El test no existe.")

        # Verificar si ya existe una vocación registrada para este usuario y test
        vocacion_usuario = (
            db.query(VocacionDeUsuarioPorTest)
            .filter(
                VocacionDeUsuarioPorTest.id_usuario == current_user["user_id"],
                VocacionDeUsuarioPorTest.id_test == id_test,
            )
            .first()
        )

        # Obtener todas las respuestas de usuario asociadas al test
        respuestas_usuario = (
            db.query(RespuestaDeUsuario)
            .filter(
                RespuestaDeUsuario.test_id == id_test,
                RespuestaDeUsuario.usuario_id == current_user["user_id"],
            )
            .all()
        )

        # Verificar si se han respondido todas las preguntas del test
        preguntas_del_test = db.query(Pregunta).filter(Pregunta.test_id == id_test).count()
        if len(respuestas_usuario) < preguntas_del_test:
            raise HTTPException(
                status_code=400,
                detail="No se han respondido todas las preguntas del test.",
            )

        # Calcular la moda de las vocaciones basadas en las respuestas
        vocaciones = [
            db.query(Respuesta.vocacion)
            .filter(Respuesta.id == respuesta.respuesta_id)
            .scalar()
            for respuesta in respuestas_usuario
        ]
        moda_vocacion = max(set(vocaciones), key=vocaciones.count)

        if vocacion_usuario:
            # Actualizar vocación existente
            vocacion_usuario.moda_vocacion = moda_vocacion
            db.commit()
            db.refresh(vocacion_usuario)
            return {
                "message": "Vocación actualizada exitosamente.",
                "data": {"id": vocacion_usuario.id, "moda_vocacion": moda_vocacion},
            }
        else:
            # Crear nueva vocación
            nueva_vocacion = VocacionDeUsuarioPorTest(
                id_usuario=current_user["user_id"],
                id_test=id_test,
                moda_vocacion=moda_vocacion,
            )
            db.add(nueva_vocacion)
            db.commit()
            db.refresh(nueva_vocacion)
            return {
                "message": "Vocación creada exitosamente.",
                "data": {"id": nueva_vocacion.id, "moda_vocacion": moda_vocacion},
            }
    except HTTPException as http_ex:
        db.rollback()
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()
