from fastapi import HTTPException
from sqlalchemy import func

from ..schemas.sch_pregunta import Pregunta
from ..schemas.sch_respuesta_usuario import RespuestaDeUsuario
from ..schemas.sch_test import Test
from ..schemas.sch_vocacion_usuario import VocacionDeUsuarioPorTest
from ..schemas.sch_institucion import Institucion
from ..schemas.sch_ciudad import Ciudad
from ..schemas.sch_usuario import Usuario
from ..db.database import get_db_session


# Servicio para listar usuarios por ciudad
def list_cities_with_users_service(current_user):
    # Verificar si el usuario tiene rol de administrador
    if current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para acceder a esta información.",
        )

    db = next(get_db_session())
    try:
        # Consultar ciudades con el conteo de usuarios por ciudad
        cities = (
            db.query(
                Ciudad.id,
                Ciudad.nombre,
                Ciudad.latitud,
                Ciudad.longitud,
                func.count(Usuario.id).label("cantidad_usuarios"),
            )
            .outerjoin(Usuario, Ciudad.id == Usuario.id_ciudad)
            .group_by(Ciudad.id, Ciudad.nombre, Ciudad.latitud, Ciudad.longitud)
            .all()
        )

        if not cities:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron ciudades registradas.",
            )

        return [
            {
                "id": city.id,
                "nombre": city.nombre,
                "latitud": city.latitud,
                "longitud": city.longitud,
                "cantidad_usuarios": city.cantidad_usuarios,
            }
            for city in cities
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

# Servicio para listar usuarios por institución
def list_usuarios_por_institucion_service(current_user):
    # Verificar si el usuario tiene rol de administrador
    if current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para acceder a esta información.",
        )

    db = next(get_db_session())
    try:
        # Consulta las instituciones con la cantidad de usuarios asociados
        instituciones = (
            db.query(
                Institucion.id,
                Institucion.nombre,
                Institucion.direccion,
                func.count(Usuario.id).label("cantidad_usuarios"),
            )
            .outerjoin(Usuario, Usuario.id_institucion == Institucion.id)
            .group_by(Institucion.id, Institucion.nombre, Institucion.direccion)
            .all()
        )

        # Formatear la respuesta
        return [
            {
                "id": inst.id,
                "nombre": inst.nombre,
                "direccion": inst.direccion,
                "cantidad_usuarios": inst.cantidad_usuarios,
            }
            for inst in instituciones
        ]
    except HTTPException as http_ex:
        # Propagar las excepciones HTTP específicas
        db.rollback()
        raise http_ex
    except Exception as ex:
        # Propagar las excepciones HTTP no manejadas
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()

# Servicio para obtener moda mas comun
def obtener_moda_vocacion_mas_comun(current_user):
    # Verificar si el usuario es administrador
    if current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para realizar esta operación.",
        )

    db = next(get_db_session())
    try:
        # Consultar la moda de la vocación más común
        moda_vocacion = (
            db.query(
                VocacionDeUsuarioPorTest.moda_vocacion,
                func.count(VocacionDeUsuarioPorTest.moda_vocacion).label("conteo"),
            )
            .group_by(VocacionDeUsuarioPorTest.moda_vocacion)
            .order_by(func.count(VocacionDeUsuarioPorTest.moda_vocacion).desc())
            .first()
        )

        if not moda_vocacion:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron datos en la tabla de vocaciones de usuario por test.",
            )

        return {
            "moda_vocacion": moda_vocacion[0],
            "conteo": moda_vocacion[1],
            "message": f"La vocación más común es '{moda_vocacion[0]}' con {moda_vocacion[1]} apariciones.",
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

# Servicio para contar los test
def contar_total_tests(current_user):
    # Verificar si el usuario es administrador
    if current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para realizar esta operación.",
        )

    db = next(get_db_session())
    try:
        # Contar la cantidad total de tests creados
        total_tests = db.query(Test).count()

        return {
            "total_tests": total_tests,
            "message": f"El total de tests creados es {total_tests}.",
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

# Servicio para obtener la vocacion mas comun por ciudad
def vocacion_mas_comun_por_ciudad_service(current_user):
    # Verificar si el usuario es administrador
    if current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para realizar esta operación.",
        )

    db = next(get_db_session())
    try:
        # Consulta para obtener la vocación más común por ciudad
        resultados = (
            db.query(
                Ciudad.id.label("id_ciudad"),
                Ciudad.nombre.label("nombre_ciudad"),
                Ciudad.latitud,
                Ciudad.longitud,
                VocacionDeUsuarioPorTest.moda_vocacion,
                func.count(VocacionDeUsuarioPorTest.moda_vocacion).label("conteo"),
            )
            .join(Usuario, Usuario.id_ciudad == Ciudad.id)
            .join(
                VocacionDeUsuarioPorTest,
                Usuario.id == VocacionDeUsuarioPorTest.id_usuario,
            )
            .group_by(
                Ciudad.id,
                Ciudad.nombre,
                Ciudad.latitud,
                Ciudad.longitud,
                VocacionDeUsuarioPorTest.moda_vocacion,
            )
            .order_by(func.count(VocacionDeUsuarioPorTest.moda_vocacion).desc())
            .all()
        )

        if not resultados:
            raise HTTPException(
                status_code=404,
                detail="No hay datos suficientes para realizar el cálculo.",
            )

        # Formatear la respuesta
        return [
            {
                "id_ciudad": r.id_ciudad,
                "nombre_ciudad": r.nombre_ciudad,
                "latitud": r.latitud,
                "longitud": r.longitud,
                "moda_vocacion": r.moda_vocacion,
            }
            for r in resultados
        ]
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

# Servicio de vocación más común por institución 
def get_most_common_vocation_per_institution_service(current_user):
    # Verificar si el usuario tiene privilegios de administrador
    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para acceder a esta información.",
        )

    db = next(get_db_session())
    try:
        # Subconsulta para encontrar la moda de vocación por institución
        subquery = (
            db.query(
                Usuario.id_institucion,
                VocacionDeUsuarioPorTest.moda_vocacion,
                func.count(VocacionDeUsuarioPorTest.moda_vocacion).label("vocacion_count"),
            )
            .join(
                VocacionDeUsuarioPorTest,
                Usuario.id == VocacionDeUsuarioPorTest.id_usuario,
            )
            .group_by(Usuario.id_institucion, VocacionDeUsuarioPorTest.moda_vocacion)
            .subquery()
        )

        # Consulta principal para combinar instituciones con la moda de vocaciones
        result = (
            db.query(
                Institucion.id,
                Institucion.nombre,
                Institucion.direccion,
                Institucion.telefono,
                subquery.c.moda_vocacion,
                func.max(subquery.c.vocacion_count).label("max_count"),
            )
            .join(subquery, Institucion.id == subquery.c.id_institucion)
            .group_by(
                Institucion.id,
                Institucion.nombre,
                Institucion.direccion,
                Institucion.telefono,
                subquery.c.moda_vocacion,
            )
            .all()
        )

        # Formatear resultados en una lista de diccionarios
        response = [
            {
                "ID_Institucion": row.id,
                "Nombre": row.nombre,
                "Direccion": row.direccion,
                "Telefono": row.telefono,
                "Moda_Vocacion": row.moda_vocacion,
            }
            for row in result
        ]

        if not response:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron datos para las instituciones.",
            )

        return response
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()

# Servicio de vocación más común por sexo 
def get_most_common_vocation_per_gender_service(current_user):
    # Verificar si el usuario tiene privilegios de administrador
    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para acceder a esta información.",
        )

    db = next(get_db_session())
    try:
        # Subconsulta para encontrar la moda de vocación por sexo
        subquery = (
            db.query(
                Usuario.sexo,
                VocacionDeUsuarioPorTest.moda_vocacion,
                func.count(VocacionDeUsuarioPorTest.moda_vocacion).label("vocacion_count"),
            )
            .join(
                VocacionDeUsuarioPorTest,
                Usuario.id == VocacionDeUsuarioPorTest.id_usuario,
            )
            .group_by(Usuario.sexo, VocacionDeUsuarioPorTest.moda_vocacion)
            .subquery()
        )

        # Consulta principal para combinar sexo con la moda de vocaciones
        result = (
            db.query(
                subquery.c.sexo,
                subquery.c.moda_vocacion,
                func.max(subquery.c.vocacion_count).label("max_count"),
            )
            .group_by(subquery.c.sexo, subquery.c.moda_vocacion)
            .having(func.max(subquery.c.vocacion_count) == subquery.c.vocacion_count)
            .all()
        )

        # Formatear resultados en una lista de diccionarios
        response = [
            {
                "Sexo": row.sexo,
                "Moda_Vocacion": row.moda_vocacion,
            }
            for row in result
        ]

        if not response:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron datos para las vocaciones por sexo.",
            )

        return response
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()

# Servicio de conteo de usuarios
def count_non_admin_users_service(current_user):
    # Verificar si el usuario tiene privilegios de administrador
    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para acceder a esta información.",
        )

    db = next(get_db_session())
    try:
        # Contar usuarios que no sean administradores
        total_usuarios = db.query(Usuario).filter(Usuario.tipo_usuario != "admin").count()

        return {"total_usuarios": total_usuarios}
    except HTTPException as http_ex:
        db.rollback()
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()

# Servicio de conteo de test completados
def count_completed_tests_service(current_user: dict):
    # Verificar si el usuario tiene privilegios de administrador
    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para acceder a esta información.",
        )
        
    db = next(get_db_session())
    try:
        # Subconsulta: para cada test y usuario, contamos cuántas respuestas registró el usuario,
        # y obtenemos el total de preguntas del test.
        subquery = (
            db.query(
                RespuestaDeUsuario.test_id.label("test_id"),
                RespuestaDeUsuario.usuario_id.label("usuario_id"),
                func.count(RespuestaDeUsuario.pregunta_id).label("cnt"),
                # Usamos scalar_subquery() para obtener el total de preguntas para cada test.
                db.query(func.count(Pregunta.id))
                .filter(Pregunta.test_id == RespuestaDeUsuario.test_id)
                .scalar_subquery()
                .label("total_questions")
            )
            .group_by(RespuestaDeUsuario.test_id, RespuestaDeUsuario.usuario_id)
            .subquery()
        )
        
        # Filtrar solo las combinaciones en las que el usuario respondió todas las preguntas,
        # y luego contar de forma distinta los test (es decir, test que fueron completados por al menos un usuario)
        total_complete_tests = (
            db.query(func.count(func.distinct(subquery.c.test_id)))
            .filter(subquery.c.cnt == subquery.c.total_questions)
            .scalar()
        )

        return {
            "total_test_respondidos": total_complete_tests,
        }
    except HTTPException as http_ex:
        db.rollback()
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close() 

# Servicio de porcentajes de usuarios por vocacion
def get_vocation_percentages_service(current_user: dict):
    # Verificar privilegios: solo administradores pueden acceder a esta información
    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para acceder a esta información."
        )
    
    db = next(get_db_session())
    try:
        # Contar el total de registros en vocaciones
        total = db.query(func.count(VocacionDeUsuarioPorTest.id)).scalar()
        if total == 0:
            return {"data": []}
        
        # Agrupar por modalidad de vocación y contar cuántos registros hay por cada una
        results = db.query(
            VocacionDeUsuarioPorTest.moda_vocacion,
            func.count(VocacionDeUsuarioPorTest.id).label("count")
        ).group_by(VocacionDeUsuarioPorTest.moda_vocacion).all()
        
        percentages = []
        for r in results:
            # Calcular el porcentaje y redondearlo a entero
            percentage = int((r.count / total) * 100)
            percentages.append({
                "vocation": r.moda_vocacion,
                "percentage": percentage
            })
        return {"data": percentages}
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()

def get_completed_tests_by_test_service(current_user: dict):
    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para acceder a esta información."
        )
    
    db = next(get_db_session())
    try:
        # Subconsulta: para cada combinación (test, usuario) se cuenta cuántas respuestas ha registrado el usuario
        # y se obtiene, mediante scalar_subquery, el total de preguntas del test.
        subq = (
            db.query(
                RespuestaDeUsuario.test_id.label("test_id"),
                RespuestaDeUsuario.usuario_id.label("usuario_id"),
                func.count(RespuestaDeUsuario.pregunta_id).label("cnt"),
                db.query(func.count(Pregunta.id))
                .filter(Pregunta.test_id == RespuestaDeUsuario.test_id)
                .scalar_subquery().label("total_questions")
            )
            .group_by(RespuestaDeUsuario.test_id, RespuestaDeUsuario.usuario_id)
            .subquery()
        )

        # Filtrar solo aquellas combinaciones donde el usuario completó el test (cnt == total_questions)
        completions = (
            db.query(
                subq.c.test_id,
                func.count(subq.c.usuario_id).label("completions")
            )
            .filter(subq.c.cnt == subq.c.total_questions)
            .group_by(subq.c.test_id)
            .all()
        )

        # Obtener todos los tests para incluir aquellos sin completions
        tests = db.query(Test).all()
        result = []
        for test in tests:
            comp = 0
            for row in completions:
                if row.test_id == test.id:
                    comp = row.completions
                    break
            result.append({
                "test_id": test.id,
                "test_nombre": test.nombre,
                "completions": comp
            })
        return {"data": result}
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()