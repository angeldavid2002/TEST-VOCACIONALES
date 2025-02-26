from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import StreamingResponse
from io import StringIO
from app.services.auth_service import verify_jwt_token
from app.services.csv_service import (
    get_users_vocations_csv_service,
    get_cities_common_vocation_csv_service,
    get_vocation_percentages_csv_service,
    get_users_by_city_csv_service
)

router = APIRouter()
security = HTTPBearer()

@router.get("/users-vocations")
async def download_users_vocations_csv(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        if user_info.get("tipo_usuario") != "admin":
            raise HTTPException(status_code=403, detail="No tiene privilegios suficientes.")
        csv_data = get_users_vocations_csv_service()
        return StreamingResponse(StringIO(csv_data), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=users_vocations.csv"})
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

@router.get("/cities-common-vocation")
async def download_cities_common_vocation_csv(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        if user_info.get("tipo_usuario") != "admin":
            raise HTTPException(status_code=403, detail="No tiene privilegios suficientes.")
        csv_data = get_cities_common_vocation_csv_service(user_info)
        return StreamingResponse(StringIO(csv_data), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=cities_common_vocation.csv"})
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

@router.get("/vocation-percentages")
async def download_vocation_percentages_csv(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        if user_info.get("tipo_usuario") != "admin":
            raise HTTPException(status_code=403, detail="No tiene privilegios suficientes.")
        csv_data = get_vocation_percentages_csv_service(user_info)
        return StreamingResponse(StringIO(csv_data), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=vocation_percentages.csv"})
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

@router.get("/users-by-city")
async def download_users_by_city_csv(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        user_info = verify_jwt_token(token)
        if user_info.get("tipo_usuario") != "admin":
            raise HTTPException(status_code=403, detail="No tiene privilegios suficientes.")
        csv_data = get_users_by_city_csv_service(user_info)
        return StreamingResponse(StringIO(csv_data), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=users_by_city.csv"})
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
