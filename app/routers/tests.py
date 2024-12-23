from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..services.auth_service import verify_jwt_token
from ..services.test_service import create_test_service
from ..models.mdl_test import TestCreate

#21 rutas

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
