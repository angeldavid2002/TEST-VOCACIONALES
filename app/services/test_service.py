from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from ..models.mdl_test import TestCreate
from ..schemas.sch_test import Test
from ..schemas.sch_pregunta import Pregunta
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

# Listar tests con múltiples filtros
def list_tests_service(page: int, nombre: str = None, fecha_actualizacion: str = None):
    db = next(get_db_session())
    try:
        page_size = 10
        offset = (page - 1) * page_size

        # Crear la consulta base con el cálculo de total de preguntas
        query = db.query(
            Test.id,
            Test.nombre,
            Test.descripcion,
            Test.fecha_creacion,
            Test.fecha_actualizacion,
            func.count(Pregunta.id).label(
                "total_preguntas"
            ),  # Contar total de preguntas por test
        ).outerjoin(
            Pregunta, Test.id == Pregunta.test_id
        )  # Outer join para calcular preguntas

        # Aplicar filtros opcionales
        if nombre:
            query = query.filter(Test.nombre.ilike(f"%{nombre}%"))
        if fecha_actualizacion:
            query = query.filter(Test.fecha_actualizacion == fecha_actualizacion)

        # Agrupar por Test.id para el cálculo de total_preguntas
        query = query.group_by(
            Test.id,
            Test.nombre,
            Test.descripcion,
            Test.fecha_creacion,
            Test.fecha_actualizacion,
        )

        # Obtener los tests paginados y contar el total
        tests = (
            query.order_by(Test.fecha_creacion.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        total_tests = query.count()  # Contar el total de tests (sin límite)

        return {
            "data": [
                {
                    "id": test.id,
                    "nombre": test.nombre,
                    "descripcion": test.descripcion,
                    "fecha_creacion": test.fecha_creacion,
                    "fecha_actualizacion": test.fecha_actualizacion,
                    "total_preguntas": test.total_preguntas,
                }
                for test in tests
            ],
            "pagination": {
                "total": total_tests,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_tests + page_size - 1) // page_size,
            },
        }
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

# eliminar test
def delete_test_service(test_id: int, current_user):
    # Verificar que el usuario actual sea administrador
    if not current_user or current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para eliminar un test.",
        )

    db = next(get_db_session())
    try:
        # Obtener el test por ID
        test = db.query(Test).filter(Test.id == test_id).first()
        if not test:
            raise HTTPException(
                status_code=404, detail="El test especificado no existe."
            )

        # Verificar si el test tiene preguntas asociadas
        pregunta_count = db.query(Pregunta).filter(Pregunta.test_id == test_id).count()
        if pregunta_count > 0:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el test porque tiene preguntas asociadas.",
            )

        # Eliminar el test
        db.delete(test)
        db.commit()
        return {"message": "Test eliminado exitosamente."}
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

# Editar test
def update_test_service(test_id: int, test_r:TestCreate, current_user):
    # Verificar que el usuario actual sea administrador
    if not current_user or current_user["tipo_usuario"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tiene los privilegios necesarios para editar un test.",
        )

    db = next(get_db_session())
    try:
        # Obtener el test por ID
        test = db.query(Test).filter(Test.id == test_id).first()
        if not test:
            raise HTTPException(
                status_code=404,
                detail="El test especificado no existe.",
            )

        # Actualizar los campos del test
        test.nombre = test_r.nombre
        test.descripcion = test_r.descripcion
        test.fecha_actualizacion = datetime.now(timezone.utc)

        # Guardar los cambios en la base de datos
        db.commit()
        return {"message": "Test actualizado exitosamente."}
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