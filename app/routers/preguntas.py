from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..services.auth_service import verify_jwt_token
from ..services.pregunta_service import (
    list_preguntas_by_test,
    search_pregunta_by_id,
    create_pregunta_service,
    update_pregunta_service,
    delete_pregunta_service,
)
from ..models.mdl_pregunta import PreguntaCreate, PreguntaUpdate

# Crear el router
router = APIRouter()

# Configurar el esquema de seguridad HTTPBearer
security = HTTPBearer()

# 1. Listar preguntas por Test_ID
@router.get("/list/{test_id}")
async def get_preguntas_by_test(
    test_id: int,
    page: int = Query(default=1, gt=0),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = list_preguntas_by_test(test_id, page, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 2. Buscar pregunta por ID
@router.get("/search/{pregunta_id}")
async def get_pregunta_by_id(
    pregunta_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = search_pregunta_by_id(pregunta_id, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 3. Crear pregunta
@router.post("/create")
async def create_pregunta(
    pregunta: PreguntaCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = create_pregunta_service(pregunta, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 4. Editar pregunta
@router.put("/update")
async def update_pregunta(
    pregunta: PreguntaUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = update_pregunta_service(pregunta, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 5. Eliminar pregunta
@router.delete("/delete/{pregunta_id}")
async def delete_pregunta(
    pregunta_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = delete_pregunta_service(pregunta_id, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
