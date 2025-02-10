import unittest
import warnings
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException

from app.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_jwt_token,
)
from app.config import config

# Suprimir warnings de deprecación (DeprecationWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class TestAuthService(unittest.TestCase):
    def setUp(self):
        # Datos de ejemplo para las pruebas
        self.user_data = {
            "user_id": 1,
            "email": "test@example.com",
            "tipo_usuario": "admin"
        }
        self.password = "mysecretpassword"
        # Generar un token válido utilizando la función del servicio
        self.valid_token = create_access_token(self.user_data)

    def test_get_password_hash_and_verify_password(self):
        """Verifica que la contraseña se hashee y se valide correctamente."""
        hashed = get_password_hash(self.password)
        self.assertNotEqual(hashed, self.password, "El hash no debe ser igual al password en claro")
        self.assertTrue(verify_password(self.password, hashed), "La verificación de la contraseña debería ser True")

    def test_create_access_token_returns_string_and_valid_payload(self):
        """Verifica que create_access_token retorne un token de tipo string y con el payload esperado."""
        token = create_access_token(self.user_data)
        self.assertIsInstance(token, str, "El token debe ser de tipo str")
        # Decodificar el token y verificar el payload
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        self.assertEqual(payload.get("user_id"), self.user_data["user_id"])
        self.assertEqual(payload.get("email"), self.user_data["email"])
        self.assertEqual(payload.get("tipo_usuario"), self.user_data["tipo_usuario"])
        self.assertIn("exp", payload)

    @patch("app.services.auth_service.jwt.decode")
    def test_verify_jwt_token_valid(self, mock_decode):
        """Verifica que verify_jwt_token retorne el payload correcto para un token válido."""
        # Simula que jwt.decode retorna el payload correcto
        mock_decode.return_value = self.user_data.copy()
        token = "valid.token.string"
        payload = verify_jwt_token(token)
        self.assertEqual(payload.get("user_id"), self.user_data["user_id"])
        self.assertEqual(payload.get("email"), self.user_data["email"])
        self.assertEqual(payload.get("tipo_usuario"), self.user_data["tipo_usuario"])

    @patch("app.services.auth_service.jwt.decode")
    def test_verify_jwt_token_expired(self, mock_decode):
        """Simula un token expirado y verifica que se lance una excepción 401 con el mensaje 'El token ha expirado.'."""
        # Forzar que jwt.decode lance un ExpiredSignatureError
        mock_decode.side_effect = ExpiredSignatureError("Token expired")
        token = "expired.token.string"
        with self.assertRaises(HTTPException) as context:
            verify_jwt_token(token)
        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("El token ha expirado", context.exception.detail)

    @patch("app.services.auth_service.jwt.decode")
    def test_verify_jwt_token_invalid(self, mock_decode):
        """Simula un token inválido y verifica que se lance una excepción 401 con el mensaje 'Token inválido o mal formado.'."""
        # Forzar que jwt.decode lance un JWTError
        mock_decode.side_effect = JWTError("Invalid token")
        token = "invalid.token.string"
        with self.assertRaises(HTTPException) as context:
            verify_jwt_token(token)
        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("Token inválido o mal formado", context.exception.detail)
