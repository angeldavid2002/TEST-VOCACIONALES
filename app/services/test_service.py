from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models.mdl_test import TestCreate
from ..schemas.sch_test import Test
from ..db.database import get_db_session

# Crear un nuevo test
def create_test_service(test: TestCreate, current_user):
    # Verificar si el usuario tiene rol de administrador
    if current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para registrar un test.",
        )

    db = next(get_db_session())
    try:
        # Crear instancia del modelo Test
        nuevo_test = Test(
            nombre=test.nombre,
            descripcion=test.descripcion,
            fecha_creacion=datetime.now(timezone.utc),
            fecha_actualizacion=datetime.now(timezone.utc),
        )

        # Guardar en la base de datos
        db.add(nuevo_test)
        db.commit()
        db.refresh(nuevo_test)

        return {
            "message": "Test registrado exitosamente.",
            "data": {"id": nuevo_test.id},
        }
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()

