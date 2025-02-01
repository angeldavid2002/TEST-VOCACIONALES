from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..models.mdl_resena import ResenaCreate
from ..services.auth_service import verify_jwt_token
from ..services.resena_service import (
    create_resena_service,
    get_resenas_paginated_desc_service,
    get_resenas_paginated_asc_service,
    get_resenas_by_rating_service,
    get_resenas_by_user_id_service,
    get_average_rating_service,
    edit_resena_service,
    delete_resena_service,
    count_total_resenas_service,
    count_resenas_by_rating_service,
    get_all_reviews_service
)

router = APIRouter()

# Configurar el esquema de seguridad HTTPBearer
security = HTTPBearer()


@router.post("/register")
async def create_resena(
    resena: ResenaCreate,
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),  # Dependencia para extraer el token
):
    try:
        # Extraer el token del encabezado
        token = credentials.credentials

        # Verificar si el token es válido
        user_info = verify_jwt_token(token)

        # Llamar al servicio para crear la reseña
        response = create_resena_service(resena, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# Consultar reseñas de más reciente a más antigua
@router.get("/recent")
async def get_recent_reviews(
    page: int = Query(1, gt=0),  # Validar que skip sea no negativo
):
    try:
        return get_resenas_paginated_desc_service(page=page)
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# Consultar reseñas de más antigua a más reciente
@router.get("/oldest")
async def get_oldest_reviews(
    page: int = Query(1, gt=0),
):
    try:
        return get_resenas_paginated_asc_service(page=page)
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# Filtrar reseñas por calificación
@router.get("/filter_rating")
async def filter_reviews_by_rating(
    rating: int,
    page: int = Query(1, gt=0),
):
    try:
        return get_resenas_by_rating_service(rating=rating, page=page)
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 4. Consultar reseñas por ID de usuario (token)
@router.get("/user")
async def get_reviews_by_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        user_info = verify_jwt_token(credentials.credentials)
        return get_resenas_by_user_id_service(user_id=user_info["user_id"])
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")


# 5. Calcular el promedio de puntuaciones
@router.get("/average")
async def get_reviews_average(
):
    try:
        return {"average_rating": get_average_rating_service()}
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

# 6. editar reseña
@router.put("/edit/{resena_id}")
async def edit_resena(
    resena_id: int,
    resena: ResenaCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Extraer el token del encabezado
        token = credentials.credentials

        # Verificar si el token es válido y obtener la información del usuario
        user_info = verify_jwt_token(token)

        # Llamar al servicio para editar la reseña
        response = edit_resena_service(resena_id, resena, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(
            status_code=500, detail=f"Error interno: {str(ex)}"
        )

# 7. eliminar reseña
@router.delete("/delete/{resena_id}")
async def delete_resena(
    resena_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Extraer el token del encabezado
        token = credentials.credentials

        # Verificar si el token es válido y obtener la información del usuario
        user_info = verify_jwt_token(token)

        # Llamar al servicio para eliminar la reseña
        response = delete_resena_service(resena_id, user_info)
        return response
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(
            status_code=500, detail=f"Error interno: {str(ex)}"
        )
        

# 8. Contabilizar el total de reseñas
@router.get("/count")
async def count_total_resenas():
    try:
        total = count_total_resenas_service()
        return {"total_resenas": total}
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(
            status_code=500, detail=f"Error interno: {str(ex)}"
        )


# 9. Contabilizar reseñas por puntuación específica
@router.get("/count_by_rating")
async def count_resenas_by_rating(rating: int):
    try:
        count = count_resenas_by_rating_service(rating=rating)
        return {"rating": rating, "count": count}
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(
            status_code=500, detail=f"Error interno: {str(ex)}"
        )

@router.get("/all")
async def get_all_reviews():
    try:
        return get_all_reviews_service()
    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

