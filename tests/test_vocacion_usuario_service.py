import unittest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from datetime import datetime, timezone

from fastapi import HTTPException
from app.services.vocacion_usuario_service import (
    create_or_update_vocacion_usuario_service,
    get_vocacion_usuario_por_test_service,
    get_all_vocaciones_usuario_service,
)
from app.config import config

# Dummy current_user
admin_user = {"user_id": 1, "tipo_usuario": "admin"}
dummy_user = {"user_id": 2, "tipo_usuario": "comun"}

# Dummy Test, Pregunta, Respuesta
dummy_test = SimpleNamespace(id=1)
dummy_pregunta = SimpleNamespace(id=10, test_id=1)
dummy_response_1 = SimpleNamespace(respuesta_id=100)

# Dummy vocacion existente para update
dummy_vocacion = SimpleNamespace(id=50, id_usuario=1, id_test=1, moda_vocacion="Old")

# Dummy para get_vocacion_usuario_por_test
dummy_vocacion_record = SimpleNamespace(id=50, id_usuario=1, id_test=1, moda_vocacion="A")

# Dummy para get_all_vocaciones_usuario_service, con relación al test
dummy_vocacion_with_test = SimpleNamespace(
    id=60,
    id_usuario=1,
    id_test=1,
    moda_vocacion="A",
    test=SimpleNamespace(nombre="Test A")
)

class TestVocacionUsuarioService(unittest.TestCase):

    # --- Tests para create_or_update_vocacion_usuario_service ---

    @patch("app.services.vocacion_usuario_service.get_db_session")
    def test_create_or_update_vocacion_test_not_exist(self, mock_get_db_session):
        mock_session = MagicMock()
        # Primera llamada: query(Test) retorna None (test no existe)
        query_test = MagicMock()
        query_test.filter.return_value.first.return_value = None
        mock_session.query.return_value = query_test
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            create_or_update_vocacion_usuario_service(1, admin_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("El test no existe", context.exception.detail)

    @patch("app.services.vocacion_usuario_service.get_db_session")
    def test_create_or_update_vocacion_incomplete_answers(self, mock_get_db_session):
        mock_session = MagicMock()
        # Configurar las siguientes llamadas en orden:
        # 1. Test query -> retorna dummy_test
        query_test = MagicMock()
        query_test.filter.return_value.first.return_value = dummy_test

        # 2. Vocacion query -> retorna None (no existe registro)
        query_vocacion = MagicMock()
        query_vocacion.filter.return_value.first.return_value = None

        # 3. Respuestas query -> retorna una lista con solo una respuesta (incompleto)
        query_respuestas = MagicMock()
        query_respuestas.filter.return_value.all.return_value = [dummy_response_1]

        # 4. Preguntas count query -> retorna 2 (más que respuestas disponibles)
        query_preguntas = MagicMock()
        query_preguntas.filter.return_value.count.return_value = 2

        # 5. Para cada respuesta en la lista, se realiza una consulta: 
        # Simulamos una llamada que retorne un mock cuya filter().scalar() devuelva "A"
        query_respuesta_vocacion = MagicMock()
        query_respuesta_vocacion.filter.return_value.scalar.return_value = "A"

        # La secuencia de llamadas:
        mock_session.query.side_effect = [
            query_test,          # para Test
            query_vocacion,      # para VocacionDeUsuarioPorTest
            query_respuestas,    # para RespuestaDeUsuario
            query_preguntas,     # para Pregunta count
            query_respuesta_vocacion  # para la primera iteración de la lista (ya que solo hay 1 respuesta)
        ]
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            create_or_update_vocacion_usuario_service(1, admin_user)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("No se han respondido todas las preguntas", context.exception.detail)

    @patch("app.services.vocacion_usuario_service.get_db_session")
    def test_create_or_update_vocacion_update(self, mock_get_db_session):
        mock_session = MagicMock()
        # Secuencia para update: ya existe registro de vocación
        # 1. Test query -> retorna dummy_test
        query_test = MagicMock()
        query_test.filter.return_value.first.return_value = dummy_test

        # 2. Vocacion query -> retorna dummy_vocacion (ya existe)
        query_vocacion = MagicMock()
        query_vocacion.filter.return_value.first.return_value = dummy_vocacion

        # 3. Respuestas query -> retorna dos respuestas (completas)
        query_respuestas = MagicMock()
        query_respuestas.filter.return_value.all.return_value = [dummy_response_1, dummy_response_1]

        # 4. Preguntas count query -> retorna 2
        query_preguntas = MagicMock()
        query_preguntas.filter.return_value.count.return_value = 2

        # 5-6. Para cada respuesta en la lista (2 respuestas), se simula una consulta que retorna "A"
        query_respuesta_vocacion = MagicMock()
        query_respuesta_vocacion.filter.return_value.scalar.return_value = "A"

        mock_session.query.side_effect = [
            query_test,          # Test
            query_vocacion,      # VocacionDeUsuarioPorTest
            query_respuestas,    # RespuestaDeUsuario
            query_preguntas,     # Pregunta count
            query_respuesta_vocacion,  # Para primera respuesta
            query_respuesta_vocacion   # Para segunda respuesta
        ]
        mock_get_db_session.return_value = iter([mock_session])
        
        result = create_or_update_vocacion_usuario_service(1, admin_user)
        self.assertIn("message", result)
        self.assertIn("actualizada", result["message"])
        self.assertEqual(result["data"]["moda_vocacion"], "A")
        mock_session.commit.assert_called_once()

    @patch("app.services.vocacion_usuario_service.get_db_session")
    def test_create_or_update_vocacion_create(self, mock_get_db_session):
        mock_session = MagicMock()
        # Secuencia para creación: no existe vocación previa
        # 1. Test query -> retorna dummy_test
        query_test = MagicMock()
        query_test.filter.return_value.first.return_value = dummy_test

        # 2. Vocacion query -> retorna None
        query_vocacion = MagicMock()
        query_vocacion.filter.return_value.first.return_value = None

        # 3. Respuestas query -> retorna dos respuestas
        query_respuestas = MagicMock()
        query_respuestas.filter.return_value.all.return_value = [dummy_response_1, dummy_response_1]

        # 4. Preguntas count query -> retorna 2
        query_preguntas = MagicMock()
        query_preguntas.filter.return_value.count.return_value = 2

        # 5-6. Para cada respuesta en la lista, simula la consulta que retorna "A"
        query_respuesta_vocacion = MagicMock()
        query_respuesta_vocacion.filter.return_value.scalar.return_value = "A"

        # Secuencia completa de llamadas:
        mock_session.query.side_effect = [
            query_test,          # Test
            query_vocacion,      # VocacionDeUsuarioPorTest
            query_respuestas,    # RespuestaDeUsuario
            query_preguntas,     # Pregunta count
            query_respuesta_vocacion,  # Primera respuesta
            query_respuesta_vocacion   # Segunda respuesta
        ]
        # Simular asignación de id en refresh para la nueva vocación
        def refresh_side_effect(instance):
            instance.id = 60
        mock_session.refresh.side_effect = refresh_side_effect

        mock_get_db_session.return_value = iter([mock_session])
        result = create_or_update_vocacion_usuario_service(1, admin_user)
        self.assertIn("message", result)
        self.assertIn("creada", result["message"])
        self.assertEqual(result["data"]["moda_vocacion"], "A")
        mock_session.commit.assert_called_once()

    @patch("app.services.vocacion_usuario_service.get_db_session")
    def test_create_or_update_vocacion_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Unexpected error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            create_or_update_vocacion_usuario_service(1, admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Unexpected error")

    # --- Tests para get_vocacion_usuario_por_test_service ---
    @patch("app.services.vocacion_usuario_service.get_db_session")
    def test_get_vocacion_usuario_por_test_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_vocacion_record
        mock_get_db_session.return_value = iter([mock_session])
        result = get_vocacion_usuario_por_test_service(1, admin_user)
        self.assertIn("message", result)
        self.assertEqual(result["data"]["moda_vocacion"], "A")

    @patch("app.services.vocacion_usuario_service.get_db_session")
    def test_get_vocacion_usuario_por_test_service_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            get_vocacion_usuario_por_test_service(1, admin_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("No se encontró vocación", context.exception.detail)

    @patch("app.services.vocacion_usuario_service.get_db_session")
    def test_get_vocacion_usuario_por_test_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            get_vocacion_usuario_por_test_service(1, admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")

    # --- Tests for get_all_vocaciones_usuario_service ---
    @patch("app.services.vocacion_usuario_service.get_db_session")
    def test_get_all_vocaciones_usuario_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [dummy_vocacion_with_test]
        mock_get_db_session.return_value = iter([mock_session])
        result = get_all_vocaciones_usuario_service(admin_user)
        self.assertIn("message", result)
        self.assertIsInstance(result["data"], list)
        self.assertEqual(result["data"][0]["nombre_test"], "Test A")

    @patch("app.services.vocacion_usuario_service.get_db_session")
    def test_get_all_vocaciones_usuario_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("All vocaciones error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            get_all_vocaciones_usuario_service(admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "All vocaciones error")

if __name__ == '__main__':
    unittest.main()
