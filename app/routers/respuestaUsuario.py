from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..services.auth_service import verify_jwt_token
from ..services.respuesta_usuario_service import (
    list_respuestas_usuario,
    create_respuesta_usuario_service,
    update_respuesta_usuario_service,
    delete_respuestas_usuario_admin_service,
)
from ..models.mdl_respuesta_usuario import (
    RespuestaDeUsuarioCreate,
    RespuestaDeUsuarioUpdate,
)

# Crear el router
router = APIRouter()

# Configurar el esquema de seguridad HTTPBearer
security = HTTPBearer()

# 1. Listar respuestas de usuario (usuarios comunes)
@router.get("/list/user")
async def get_respuestas_usuario(
    test_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = list_respuestas_usuario(test_id, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 2. Listar respuestas de usuario (administradores)
""" @router.get("/list/admin")
async def get_respuestas_usuario_admin(
    test_id: int,
    usuario_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = list_respuestas_usuario_admin(test_id, usuario_id, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}") """


# 3. Crear respuesta de usuario
@router.post("/create")
async def create_respuesta_usuario(
    respuesta_data: RespuestaDeUsuarioCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),  # Uso de HTTPBearer
):
    try:
        # Extraer el token del encabezado
        token = credentials.credentials

        # Verificar el token y obtener información del usuario
        user_info = verify_jwt_token(token)

        # Llamar al servicio para manejar la lógica de creación
        response = create_respuesta_usuario_service(respuesta_data, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 4. Editar respuesta de usuario
@router.put("/update")
async def update_respuesta_usuario(
    respuesta_data: RespuestaDeUsuarioUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = update_respuesta_usuario_service(respuesta_data, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 5. Eliminar respuestas de usuario (administradores)
@router.delete("/delete")
async def delete_respuestas_usuario_admin(
    test_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        response = delete_respuestas_usuario_admin_service(test_id, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
