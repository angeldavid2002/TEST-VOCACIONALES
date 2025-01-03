from fastapi import HTTPException
from sqlalchemy import func

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
