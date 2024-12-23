from fastapi import APIRouter, HTTPException
from ..models.mdl_user import UsuarioCreate, UsuarioLogin
from ..services.user_services import *

router = APIRouter()

@router.post("/register")
async def register(user: UsuarioCreate):
    try:
        response = register_user(user)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/login")
async def login(user: UsuarioLogin):
    try:
        response = login_user(user.email, user.password)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))