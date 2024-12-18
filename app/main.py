from fastapi import FastAPI
from app.routers import resenas
from routers import auth, tests

app = FastAPI()

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(resenas.router, prefix="/reseñas", tags=["reseñas"])
app.include_router(tests.router, prefix="/tests", tags=["tests"])
