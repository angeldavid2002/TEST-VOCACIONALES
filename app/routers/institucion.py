from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..models.mdl_institucion import InstitucionCreate, InstitucionUpdate
from ..services.institucion_service import (
    register_institucion_service,
    update_institucion_service,
    delete_institucion_service,
    list_instituciones_service,
)
from ..services.auth_service import verify_jwt_token

router = APIRouter()

# Configuración del esquema de seguridad HTTPBearer
security = HTTPBearer()


@router.post("/register")
async def register_institucion(
    institucion: InstitucionCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = register_institucion_service(institucion, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

@router.put("/update/{id}")
async def update_institucion(
    id: int,
    institucion: InstitucionUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = update_institucion_service(id, institucion, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

@router.delete("/delete/{id}")
async def delete_institucion(
    id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = delete_institucion_service(id, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

@router.get("/list")
async def list_instituciones():
    try:
        response = list_instituciones_service()
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
