import unittest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from datetime import datetime, timezone

from fastapi import HTTPException
from app.services.statics_service import (
    list_cities_with_users_service,
    list_usuarios_por_institucion_service,
    obtener_moda_vocacion_mas_comun,
    contar_total_tests,
    vocacion_mas_comun_por_ciudad_service,
    get_most_common_vocation_per_institution_service,
    get_most_common_vocation_per_gender_service,
    count_non_admin_users_service,
    count_completed_tests_service,
)
from app.config import config

# Dummy current_user para admin y no admin
admin_user = {"user_id": 1, "tipo_usuario": "admin"}
dummy_usuario = {"user_id": 2, "tipo_usuario": "comun"}  # Usuario no admin

# Dummy para Ciudad (para list_cities_with_users_service)
dummy_city = SimpleNamespace(
    id=1,
    nombre="City A",
    latitud=4.5,
    longitud=-74.1,
    cantidad_usuarios=10  # valor simulado
)

# Dummy para Institucion (para list_usuarios_por_institucion_service)
dummy_institucion = SimpleNamespace(
    id=1,
    nombre="Institution A",
    direccion="Street 123",
    telefono="1234567890",
    cantidad_usuarios=20
)

# Dummy para obtener_moda_vocacion_mas_comun: simulamos que la consulta retorna una tupla (moda, conteo)
dummy_moda = ("VocacionX", 15)

# Dummy para count_completed_tests_service: simulamos que el total es 3
dummy_completed_tests = 3

# Dummy para vocacion_mas_comun_por_ciudad_service: simulamos un objeto con datos
dummy_vocacion_ciudad = SimpleNamespace(
    id_ciudad=1,
    nombre_ciudad="City A",
    latitud=4.5,
    longitud=-74.0,
    moda_vocacion="VocacionY",
    conteo=10
)

# Dummy para get_most_common_vocation_per_institution_service
dummy_inst_vocacion = SimpleNamespace(
    id=1,
    nombre="Institution A",
    direccion="Street 123",
    telefono="1234567890",
    moda_vocacion="VocacionZ",
    max_count=5
)

# Dummy para get_most_common_vocation_per_gender_service
dummy_gender = SimpleNamespace(
    sexo="Masculino",
    moda_vocacion="VocacionW",
    max_count=7
)

# Dummy para count_non_admin_users_service
dummy_non_admin_count = 25

class TestStaticsService(unittest.TestCase):

    # --- Tests for list_cities_with_users_service ---
    @patch("app.services.statics_service.get_db_session")
    def test_list_cities_with_users_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular cadena de métodos: query.outerjoin().group_by().all()
        mock_query = MagicMock()
        mock_query.outerjoin.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [dummy_city]
        mock_session.query.return_value = mock_query
        mock_get_db_session.return_value = iter([mock_session])
        
        result = list_cities_with_users_service(admin_user)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["id"], dummy_city.id)
        self.assertEqual(result[0]["nombre"], dummy_city.nombre)
        self.assertEqual(result[0]["cantidad_usuarios"], dummy_city.cantidad_usuarios)

    @patch("app.services.statics_service.get_db_session")
    def test_list_cities_with_users_service_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            list_cities_with_users_service(dummy_usuario)
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.statics_service.get_db_session")
    def test_list_cities_with_users_service_no_cities(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.outerjoin.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            list_cities_with_users_service(admin_user)
        self.assertEqual(context.exception.status_code, 404)

    @patch("app.services.statics_service.get_db_session")
    def test_list_cities_with_users_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("City query error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            list_cities_with_users_service(admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "City query error")

    # --- Tests for list_usuarios_por_institucion_service ---
    @patch("app.services.statics_service.get_db_session")
    def test_list_usuarios_por_institucion_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.outerjoin.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [dummy_institucion]
        mock_session.query.return_value = mock_query
        mock_get_db_session.return_value = iter([mock_session])
        result = list_usuarios_por_institucion_service(admin_user)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["id"], dummy_institucion.id)
        self.assertEqual(result[0]["nombre"], dummy_institucion.nombre)
        self.assertEqual(result[0]["cantidad_usuarios"], dummy_institucion.cantidad_usuarios)

    @patch("app.services.statics_service.get_db_session")
    def test_list_usuarios_por_institucion_service_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            list_usuarios_por_institucion_service(dummy_usuario)
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.statics_service.get_db_session")
    def test_list_usuarios_por_institucion_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Institution query error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            list_usuarios_por_institucion_service(admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    # --- Tests for obtener_moda_vocacion_mas_comun ---
    @patch("app.services.statics_service.get_db_session")
    def test_obtener_moda_vocacion_mas_comun_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular cadena: query.group_by().order_by().first()
        mock_query = MagicMock()
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = dummy_moda
        mock_session.query.return_value = mock_query
        mock_get_db_session.return_value = iter([mock_session])
        result = obtener_moda_vocacion_mas_comun(admin_user)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["moda_vocacion"], dummy_moda[0])
        self.assertEqual(result["conteo"], dummy_moda[1])
        self.assertIn("La vocación más común es", result["message"])

    @patch("app.services.statics_service.get_db_session")
    def test_obtener_moda_vocacion_mas_comun_no_data(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None
        mock_session.query.return_value = mock_query
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            obtener_moda_vocacion_mas_comun(admin_user)
        self.assertEqual(context.exception.status_code, 404)

    @patch("app.services.statics_service.get_db_session")
    def test_obtener_moda_vocacion_mas_comun_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            obtener_moda_vocacion_mas_comun(dummy_usuario)
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.statics_service.get_db_session")
    def test_obtener_moda_vocacion_mas_comun_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Moda query error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            obtener_moda_vocacion_mas_comun(admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    # --- Tests for contar_total_tests ---
    @patch("app.services.statics_service.get_db_session")
    def test_contar_total_tests_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.count.return_value = dummy_total_tests = 5
        mock_get_db_session.return_value = iter([mock_session])
        result = contar_total_tests(admin_user)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["total_tests"], dummy_total_tests)
        self.assertIn(f"El total de tests creados es {dummy_total_tests}", result["message"])

    @patch("app.services.statics_service.get_db_session")
    def test_contar_total_tests_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            contar_total_tests(dummy_usuario)
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.statics_service.get_db_session")
    def test_contar_total_tests_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Test count error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            contar_total_tests(admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    # --- Tests for vocacion_mas_comun_por_ciudad_service ---
    @patch("app.services.statics_service.get_db_session")
    def test_vocacion_mas_comun_por_ciudad_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Configurar la cadena de llamadas para que .all() devuelva una lista con un objeto dummy
        mock_query = MagicMock()
        mock_query.join.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [dummy_vocacion_ciudad]
        mock_session.query.return_value = mock_query
        mock_get_db_session.return_value = iter([mock_session])
        result = vocacion_mas_comun_por_ciudad_service(admin_user)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["id_ciudad"], dummy_vocacion_ciudad.id_ciudad)
        self.assertEqual(result[0]["nombre_ciudad"], dummy_vocacion_ciudad.nombre_ciudad)

    @patch("app.services.statics_service.get_db_session")
    def test_vocacion_mas_comun_por_ciudad_service_no_data(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.join.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            vocacion_mas_comun_por_ciudad_service(admin_user)
        self.assertEqual(context.exception.status_code, 404)

    @patch("app.services.statics_service.get_db_session")
    def test_vocacion_mas_comun_por_ciudad_service_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            vocacion_mas_comun_por_ciudad_service(dummy_usuario)
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.statics_service.get_db_session")
    def test_vocacion_mas_comun_por_ciudad_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("City vocacion error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            vocacion_mas_comun_por_ciudad_service(admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    # --- Tests for get_most_common_vocation_per_institution_service ---
    @patch("app.services.statics_service.get_db_session")
    def test_get_most_common_vocation_per_institution_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Configurar cadena para que .all() devuelva un listado con dummy_inst_vocacion
        mock_query = MagicMock()
        mock_query.join.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [dummy_inst_vocacion]
        mock_session.query.return_value = mock_query
        mock_get_db_session.return_value = iter([mock_session])
        result = get_most_common_vocation_per_institution_service(admin_user)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["ID_Institucion"], dummy_inst_vocacion.id)
        self.assertEqual(result[0]["Moda_Vocacion"], dummy_inst_vocacion.moda_vocacion)

    @patch("app.services.statics_service.get_db_session")
    def test_get_most_common_vocation_per_institution_service_no_data(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.join.return_value.group_by.return_value.all.return_value = []
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            get_most_common_vocation_per_institution_service(admin_user)
        self.assertEqual(context.exception.status_code, 404)

    @patch("app.services.statics_service.get_db_session")
    def test_get_most_common_vocation_per_institution_service_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            get_most_common_vocation_per_institution_service(dummy_usuario)
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.statics_service.get_db_session")
    def test_get_most_common_vocation_per_institution_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Institution vocacion error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            get_most_common_vocation_per_institution_service(admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    # --- Tests for get_most_common_vocation_per_gender_service ---
    @patch("app.services.statics_service.get_db_session")
    def test_get_most_common_vocation_per_gender_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Configurar cadena para que .group_by().having().all() devuelva una lista con dummy_gender
        mock_query = MagicMock()
        mock_query.group_by.return_value = mock_query
        mock_query.having.return_value = mock_query
        mock_query.all.return_value = [dummy_gender]
        mock_session.query.return_value = mock_query
        mock_get_db_session.return_value = iter([mock_session])
        result = get_most_common_vocation_per_gender_service(admin_user)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["Sexo"], dummy_gender.sexo)
        self.assertEqual(result[0]["Moda_Vocacion"], dummy_gender.moda_vocacion)

    @patch("app.services.statics_service.get_db_session")
    def test_get_most_common_vocation_per_gender_service_no_data(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.group_by.return_value = mock_query
        mock_query.having.return_value = mock_query
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            get_most_common_vocation_per_gender_service(admin_user)
        self.assertEqual(context.exception.status_code, 404)

    @patch("app.services.statics_service.get_db_session")
    def test_get_most_common_vocation_per_gender_service_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            get_most_common_vocation_per_gender_service(dummy_usuario)
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.statics_service.get_db_session")
    def test_get_most_common_vocation_per_gender_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Gender vocacion error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            get_most_common_vocation_per_gender_service(admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    # --- Tests for count_non_admin_users_service ---
    @patch("app.services.statics_service.get_db_session")
    def test_count_non_admin_users_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.count.return_value = dummy_non_admin_count
        mock_get_db_session.return_value = iter([mock_session])
        result = count_non_admin_users_service(admin_user)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["total_usuarios"], dummy_non_admin_count)

    @patch("app.services.statics_service.get_db_session")
    def test_count_non_admin_users_service_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            count_non_admin_users_service(dummy_usuario)
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.statics_service.get_db_session")
    def test_count_non_admin_users_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.side_effect = Exception("Non admin count error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            count_non_admin_users_service(admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Non admin count error")

    # --- Tests for count_completed_tests_service ---
    @patch("app.services.statics_service.get_db_session")
    def test_count_completed_tests_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que el scalar devuelve dummy_completed_tests
        mock_session.query.return_value.filter.return_value.scalar.return_value = dummy_completed_tests
        mock_get_db_session.return_value = iter([mock_session])
        result = count_completed_tests_service(admin_user)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["total_test_respondidos"], dummy_completed_tests)

    @patch("app.services.statics_service.get_db_session")
    def test_count_completed_tests_service_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            count_completed_tests_service(dummy_usuario)
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.statics_service.get_db_session")
    def test_count_completed_tests_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Test count error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            count_completed_tests_service(admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)
