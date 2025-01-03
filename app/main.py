from fastapi import FastAPI
from .routers import (
    auth,
    respuestas,
    tests,
    resenas,
    preguntas,
    respuestaUsuario,
    vocacionUsuario,
    statics,
)

app = FastAPI()

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(resenas.router, prefix="/resenas", tags=["Reseñas"])
app.include_router(tests.router, prefix="/tests", tags=["Tests"])
app.include_router(preguntas.router, prefix="/preguntas", tags=["Preguntas"])
app.include_router(respuestas.router, prefix="/respuestas", tags=["Respuestas"])
app.include_router(respuestaUsuario.router, prefix="/respuestaUsuario", tags=["Respuesta usuario"])
app.include_router(vocacionUsuario.router, prefix="/vocacion", tags=["Vocacion usuario"])
app.include_router(statics.router, prefix="/statics", tags=["Estadisticas tests"])
