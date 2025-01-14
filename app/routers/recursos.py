from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..models.mdl_recurso import RecursoCreate
from ..services.recurso_service import register_recurso_service
from ..services.auth_service import verify_jwt_token

router = APIRouter()

# Configuración del esquema de seguridad HTTPBearer
security = HTTPBearer()


@router.post("/recursos/register")
async def register_recurso(
    recurso: RecursoCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Verificar el token del usuario
        token = credentials.credentials
        user_info = verify_jwt_token(token)

        # Llamar al servicio para registrar el recurso
        response = register_recurso_service(recurso, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
