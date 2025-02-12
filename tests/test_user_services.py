import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace

from fastapi import HTTPException
from app.services.user_services import (
    register_user,
    login_user,
    get_user_data_service,
    change_password_service,
    edit_user_service
)
from app.models.mdl_user import UsuarioCreate, UsuarioUpdate, PasswordChangeRequest
from app.services.auth_service import get_password_hash, verify_password, create_access_token
from app.config import config

# Objeto dummy para un usuario ya existente (para pruebas de email existente)
dummy_user = SimpleNamespace(
    id=1,
    nombre="Test User",
    email="test@example.com",
    sexo="Masculino",
    contrasena="hashedpassword",
    tipo_usuario="comun",
    id_ciudad=1,
    id_institucion=1,
    fecha_registro=datetime.now(timezone.utc).date()
)

# Objetos dummy para Ciudad e Institución para simular su existencia
dummy_city = SimpleNamespace(
    id=1,
    nombre="Dummy City",
    latitud=1.23,
    longitud=4.56
)
dummy_institution = SimpleNamespace(
    id=1,
    nombre="Dummy Institution",
    direccion="Calle Falsa 123",
    telefono="1234567890"
)

class TestUserServices(unittest.TestCase):

    @patch("app.services.user_services.get_db_session")
    def test_register_user_success(self, mock_get_db_session):
        # Configurar un mock de sesión
        mock_session = MagicMock()
        # Simular: 1) No existe usuario con ese email, 2) La ciudad existe, 3) La institución existe.
        mock_filter = MagicMock()
        mock_filter.first.side_effect = [None, dummy_city, dummy_institution]
        mock_session.query.return_value.filter.return_value = mock_filter
        mock_get_db_session.return_value = iter([mock_session])
        
        user_data = UsuarioCreate(
            email="newuser@example.com",
            nombre="New User",
            sexo="Masculino",
            password="newpassword",
            id_ciudad=1,
            id_institucion=1,
            fecha_registro=datetime.now(timezone.utc).date()
        )
        
        result = register_user(user_data)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Usuario registrado exitosamente")
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch("app.services.user_services.get_db_session")
    def test_register_user_email_exists(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que ya existe un usuario con ese email.
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_user
        mock_get_db_session.return_value = iter([mock_session])
        
        user_data = UsuarioCreate(
            email="test@example.com",
            nombre="Test User",
            sexo="Masculino",
            password="password",
            id_ciudad=1,
            id_institucion=1,
            fecha_registro=datetime.now(timezone.utc).date()
        )
        with self.assertRaises(HTTPException) as context:
            register_user(user_data)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("El email ya está registrado", context.exception.detail)

    @patch("app.services.user_services.get_db_session")
    def test_register_user_city_not_found(self, mock_get_db_session):
        # Simular que la ciudad no existe.
        mock_session = MagicMock()
        # La primera llamada (usuario) retorna None, la segunda (ciudad) retorna None
        mock_filter = MagicMock()
        mock_filter.first.side_effect = [None, None]  # No se encuentra ciudad
        mock_session.query.return_value.filter.return_value = mock_filter
        mock_get_db_session.return_value = iter([mock_session])
        
        user_data = UsuarioCreate(
            email="another@example.com",
            nombre="Another User",
            sexo="Masculino",
            password="password",
            id_ciudad=999,  # id de ciudad inexistente
            id_institucion=1,
            fecha_registro=datetime.now(timezone.utc).date()
        )
        with self.assertRaises(HTTPException) as context:
            register_user(user_data)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("La ciudad con id 999 no existe", context.exception.detail)

    @patch("app.services.user_services.get_db_session")
    def test_register_user_institution_not_found(self, mock_get_db_session):
        # Simular que la institución no existe.
        mock_session = MagicMock()
        # Cadena: usuario no existe -> None; ciudad existe -> dummy_city; institución -> None
        mock_filter = MagicMock()
        mock_filter.first.side_effect = [None, dummy_city, None]
        mock_session.query.return_value.filter.return_value = mock_filter
        mock_get_db_session.return_value = iter([mock_session])
        
        user_data = UsuarioCreate(
            email="another2@example.com",
            nombre="Another User 2",
            sexo="Masculino",
            password="password",
            id_ciudad=1,
            id_institucion=999,  # id de institución inexistente
            fecha_registro=datetime.now(timezone.utc).date()
        )
        with self.assertRaises(HTTPException) as context:
            register_user(user_data)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("La institución con id 999 no existe", context.exception.detail)

    @patch("app.services.user_services.get_db_session")
    def test_register_user_unexpected_exception(self, mock_get_db_session):
        # Simular una excepción inesperada en register_user
        mock_session = MagicMock()
        # Configuramos first() para lanzar una excepción
        mock_session.query.return_value.filter.return_value.first.side_effect = Exception("Unexpected error")
        mock_get_db_session.return_value = iter([mock_session])
        
        user_data = UsuarioCreate(
            email="error@example.com",
            nombre="Error User",
            sexo="Masculino",
            password="password",
            id_ciudad=1,
            id_institucion=1,
            fecha_registro=datetime.now(timezone.utc).date()
        )
        with self.assertRaises(HTTPException) as context:
            register_user(user_data)
        self.assertEqual(context.exception.status_code, 500)

    @patch("app.services.user_services.get_db_session")
    def test_login_user_unexpected_exception(self, mock_get_db_session):
        # Simular una excepción inesperada en login_user
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.side_effect = Exception("DB error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            login_user("test@example.com", "password")
        self.assertEqual(context.exception.status_code, 500)

    @patch("app.services.user_services.get_db_session")
    def test_get_user_data_service_not_authorized(self, mock_get_db_session):
        # Simular un current_user sin 'user_id'
        current_user = {}
        with self.assertRaises(HTTPException) as context:
            get_user_data_service(current_user)
        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("No está autorizado", context.exception.detail)

    @patch("app.services.user_services.get_db_session")
    def test_get_user_data_service_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 999}
        with self.assertRaises(HTTPException) as context:
            get_user_data_service(current_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Usuario no encontrado", context.exception.detail)

    @patch("app.services.user_services.get_db_session")
    def test_get_user_data_service_internal_error(self, mock_get_db_session):
        # Simular un error interno al ejecutar la consulta
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Internal DB error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            get_user_data_service({"user_id": 1})
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.user_services.get_db_session")
    def test_change_password_service_user_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        password_request = PasswordChangeRequest(
            current_password="oldpassword",
            new_password="newpassword",
            confirm_password="newpassword"
        )
        with self.assertRaises(HTTPException) as context:
            change_password_service(password_request, {"user_id": 999})
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Usuario no encontrado", context.exception.detail)

    @patch("app.services.user_services.get_db_session")
    def test_change_password_service_internal_error(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que al hacer commit se lanza una excepción
        dummy_db_user = SimpleNamespace(
            id=1,
            contrasena=get_password_hash("oldpassword")
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_db_user
        mock_session.commit.side_effect = Exception("Commit error")
        mock_get_db_session.return_value = iter([mock_session])
        
        password_request = PasswordChangeRequest(
            current_password="oldpassword",
            new_password="newpassword",
            confirm_password="newpassword"
        )
        with self.assertRaises(HTTPException) as context:
            change_password_service(password_request, {"user_id": 1})
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.user_services.get_db_session")
    def test_edit_user_service_internal_error(self, mock_get_db_session):
        mock_session = MagicMock()
        dummy_db_user = SimpleNamespace(
            id=1,
            nombre="Test User",
            email="test@example.com",
            sexo="Masculino",
            id_ciudad=1,
            id_institucion=1,
            fecha_registro=datetime.now(timezone.utc).date()
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_db_user
        # Simular error en commit
        mock_session.commit.side_effect = Exception("Commit error")
        mock_get_db_session.return_value = iter([mock_session])
        
        update_data = UsuarioUpdate(
            nombre="Updated User",
            id_ciudad=2,
            id_institucion=3
        )
        with self.assertRaises(HTTPException) as context:
            edit_user_service(update_data, {"user_id": 1})
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

