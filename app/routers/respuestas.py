from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..services.auth_service import verify_jwt_token
from ..services.respuesta_service import (
    list_respuestas_by_pregunta,
    search_respuesta_by_id,
    create_respuesta_service,
    update_respuesta_service,
    delete_respuesta_service,
)
from ..models.mdl_respuesta import RespuestaCreate, RespuestaUpdate

# Crear el router
router = APIRouter()

# Configurar el esquema de seguridad HTTPBearer
security = HTTPBearer()

# 1. Listar respuestas por pregunta_id
@router.get("/list/{pregunta_id}")
async def get_respuestas_by_pregunta(
    pregunta_id: int,
    page: int = Query(default=1, gt=0),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = list_respuestas_by_pregunta(pregunta_id, page, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 2. Buscar respuesta por ID
@router.get("/search/{respuesta_id}")
async def get_respuesta_by_id(
    respuesta_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = search_respuesta_by_id(respuesta_id, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 3. Crear respuesta
@router.post("/create")
async def create_respuesta(
    respuesta: RespuestaCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = create_respuesta_service(respuesta, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 4. Editar respuesta
@router.put("/update")
async def update_respuesta(
    respuesta: RespuestaUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = update_respuesta_service(respuesta, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 5. Eliminar respuesta
@router.delete("/delete/{respuesta_id}")
async def delete_respuesta(
    respuesta_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = delete_respuesta_service(respuesta_id, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
