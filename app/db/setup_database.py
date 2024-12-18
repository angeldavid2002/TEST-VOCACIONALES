import os
from .database import engine, SessionLocal
from ..schemas.sch_base import Base

# Importar todos los modelos
from ..schemas.sch_ciudad import Ciudad
from ..schemas.sch_institucion import Institucion
from ..schemas.sch_usuario import Usuario
from ..schemas.sch_test import Test
from ..schemas.sch_pregunta import Pregunta
from ..schemas.sch_respuesta import Respuesta
from ..schemas.sch_respuesta_usuario import RespuestaDeUsuario
from ..schemas.sch_vocacion_usuario import VocacionDeUsuarioPorTest
from ..schemas.sch_resena import Resena

from datetime import datetime, timezone

def initialize_database():
    # Verificar si la base de datos ya existe
    if os.path.exists("database.db"):
        print("La base de datos ya existe. No es necesario inicializarla nuevamente.")
        return

    # Crear tablas
    Base.metadata.create_all(bind=engine)

    # Crear sesión
    session = SessionLocal()

    # Insertar ciudades de Colombia
    ciudades = [
        {"nombre": "Bogotá", "latitud": 4.60971, "longitud": -74.08175},
        {"nombre": "Medellín", "latitud": 6.25184, "longitud": -75.56359},
        {"nombre": "Cali", "latitud": 3.43722, "longitud": -76.5225},
        {"nombre": "Barranquilla", "latitud": 10.96854, "longitud": -74.78132},
        {"nombre": "Cartagena", "latitud": 10.39972, "longitud": -75.51444},
        {"nombre": "Tunja", "latitud": 5.5355, "longitud": -73.3672},
        {"nombre": "Manizales", "latitud": 5.06889, "longitud": -75.51738},
        {"nombre": "Florencia", "latitud": 1.6167, "longitud": -75.6167},
        {"nombre": "Yopal", "latitud": 5.3352, "longitud": -72.3964},
        {"nombre": "Popayán", "latitud": 2.43823, "longitud": -76.61316},
        {"nombre": "Valledupar", "latitud": 10.46314, "longitud": -73.25322},
        {"nombre": "Quibdó", "latitud": 5.6940, "longitud": -76.6536},
        {"nombre": "Montería", "latitud": 8.74798, "longitud": -75.88143},
        {"nombre": "Inírida", "latitud": 3.8667, "longitud": -67.9667},
        {"nombre": "San José del Guaviare", "latitud": 2.5700, "longitud": -72.6500},
        {"nombre": "Neiva", "latitud": 2.9273, "longitud": -75.28189},
        {"nombre": "Riohacha", "latitud": 11.54479, "longitud": -74.19904},
        {"nombre": "Santa Marta", "latitud": 11.24079, "longitud": -74.19904},
        {"nombre": "Villavicencio", "latitud": 4.1420, "longitud": -73.62664},
        {"nombre": "San Juan de Pasto", "latitud": 1.21361, "longitud": -77.28111},
        {"nombre": "Cúcuta", "latitud": 7.89391, "longitud": -72.50782},
        {"nombre": "Mocoa", "latitud": 1.1519, "longitud": -76.6487},
        {"nombre": "Armenia", "latitud": 4.5333, "longitud": -75.6811},
        {"nombre": "Pereira", "latitud": 4.81333, "longitud": -75.69611},
        {"nombre": "San Andrés", "latitud": 12.5833, "longitud": -81.7000},
        {"nombre": "Bucaramanga", "latitud": 7.12539, "longitud": -73.1198},
        {"nombre": "Sincelejo", "latitud": 9.3033, "longitud": -75.4000},
        {"nombre": "Ibagué", "latitud": 4.43889, "longitud": -75.23222},
        {"nombre": "Leticia", "latitud": -4.2159, "longitud": -69.9408},
        {"nombre": "Arauca", "latitud": 7.0902, "longitud": -70.7470},
        {"nombre": "Bello", "latitud": 6.33732, "longitud": -75.55795},
        {"nombre": "Soledad", "latitud": 10.91843, "longitud": -74.76459},
    ]

    for ciudad in ciudades:
        ciudad_obj = Ciudad(**ciudad)
        session.add(ciudad_obj)
    # Obtener la ciudad de Valledupar para asociarla a las instituciones
    valledupar = session.query(Ciudad).filter_by(nombre="Valledupar").first()

    # Insertar instituciones (colegios) en Valledupar
    colegios_valledupar = [
        {
            "nombre": "Colegio Nacional Loperena",
            "direccion": "Calle 14 # 11-50, Valledupar",
            "telefono": "3201234567",
        },
        {
            "nombre": "Institución Educativa CASD Simón Bolívar",
            "direccion": "Carrera 19 # 6-20, Valledupar",
            "telefono": "3019876543",
        },
        {
            "nombre": "Colegio Gimnasio del Norte",
            "direccion": "Avenida Fundación # 21-10, Valledupar",
            "telefono": "3124567890",
        },
    ]

    for colegio in colegios_valledupar:
        institucion_obj = Institucion(
            nombre=colegio["nombre"],
            direccion=colegio["direccion"],
            telefono=colegio["telefono"],
        )
        session.add(institucion_obj)
    
    # Insertar usuario administrador
    admin = Usuario(
        email="admin@universidadcesar.edu.co",
        nombre="Administrador",
        contrasena="UPCVT",  # En producción guarda contraseñas hasheadas
        tipo_usuario="admin",
        fecha_registro=datetime.now(timezone.utc),
    )
    session.add(admin)

    # Confirmar los cambios
    session.commit()
    session.close()
    print("Base de datos inicializada correctamente.")

if __name__ == "__main__":
    initialize_database()
