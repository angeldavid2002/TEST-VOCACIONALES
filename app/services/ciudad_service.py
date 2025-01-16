from fastapi import HTTPException
from ..db.database import get_db_session
from ..schemas.sch_ciudad import Ciudad
from ..models.mdl_ciudad import CiudadCreate, CiudadUpdate


def register_city_service(city: CiudadCreate, current_user):
    # Verificar si el usuario tiene privilegios de administrador
    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para registrar ciudades.",
        )

    db = next(get_db_session())
    try:
        # Validar si la ciudad ya existe por nombre
        if db.query(Ciudad).filter(Ciudad.nombre == city.nombre).first():
            raise HTTPException(
                status_code=400,
                detail=f"La ciudad con el nombre '{city.nombre}' ya está registrada.",
            )

        # Crear nueva ciudad
        nueva_ciudad = Ciudad(
            nombre=city.nombre,
            latitud=city.latitud,
            longitud=city.longitud,
        )

        # Guardar en la base de datos
        db.add(nueva_ciudad)
        db.commit()
        db.refresh(nueva_ciudad)

        return {"message": "Ciudad registrada exitosamente", "id": nueva_ciudad.id}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()

def update_city_service(city_id: int, city: CiudadUpdate, current_user):
    # Verificar si el usuario tiene privilegios de administrador
    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para editar ciudades.",
        )

    db = next(get_db_session())
    try:
        # Buscar la ciudad por ID
        ciudad_existente = db.query(Ciudad).filter(Ciudad.id == city_id).first()
        if not ciudad_existente:
            raise HTTPException(
                status_code=404,
                detail=f"La ciudad con ID {city_id} no existe.",
            )

        # Actualizar los campos de la ciudad
        ciudad_existente.nombre = (
            city.nombre if city.nombre else ciudad_existente.nombre
        )
        ciudad_existente.latitud = (
            city.latitud if city.latitud is not None else ciudad_existente.latitud
        )
        ciudad_existente.longitud = (
            city.longitud if city.longitud is not None else ciudad_existente.longitud
        )

        # Guardar los cambios en la base de datos
        db.commit()
        db.refresh(ciudad_existente)

        return {"message": "Ciudad actualizada exitosamente", "id": ciudad_existente.id}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()

def delete_city_service(city_id: int, current_user):
    # Verificar si el usuario tiene privilegios de administrador
    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para eliminar ciudades.",
        )

    db = next(get_db_session())
    try:
        # Buscar la ciudad por ID
        ciudad = db.query(Ciudad).filter(Ciudad.id == city_id).first()
        if not ciudad:
            raise HTTPException(
                status_code=404,
                detail=f"La ciudad con ID {city_id} no existe.",
            )

        # Eliminar la ciudad
        db.delete(ciudad)
        db.commit()

        return {"message": f"Ciudad con ID {city_id} eliminada exitosamente."}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()

def list_ciudades_service():
    db = next(get_db_session())
    try:
        ciudades = db.query(Ciudad).all()

        # Estructurar la respuesta
        response = [
            {
                "id": ciudad.id,
                "nombre": ciudad.nombre,
                "latitud": ciudad.latitud,
                "longitud": ciudad.longitud,
            }
            for ciudad in ciudades
        ]
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()
