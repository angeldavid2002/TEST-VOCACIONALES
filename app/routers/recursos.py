from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..models.mdl_recurso import RecursoCreate, RecursoUpdate
from ..services.recurso_service import (
    delete_recurso_service,
    edit_recurso_service,
    get_total_recursos,
    list_recursos_service,
    register_recurso_service,
)
from ..services.auth_service import verify_jwt_token

router = APIRouter()

# Configuración del esquema de seguridad HTTPBearer
security = HTTPBearer()


@router.post("/register")
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

@router.put("/editar/{recurso_id}")
async def edit_recurso(
    recurso_id: int,
    recurso_data: RecursoUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = edit_recurso_service(recurso_id, recurso_data, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

@router.delete("/borrar/{recurso_id}")
async def delete_recurso(
    recurso_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = delete_recurso_service(recurso_id, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

@router.get("/listar")
async def list_recursos(
    recurso_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
    try:
        token = credentials.credentials
        verify_jwt_token(token)
        response = list_recursos_service()
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
<<<<<<< HEAD
    

=======

@router.get("/total")
async def get_total_recursos_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        verify_jwt_token(token)
        # Obtener el total de recursos
        response = get_total_recursos()
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
>>>>>>> 5389e873a92c08d700a5c5313746f459bc044230
