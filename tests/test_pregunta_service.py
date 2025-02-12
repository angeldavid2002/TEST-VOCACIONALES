import unittest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from datetime import datetime, timezone

from fastapi import HTTPException
from app.services.pregunta_service import (
    list_preguntas_by_test,
    search_pregunta_by_id,
    create_pregunta_service,
    update_pregunta_service,
    delete_pregunta_service
)
from app.models.mdl_pregunta import PreguntaCreate, PreguntaUpdate
from app.config import config

# Dummy objetos para simular registros en la base de datos
dummy_test = SimpleNamespace(id=1, nombre="Test 1")
dummy_pregunta = SimpleNamespace(id=10, test_id=1, enunciado="¿Cuál es tu meta?")
dummy_pregunta_with_respuestas = SimpleNamespace(
    id=20,
    test_id=1,
    enunciado="Pregunta con respuestas",
    respuestas=[{"id": 101}, {"id": 102}]
)

class TestPreguntaService(unittest.TestCase):

    @patch("app.services.pregunta_service.get_db_session")
    def test_list_preguntas_by_test_success(self, mock_get_db_session):
        # Configurar mock de sesión
        mock_session = MagicMock()
        # Simular que el test existe
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_test
        # Simular que se encuentran preguntas
        mock_session.query.return_value.filter.return_value.all.return_value = [dummy_pregunta]
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        result = list_preguntas_by_test(1, current_user)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["id"], dummy_pregunta.id)
        self.assertEqual(result[0]["enunciado"], dummy_pregunta.enunciado)

    @patch("app.services.pregunta_service.get_db_session")
    def test_list_preguntas_by_test_test_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que el test no existe
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        with self.assertRaises(HTTPException) as context:
            list_preguntas_by_test(999, current_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("El test especificado no existe", context.exception.detail)

    @patch("app.services.pregunta_service.get_db_session")
    def test_list_preguntas_by_test_no_questions(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que el test existe
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_test
        # Simular que no se encuentran preguntas
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        with self.assertRaises(HTTPException) as context:
            list_preguntas_by_test(1, current_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("No se encontraron preguntas para este test", context.exception.detail)

    def test_list_preguntas_by_test_not_authorized(self):
        # Si current_user es None se debe lanzar 401
        with self.assertRaises(HTTPException) as context:
            list_preguntas_by_test(1, None)
        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("No está autorizado", context.exception.detail)

    @patch("app.services.pregunta_service.get_db_session")
    def test_list_preguntas_by_test_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular excepción inesperada
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        with self.assertRaises(HTTPException) as context:
            list_preguntas_by_test(1, current_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.pregunta_service.get_db_session")
    def test_search_pregunta_by_id_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_pregunta
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        result = search_pregunta_by_id(10, current_user)
        self.assertIn("data", result)
        self.assertEqual(result["data"]["id"], dummy_pregunta.id)
        self.assertEqual(result["data"]["test_id"], dummy_pregunta.test_id)
        self.assertEqual(result["data"]["enunciado"], dummy_pregunta.enunciado)

    @patch("app.services.pregunta_service.get_db_session")
    def test_search_pregunta_by_id_not_authorized(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            search_pregunta_by_id(10, None)
        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("No está autorizado", context.exception.detail)

    @patch("app.services.pregunta_service.get_db_session")
    def test_search_pregunta_by_id_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        with self.assertRaises(HTTPException) as context:
            search_pregunta_by_id(999, current_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("La pregunta especificada no existe", context.exception.detail)

    @patch("app.services.pregunta_service.get_db_session")
    def test_search_pregunta_by_id_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        with self.assertRaises(HTTPException) as context:
            search_pregunta_by_id(10, current_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.pregunta_service.get_db_session")
    def test_create_pregunta_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que el test existe
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_test
        # Simular asignación de id a la nueva pregunta
        nueva_pregunta = SimpleNamespace(id=100, test_id=dummy_test.id, enunciado="Nueva pregunta")
        mock_session.add.side_effect = lambda x: setattr(x, "id", nueva_pregunta.id)
        mock_get_db_session.return_value = iter([mock_session])
        
        pregunta_data = PreguntaCreate(
            test_id=1,
            enunciado="Nueva pregunta"
        )
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        result = create_pregunta_service(pregunta_data, current_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Pregunta creada exitosamente.")
        self.assertEqual(result["data"]["id"], nueva_pregunta.id)
        mock_session.commit.assert_called_once()

    @patch("app.services.pregunta_service.get_db_session")
    def test_create_pregunta_service_not_admin(self, mock_get_db_session):
        current_user = {"user_id": 1, "tipo_usuario": "comun"}
        with self.assertRaises(HTTPException) as context:
            create_pregunta_service(PreguntaCreate(test_id=1, enunciado="Pregunta"), current_user)
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.pregunta_service.get_db_session")
    def test_create_pregunta_service_test_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que el test no existe
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        with self.assertRaises(HTTPException) as context:
            create_pregunta_service(PreguntaCreate(test_id=999, enunciado="Pregunta"), current_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("El test especificado no existe", context.exception.detail)

    @patch("app.services.pregunta_service.get_db_session")
    def test_create_pregunta_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.side_effect = Exception("Unexpected error")
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        with self.assertRaises(HTTPException) as context:
            create_pregunta_service(PreguntaCreate(test_id=1, enunciado="Pregunta"), current_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.pregunta_service.get_db_session")
    def test_update_pregunta_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la pregunta existe
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_pregunta
        mock_get_db_session.return_value = iter([mock_session])
        
        update_data = PreguntaUpdate(enunciado="Pregunta actualizada")
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        result = update_pregunta_service(update_data, dummy_pregunta.id, current_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Pregunta actualizada exitosamente.")
        # Verificar que el enunciado se actualizó
        self.assertEqual(dummy_pregunta.enunciado, "Pregunta actualizada")
        mock_session.commit.assert_called_once()

    @patch("app.services.pregunta_service.get_db_session")
    def test_update_pregunta_service_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            update_pregunta_service(PreguntaUpdate(enunciado="New text"), dummy_pregunta.id, {"user_id": 1, "tipo_usuario": "comun"})
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.pregunta_service.get_db_session")
    def test_update_pregunta_service_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la pregunta no se encuentra
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        with self.assertRaises(HTTPException) as context:
            update_pregunta_service(PreguntaUpdate(enunciado="Updated"), 999, current_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("La pregunta especificada no existe", context.exception.detail)

    @patch("app.services.pregunta_service.get_db_session")
    def test_update_pregunta_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        with self.assertRaises(HTTPException) as context:
            update_pregunta_service(PreguntaUpdate(enunciado="Updated"), dummy_pregunta.id, current_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.pregunta_service.get_db_session")
    def test_delete_pregunta_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la pregunta existe y no tiene respuestas asociadas
        dummy_pregunta_no_respuestas = SimpleNamespace(
            id=30,
            test_id=1,
            enunciado="Pregunta sin respuestas",
            respuestas=[]
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_pregunta_no_respuestas
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        result = delete_pregunta_service(30, current_user)
        self.assertIn("message", result)
        self.assertIn("eliminada exitosamente", result["message"])
        mock_session.commit.assert_called_once()

    @patch("app.services.pregunta_service.get_db_session")
    def test_delete_pregunta_service_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la pregunta no se encuentra
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        with self.assertRaises(HTTPException) as context:
            delete_pregunta_service(999, current_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("La pregunta especificada no existe", context.exception.detail)

    @patch("app.services.pregunta_service.get_db_session")
    def test_delete_pregunta_service_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            delete_pregunta_service(dummy_pregunta.id, {"user_id": 1, "tipo_usuario": "comun"})
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.pregunta_service.get_db_session")
    def test_delete_pregunta_service_with_respuestas(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la pregunta tiene respuestas asociadas
        dummy_pregunta_with_answers = SimpleNamespace(
            id=40,
            test_id=1,
            enunciado="Pregunta con respuestas",
            respuestas=[{"id": 101}]
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_pregunta_with_answers
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        with self.assertRaises(HTTPException) as context:
            delete_pregunta_service(40, current_user)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("No se puede eliminar la pregunta", context.exception.detail)

    @patch("app.services.pregunta_service.get_db_session")
    def test_delete_pregunta_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_pregunta
        mock_session.delete.side_effect = Exception("Delete error")
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        with self.assertRaises(HTTPException) as context:
            delete_pregunta_service(dummy_pregunta.id, current_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)
