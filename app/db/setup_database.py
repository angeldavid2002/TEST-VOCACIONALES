# Importar librerías
import os
from datetime import datetime, timezone
from sqlalchemy import inspect, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles

# Importar servicios y configuraciones
from ..services.auth_service import get_password_hash
from ..config import config

# Importar modelos
from ..schemas.sch_base import Base
from ..schemas.sch_ciudad import Ciudad
from ..schemas.sch_institucion import Institucion
from ..schemas.sch_usuario import Usuario
from ..schemas.sch_test import Test
from ..schemas.sch_pregunta import Pregunta
from ..schemas.sch_respuesta import Respuesta
from ..schemas.sch_respuesta_usuario import RespuestaDeUsuario
from ..schemas.sch_vocacion_usuario import VocacionDeUsuarioPorTest
from ..schemas.sch_resena import Resena
from ..schemas.sch_recurso import Recurso

# Importar configuración de la base de datos
from .database import engine, get_db_session


@compiles(DropTable)
def add_if_exists(element, compiler, **kwargs):
    # Extiende DropTable para agregar 'IF EXISTS' a las consultas.
    return compiler.visit_drop_table(element) + " IF EXISTS"


def initialize_database():
    # Inicializa la base de datos:
    # Si no existe, la crea con el esquema completo.
    # Si existe, sincroniza completamente el esquema con los modelos.

    if not os.path.exists("database.db"):
        print("La base de datos no existe. Creando una nueva...")
        create_schema()
    else:
        print("La base de datos ya existe. Sincronizando esquema...")
        sync_schema()

    # Insertar datos iniciales
    insert_initial_data()


def create_schema():
    # Crea el esquema inicial de la base de datos.
    Base.metadata.create_all(bind=engine)
    print("Esquema inicial creado.")


def sync_schema():
    # Sincroniza el esquema de la base de datos:
    # Elimina tablas y columnas que no están definidas en los modelos.
    # Crea tablas y columnas que faltan en la base de datos.
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # Eliminar tablas que no están en los modelos
    for table_name in existing_tables:
        if table_name not in Base.metadata.tables:
            print(f"Tabla '{table_name}' no está en los modelos. Eliminándola...")
            with engine.connect() as connection:
                connection.execute(DropTable(Base.metadata.tables.get(table_name)))

    # Crear y actualizar tablas y columnas
    Base.metadata.create_all(bind=engine)

    # Sincronizar columnas
    with engine.connect() as connection:
        for table_name, table in Base.metadata.tables.items():
            if table_name in existing_tables:
                columns = inspector.get_columns(table_name)
                column_names = [col["name"] for col in columns]

                # Eliminar columnas que no están en los modelos
                for col in columns:
                    if col["name"] not in table.columns:
                        print(
                            f"Columna '{col['name']}' no está en el modelo de la tabla '{table_name}'. Eliminándola..."
                        )
                        connection.execute(
                            text(f"ALTER TABLE {table_name} DROP COLUMN {col['name']}")
                        )

                # Agregar columnas que faltan en la tabla
                for column in table.columns:
                    if column.name not in column_names:
                        print(
                            f"Columna '{column.name}' no encontrada en la tabla '{table_name}'. Agregándola..."
                        )
                        alter_table_add_column(connection, table_name, column)


def alter_table_add_column(connection, table_name, column):
    # Agrega una columna a una tabla existente.
    column_type = str(column.type.compile(dialect=engine.dialect))
    default_clause = (
        f"DEFAULT {column.default.arg}" if column.default is not None else ""
    )
    nullable_clause = "" if column.nullable else "NOT NULL"
    alter_query = text(
        f"ALTER TABLE {table_name} ADD COLUMN {column.name} {column_type} {nullable_clause} {default_clause};"
    )

    try:
        connection.execute(alter_query)
        print(f"Columna '{column.name}' agregada a la tabla '{table_name}'.")
    except ProgrammingError as e:
        print(
            f"Error al agregar columna '{column.name}' a la tabla '{table_name}': {e}"
        )


def insert_initial_data():
    # Inserta datos iniciales si no existen, evitando duplicados.
    session_generator = get_db_session()
    session = next(session_generator)
    try:
        # Insertar ciudades
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
            {
                "nombre": "San José del Guaviare",
                "latitud": 2.5700,
                "longitud": -72.6500,
            },
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
            if not session.query(Ciudad).filter_by(nombre=ciudad["nombre"]).first():
                session.add(Ciudad(**ciudad))

        # Insertar instituciones en Valledupar
        valledupar = session.query(Ciudad).filter_by(nombre="Valledupar").first()
        if valledupar:
            instituciones = [
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
            for institucion in instituciones:
                if (
                    not session.query(Institucion)
                    .filter_by(nombre=institucion["nombre"])
                    .first()
                ):
                    session.add(Institucion(**institucion))

        # Insertar usuario administrador
        if not session.query(Usuario).filter_by(email=config.ADMIN_EMAIL).first():
            admin = Usuario(
                email=config.ADMIN_EMAIL,
                nombre=config.ADMIN_NAME,
                sexo="Masculino",
                contrasena=get_password_hash(config.ADMIN_PASSWORD),
                tipo_usuario=config.ADMIN_USER_TYPE,
                fecha_registro=datetime.now(timezone.utc),
            )
            session.add(admin)

        session.commit()
        print("Datos iniciales insertados correctamente.")
    except Exception as e:
        session.rollback()
        print(f"Error al insertar datos iniciales: {e}")
    finally:
        session.close()
        next(session_generator, None)


if __name__ == "__main__":
    initialize_database()
