from fastapi import FastAPI
from .routers import auth, tests, resenas

app = FastAPI()

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(resenas.router, prefix="/resenas", tags=["Reseñas"])
app.include_router(tests.router, prefix="/tests", tags=["tests"])
