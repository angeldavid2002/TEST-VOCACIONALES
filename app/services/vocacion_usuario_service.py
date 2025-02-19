from typing import Counter
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
        total_preguntas = db.query(Pregunta).filter(Pregunta.test_id == id_test).count()
        if len(respuestas_usuario) < total_preguntas:
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
        counter = Counter(vocaciones)
        if not counter:
            raise HTTPException(status_code=400, detail="No se pudieron calcular las vocaciones.")
        most_common = counter.most_common()
        moda_vocacion = most_common[0][0]
        # Si no existe un segundo valor distinto, se asigna la misma moda
        moda_vocacion2 = most_common[1][0] if len(most_common) > 1 else moda_vocacion

        if vocacion_usuario:
            # Actualizar vocación existente
            vocacion_usuario.moda_vocacion = moda_vocacion
            vocacion_usuario.moda_vocacion2 = moda_vocacion2
            db.commit()
            db.refresh(vocacion_usuario)
            return {
                "message": "Vocación actualizada exitosamente.",
                "data": {
                    "id": vocacion_usuario.id,
                    "moda_vocacion": moda_vocacion,
                    "moda_vocacion2": moda_vocacion2,
                },
            }
        else:
            # Crear nueva vocación
            nueva_vocacion = VocacionDeUsuarioPorTest(
                id_usuario=current_user["user_id"],
                id_test=id_test,
                moda_vocacion=moda_vocacion,
                moda_vocacion2=moda_vocacion2,
            )
            db.add(nueva_vocacion)
            db.commit()
            db.refresh(nueva_vocacion)
            return {
                "message": "Vocación creada exitosamente.",
                "data": {
                    "id": nueva_vocacion.id,
                    "moda_vocacion": moda_vocacion,
                    "moda_vocacion2": moda_vocacion2,
                },
            }
    except HTTPException as http_ex:
        db.rollback()
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()

def get_vocacion_usuario_por_test_service(id_test: int, current_user: dict):
    """
    Retorna la vocación registrada para un usuario en un test específico.
    """
    db = next(get_db_session())
    try:
        vocacion_usuario = (
            db.query(VocacionDeUsuarioPorTest)
            .filter(
                VocacionDeUsuarioPorTest.id_usuario == current_user["user_id"],
                VocacionDeUsuarioPorTest.id_test == id_test,
            )
            .first()
        )

        if not vocacion_usuario:
            raise HTTPException(
                status_code=404,
                detail="No se encontró vocación para el test especificado."
            )

        return {
            "message": "Vocación encontrada exitosamente.",
            "data": {
                "id": vocacion_usuario.id,
                "id_test": vocacion_usuario.id_test,
                "moda_vocacion": vocacion_usuario.moda_vocacion,
                "moda_vocacion2": vocacion_usuario.moda_vocacion2,
            }
        }
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()

def get_all_vocaciones_usuario_service(current_user: dict):
    """
    Lista todos los tests realizados por el usuario, incluyendo el id del test,
    nombre del test y la vocación (moda) obtenida, junto con la segunda moda.
    """
    db = next(get_db_session())
    try:
        vocaciones = (
            db.query(VocacionDeUsuarioPorTest)
            .filter(VocacionDeUsuarioPorTest.id_usuario == current_user["user_id"])
            .all()
        )

        resultados = []
        for vocacion in vocaciones:
            # Se asume que el modelo Test tiene un atributo 'nombre'
            resultados.append({
                "id_test": vocacion.id_test,
                "nombre_test": vocacion.test.nombre,
                "moda_vocacion": vocacion.moda_vocacion,
                "moda_vocacion2": vocacion.moda_vocacion2,
            })

        return {
            "message": "Lista de vocaciones obtenida exitosamente.",
            "data": resultados
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()