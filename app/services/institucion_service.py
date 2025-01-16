from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..db.database import get_db_session
from ..schemas.sch_institucion import Institucion
from ..models.mdl_institucion import InstitucionCreate, InstitucionUpdate


def register_institucion_service(institucion_data: InstitucionCreate, current_user):

    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para registrar instituciones.",
        )

    db = next(get_db_session())
    try:
        # Verificar si ya existe una institución con el mismo nombre
        if (
            db.query(Institucion)
            .filter(Institucion.nombre == institucion_data.nombre)
            .first()
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe una institución con el nombre '{institucion_data.nombre}'.",
            )

        nueva_institucion = Institucion(
            nombre=institucion_data.nombre,
            direccion=institucion_data.direccion,
            telefono=institucion_data.telefono,
        )

        db.add(nueva_institucion)
        db.commit()
        db.refresh(nueva_institucion)

        return {
            "message": "Institución registrada exitosamente",
            "id": nueva_institucion.id,
        }
    except HTTPException as e:
        raise e
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()


def update_institucion_service(
    id: int, institucion_data: InstitucionUpdate, current_user
):
    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para editar instituciones.",
        )

    db = next(get_db_session())
    try:
        institucion = db.query(Institucion).filter(Institucion.id == id).first()
        if not institucion:
            raise HTTPException(
                status_code=404, detail=f"No se encontró la institución con ID {id}."
            )

        # Actualizar solo los campos proporcionados
        institucion.nombre = institucion_data.nombre or institucion.nombre
        institucion.direccion = institucion_data.direccion or institucion.direccion
        institucion.telefono = institucion_data.telefono or institucion.telefono

        db.commit()
        db.refresh(institucion)

        return {"message": "Institución actualizada exitosamente", "id": institucion.id}
    except HTTPException as e:
        raise e
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()


def delete_institucion_service(id: int, current_user):

    if current_user.get("tipo_usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para eliminar instituciones.",
        )

    db = next(get_db_session())
    try:
        institucion = db.query(Institucion).filter(Institucion.id == id).first()
        if not institucion:
            raise HTTPException(
                status_code=404, detail=f"No se encontró la institución con ID {id}."
            )

        # Verificar si hay usuarios asociados
        if institucion.usuarios:  # Asegúrate de que la relación usuarios esté definida
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar la institución '{institucion.nombre}' porque tiene usuarios asociados.",
            )

        db.delete(institucion)
        db.commit()

        return {"message": "Institución eliminada exitosamente"}
    except HTTPException as e:
        raise e
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()


def list_instituciones_service():

    db = next(get_db_session())
    try:
        instituciones = db.query(Institucion).all()

        response = [
            {
                "id": institucion.id,
                "nombre": institucion.nombre,
                "direccion": institucion.direccion,
                "telefono": institucion.telefono,
            }
            for institucion in instituciones
        ]

        return {"total": len(response), "instituciones": response}
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()
