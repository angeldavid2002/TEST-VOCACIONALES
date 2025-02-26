import csv
import io
from fastapi import HTTPException
from sqlalchemy import func
from ..db.database import get_db_session
from ..schemas.sch_usuario import Usuario
from ..schemas.sch_ciudad import Ciudad
from ..schemas.sch_vocacion_usuario import VocacionDeUsuarioPorTest
from ..schemas.sch_respuesta_usuario import RespuestaDeUsuario

def get_users_vocations_csv_service():
    db = next(get_db_session())
    try:
        # Solo usuarios normales: filtro Usuario.tipo_usuario != 'admin'
        results = (
            db.query(
                Usuario.id,
                Usuario.nombre,
                Usuario.email,
                VocacionDeUsuarioPorTest.moda_vocacion,
                VocacionDeUsuarioPorTest.moda_vocacion2
            )
            .join(VocacionDeUsuarioPorTest, Usuario.id == VocacionDeUsuarioPorTest.id_usuario)
            .filter(Usuario.tipo_usuario != 'admin')
            .all()
        )
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["User ID", "Nombre", "Email", "Vocacion Principal", "Vocacion Secundaria"])
        for row in results:
            writer.writerow(row)
        return output.getvalue()
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()

def get_cities_common_vocation_csv_service(current_user: dict):
    db = next(get_db_session())
    try:
        # Consulta para obtener ciudades con la vocación más común de usuarios normales
        results = (
            db.query(
                Ciudad.id.label("city_id"),
                Ciudad.nombre.label("city_name"),
                Ciudad.latitud,
                Ciudad.longitud,
                VocacionDeUsuarioPorTest.moda_vocacion
            )
            .join(Usuario, Ciudad.id == Usuario.id_ciudad)
            .join(VocacionDeUsuarioPorTest, Usuario.id == VocacionDeUsuarioPorTest.id_usuario)
            .filter(Usuario.tipo_usuario != 'admin')
            .group_by(
                Ciudad.id,
                Ciudad.nombre,
                Ciudad.latitud,
                Ciudad.longitud,
                VocacionDeUsuarioPorTest.moda_vocacion
            )
            .all()
        )
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["City ID", "City Name", "Latitud", "Longitud", "Vocacion Principal"])
        for r in results:
            writer.writerow([r.city_id, r.city_name, r.latitud, r.longitud, r.moda_vocacion])
        return output.getvalue()
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()

def get_vocation_percentages_csv_service(current_user: dict):
    db = next(get_db_session())
    try:
        # Contar el total de usuarios normales (no admin)
        total_users = db.query(func.count(Usuario.id)).filter(Usuario.tipo_usuario != 'admin').scalar()
        if total_users == 0:
            raise HTTPException(status_code=404, detail="No se encontraron usuarios normales.")
        # Obtener la vocación principal y su conteo para usuarios normales
        results = (
            db.query(
                VocacionDeUsuarioPorTest.moda_vocacion,
                func.count(VocacionDeUsuarioPorTest.id).label("count")
            )
            .join(Usuario, Usuario.id == VocacionDeUsuarioPorTest.id_usuario)
            .filter(Usuario.tipo_usuario != 'admin')
            .group_by(VocacionDeUsuarioPorTest.moda_vocacion)
            .all()
        )
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Vocacion", "Porcentaje"])
        for vocacion, count in results:
            percentage = round((count / total_users) * 100)
            writer.writerow([vocacion, percentage])
        return output.getvalue()
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()

def get_users_by_city_csv_service(current_user: dict):
    db = next(get_db_session())
    try:
        # Filtrar solo usuarios normales
        results = (
            db.query(
                Ciudad.id.label("city_id"),
                Ciudad.nombre.label("city_name"),
                Usuario.id.label("user_id"),
                Usuario.nombre.label("user_name"),
                Usuario.email.label("email")
            )
            .join(Usuario, Ciudad.id == Usuario.id_ciudad)
            .filter(Usuario.tipo_usuario != 'admin')
            .all()
        )
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["City ID", "City Name", "User ID", "User Name", "Email"])
        for r in results:
            writer.writerow([r.city_id, r.city_name, r.user_id, r.user_name, r.email])
        return output.getvalue()
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        db.close()
