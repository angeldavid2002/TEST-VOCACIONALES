from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..services.statics_service import (
    contar_total_tests,
    list_cities_with_users_service,
    list_usuarios_por_institucion_service,
    obtener_moda_vocacion_mas_comun,
    vocacion_mas_comun_por_ciudad_service,
)
from ..services.auth_service import verify_jwt_token

router = APIRouter()

# Configurar el esquema de seguridad HTTPBearer
security = HTTPBearer()


# 1. Listar ciudades con usuarios (solo admin)
@router.get("/list/cities")
async def get_cities_with_users(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = list_cities_with_users_service(user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 2. Endpoint para obtener usuarios por institución
@router.get("/instituciones/usuarios")
async def get_usuarios_por_institucion(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Extraer el token del encabezado
        token = credentials.credentials

        # Verificar el token y obtener información del usuario
        user_info = verify_jwt_token(token)

        # Llamar al servicio para obtener los datos
        response = list_usuarios_por_institucion_service(user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 3. Vocación más común (solo admin)
@router.get("/common-vocation")
async def get_moda_vocacion_mas_comun(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = obtener_moda_vocacion_mas_comun(user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

# 4. Total de test creados (solo admin)
@router.get("/total-tests")
async def get_total_tests(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = contar_total_tests(user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

# 5. Vocación más común por ciudad (solo admin)
@router.get("/city-common-vocation")
async def get_vocacion_mas_comun_por_ciudad(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = vocacion_mas_comun_por_ciudad_service(user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")