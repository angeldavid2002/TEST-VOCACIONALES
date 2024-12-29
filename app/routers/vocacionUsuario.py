from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..services.vocacion_usuario_service import create_or_update_vocacion_usuario_service
from ..services.auth_service import verify_jwt_token


# 4 rutas

router = APIRouter()

# Configurar el esquema de seguridad HTTPBearer
security = HTTPBearer()

# 1. Ruta para crear o actualizar un usuario con vocación
@router.post("/vocacion-usuario/create-update/{id_test}")
async def create_or_update_vocacion_usuario(
    id_test: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Extraer y verificar el token
        token = credentials.credentials
        user_info = verify_jwt_token(token)

        # Llamar al servicio para manejar la lógica de creación/actualización
        response = create_or_update_vocacion_usuario_service(id_test, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")