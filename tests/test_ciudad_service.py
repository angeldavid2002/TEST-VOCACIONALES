from types import SimpleNamespace
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from fastapi import HTTPException
from app.services.ciudad_service import (
    register_city_service,
    update_city_service,
    delete_city_service,
    list_ciudades_service,
)
from app.models.mdl_ciudad import CiudadCreate, CiudadUpdate
from app.config import config

# Objeto dummy para simular una ciudad existente (para update, delete y list)
dummy_city = MagicMock()
dummy_city.id = 1
dummy_city.nombre = "Dummy City"
dummy_city.latitud = 1.23
dummy_city.longitud = 4.56

# Dummy current_user para administrador y para usuario no admin
admin_user = {"tipo_usuario": "admin"}
non_admin_user = {"tipo_usuario": "comun"}

class TestCiudadService(unittest.TestCase):

    @patch("app.services.ciudad_service.get_db_session")
    def test_register_city_success(self, mock_get_db_session):
        # Configurar un mock de sesión
        mock_session = MagicMock()
        # Simular que no existe ciudad con ese nombre
        # Para la consulta, first() retorna None
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        # Datos de registro
        city_data = CiudadCreate(
            nombre="New City",
            latitud=2.34,
            longitud=5.67
        )
        
        result = register_city_service(city_data, admin_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Ciudad registrada exitosamente")
        # Verificar commit y refresh fueron llamados
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch("app.services.ciudad_service.get_db_session")
    def test_register_city_already_exists(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que ya existe una ciudad con ese nombre
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_city
        mock_get_db_session.return_value = iter([mock_session])
        
        city_data = CiudadCreate(
            nombre="Dummy City",  # Nombre que ya existe
            latitud=2.34,
            longitud=5.67
        )
        with self.assertRaises(HTTPException) as context:
            register_city_service(city_data, admin_user)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("La ciudad con el nombre", context.exception.detail)

    @patch("app.services.ciudad_service.get_db_session")
    def test_register_city_not_admin(self, mock_get_db_session):
        # Usuario sin privilegios admin
        with self.assertRaises(HTTPException) as context:
            register_city_service(CiudadCreate(nombre="New City", latitud=2.34, longitud=5.67), non_admin_user)
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("No tiene los privilegios", context.exception.detail)

    @patch("app.services.ciudad_service.get_db_session")
    def test_register_city_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        # Forzar que first() lance una excepción inesperada
        mock_session.query.return_value.filter.return_value.first.side_effect = Exception("Unexpected error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            register_city_service(CiudadCreate(nombre="Error City", latitud=0, longitud=0), admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.ciudad_service.get_db_session")
    def test_update_city_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la ciudad existe
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_city
        mock_get_db_session.return_value = iter([mock_session])
        
        update_data = CiudadUpdate(
            nombre="Updated City",
            latitud=3.45,
            longitud=6.78
        )
        result = update_city_service(1, update_data, admin_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Ciudad actualizada exitosamente")
        # Verificar que se actualicen los campos
        self.assertEqual(dummy_city.nombre, "Updated City")
        self.assertEqual(dummy_city.latitud, 3.45)
        self.assertEqual(dummy_city.longitud, 6.78)

    @patch("app.services.ciudad_service.get_db_session")
    def test_update_city_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la ciudad no se encuentra
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        update_data = CiudadUpdate(nombre="Updated City")
        with self.assertRaises(HTTPException) as context:
            update_city_service(999, update_data, admin_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("La ciudad con ID 999 no existe", context.exception.detail)

    @patch("app.services.ciudad_service.get_db_session")
    def test_update_city_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            update_city_service(1, CiudadUpdate(nombre="Updated City"), non_admin_user)
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.ciudad_service.get_db_session")
    def test_update_city_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que ocurre un error durante commit
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_city
        mock_session.commit.side_effect = Exception("Commit error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            update_city_service(1, CiudadUpdate(nombre="Fail City"), admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.ciudad_service.get_db_session")
    def test_delete_city_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la ciudad existe
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_city
        mock_get_db_session.return_value = iter([mock_session])
        
        result = delete_city_service(1, admin_user)
        self.assertIn("message", result)
        self.assertIn("eliminada exitosamente", result["message"])
        mock_session.commit.assert_called_once()

    @patch("app.services.ciudad_service.get_db_session")
    def test_delete_city_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la ciudad no existe
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_city_service(999, admin_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("La ciudad con ID 999 no existe", context.exception.detail)

    @patch("app.services.ciudad_service.get_db_session")
    def test_delete_city_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            delete_city_service(1, non_admin_user)
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.ciudad_service.get_db_session")
    def test_delete_city_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_city
        mock_session.delete.side_effect = Exception("Delete error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_city_service(1, admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.ciudad_service.get_db_session")
    def test_list_ciudades_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que hay dos ciudades en la base de datos
        dummy_city2 = SimpleNamespace(
            id=2,
            nombre="Another City",
            latitud=7.89,
            longitud=0.12
        )
        mock_session.query.return_value.all.return_value = [dummy_city, dummy_city2]
        mock_get_db_session.return_value = iter([mock_session])
        
        result = list_ciudades_service()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["nombre"], dummy_city.nombre)
        self.assertEqual(result[1]["nombre"], dummy_city2.nombre)

    @patch("app.services.ciudad_service.get_db_session")
    def test_list_ciudades_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            list_ciudades_service()
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)
