from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..models.mdl_user import PasswordChangeRequest, UsuarioUpdate
from ..services.user_services import (
    change_password_service,
    edit_user_service,
    get_user_data_service,
)
from ..services.auth_service import verify_jwt_token

router = APIRouter()

# Configuración del esquema de seguridad HTTPBearer
security = HTTPBearer()


@router.get("/data")
async def get_user_data(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # Verificar token del usuario
        token = credentials.credentials
        user_info = verify_jwt_token(token)

        # Obtener los datos del usuario
        response = get_user_data_service(user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.put("/change-password")
async def change_password(
    password_request: PasswordChangeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Verificar el token y obtener la información del usuario
        token = credentials.credentials
        user_info = verify_jwt_token(token)

        # Llamar al servicio para cambiar la contraseña
        response = change_password_service(password_request, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

@router.put("/edit")
async def edit_user(
    user_data: UsuarioUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Verificar el token y obtener la información del usuario
        token = credentials.credentials
        current_user = verify_jwt_token(token)

        # Llamar al servicio para editar el usuario
        response = edit_user_service(user_data, current_user)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

