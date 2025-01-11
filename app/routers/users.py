from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..services.user_services import get_user_data_service
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