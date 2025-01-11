from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..models.mdl_ciudad import CiudadCreate, CiudadUpdate
from ..services.ciudad_service import register_city_service, update_city_service
from ..services.auth_service import verify_jwt_token

router = APIRouter()

# Configuración del esquema de seguridad HTTPBearer
security = HTTPBearer()

@router.post("/register")
async def register_city(
    city: CiudadCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Verificar el token del usuario
        token = credentials.credentials
        user_info = verify_jwt_token(token)

        # Llamar al servicio para registrar la ciudad
        response = register_city_service(city, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

@router.put("/update/{city_id}")
async def update_city(
    city_id: int,
    city: CiudadUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Verificar el token del usuario
        token = credentials.credentials
        user_info = verify_jwt_token(token)

        # Llamar al servicio para actualizar la ciudad
        response = update_city_service(city_id, city, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")