from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..services.auth_service import verify_jwt_token
from ..services.test_service import (
    create_test_service,
    get_test_by_id_service,
    list_tests_service,
    delete_test_service,
    update_test_service,
)
from ..models.mdl_test import TestCreate

# 4 rutas

router = APIRouter()

# Configurar el esquema de seguridad HTTPBearer
security = HTTPBearer()


# 1. registrar test
@router.post("/register")
async def create_test(
    test: TestCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Extraer el token del encabezado
        token = credentials.credentials

        # Verificar el token y obtener información del usuario
        user_info = verify_jwt_token(token)

        # Llamar al servicio para crear el test
        response = create_test_service(test, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

# 2. Listar tests
@router.get("/list")
async def list_tests(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Extraer el token del encabezado
        token = credentials.credentials

        # Verificar el token y obtener información del usuario
        user_info = verify_jwt_token(token)

        # Llamar al servicio para listar todos los tests sin paginación
        response = list_tests_service()
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

# Obterner test por id
@router.get("/{test_id}", response_model=dict)
def get_test_by_id(test_id: int):
    return get_test_by_id_service(test_id)

# 3. Eliminar tests
@router.delete("/{test_id}")
async def delete_test(
    test_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Extraer el token del encabezado
        token = credentials.credentials

        # Verificar el token y obtener información del usuario
        user_info = verify_jwt_token(token)

        # Llamar al servicio para eliminar el test
        response = delete_test_service(test_id, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

# 4. Editar test
@router.put("/{test_id}")
async def update_test(
    test_id: int,
    test: TestCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Extraer el token del encabezado
        token = credentials.credentials

        # Verificar el token y obtener información del usuario
        user_info = verify_jwt_token(token)

        # Llamar al servicio para actualizar el test
        response = update_test_service(test_id, test, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
