import unittest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from datetime import datetime, timezone

from fastapi import HTTPException
from app.services.respuesta_service import (
    list_respuestas_by_pregunta,
    search_respuesta_by_id,
    create_respuesta_service,
    update_respuesta_service,
    delete_respuesta_service
)
from app.models.mdl_respuesta import RespuestaCreate, RespuestaUpdate
from app.config import config

# Dummy objetos para simular registros en la base de datos

# Dummy pregunta para verificar existencia en list_respuestas_by_pregunta y create_respuesta_service
dummy_pregunta = SimpleNamespace(id=1)

# Dummy respuesta sin asociaciones (para eliminar)
dummy_respuesta = SimpleNamespace(
    id=10,
    pregunta_id=1,
    respuesta="Respuesta de prueba",
    vocacion="Vocación 1",
    # Simular que no tiene asociaciones
    respuestas_de_usuario=[]
)

# Dummy respuesta para join en search, list, etc. con atributo nombre_usuario
dummy_respuesta_with_usuario = SimpleNamespace(
    id=10,
    pregunta_id=1,
    respuesta="Respuesta de prueba",
    vocacion="Vocación 1",
    nombre_usuario="Usuario Test"
)

# Dummy current_user para admin y usuario común
admin_user = {"tipo_usuario": "admin", "user_id": 1}
dummy_user = {"tipo_usuario": "comun", "user_id": 1}

class TestRespuestaService(unittest.TestCase):

    # --- Tests para list_respuestas_by_pregunta ---
    @patch("app.services.respuesta_service.get_db_session")
    def test_list_respuestas_by_pregunta_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la pregunta existe
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_pregunta
        # Simular que se encuentran respuestas
        mock_session.query.return_value.filter.return_value.all.return_value = [dummy_respuesta_with_usuario]
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "comun"}
        result = list_respuestas_by_pregunta(1, current_user)
        self.assertIsInstance(result, dict)
        self.assertIn("data", result)
        self.assertEqual(result["data"][0]["id"], dummy_respuesta_with_usuario.id)

    @patch("app.services.respuesta_service.get_db_session")
    def test_list_respuestas_by_pregunta_not_authorized(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            list_respuestas_by_pregunta(1, None)
        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("No está autorizado", context.exception.detail)

    @patch("app.services.respuesta_service.get_db_session")
    def test_list_respuestas_by_pregunta_question_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la pregunta no existe
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "comun"}
        with self.assertRaises(HTTPException) as context:
            list_respuestas_by_pregunta(999, current_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("La pregunta especificada no existe", context.exception.detail)

    @patch("app.services.respuesta_service.get_db_session")
    def test_list_respuestas_by_pregunta_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "comun"}
        with self.assertRaises(HTTPException) as context:
            list_respuestas_by_pregunta(1, current_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")

    # --- Tests para search_respuesta_by_id ---
    @patch("app.services.respuesta_service.get_db_session")
    def test_search_respuesta_by_id_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_respuesta
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "comun"}
        result = search_respuesta_by_id(10, current_user)
        self.assertIn("data", result)
        self.assertEqual(result["data"]["id"], dummy_respuesta.id)
        self.assertEqual(result["data"]["pregunta_id"], dummy_respuesta.pregunta_id)
        self.assertEqual(result["data"]["respuesta"], dummy_respuesta.respuesta)

    @patch("app.services.respuesta_service.get_db_session")
    def test_search_respuesta_by_id_not_authorized(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            search_respuesta_by_id(10, None)
        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("No está autorizado", context.exception.detail)

    @patch("app.services.respuesta_service.get_db_session")
    def test_search_respuesta_by_id_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "comun"}
        with self.assertRaises(HTTPException) as context:
            search_respuesta_by_id(999, current_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("La respuesta especificada no existe", context.exception.detail)

    @patch("app.services.respuesta_service.get_db_session")
    def test_search_respuesta_by_id_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "comun"}
        with self.assertRaises(HTTPException) as context:
            search_respuesta_by_id(10, current_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")

    # --- Tests para create_respuesta_service ---
    @patch("app.services.respuesta_service.get_db_session")
    def test_create_respuesta_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la pregunta existe
        dummy_question = SimpleNamespace(id=1)
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_question
        # Simular que se asigna un id a la nueva respuesta
        nueva_respuesta = SimpleNamespace(id=50)
        mock_session.add.side_effect = lambda x: setattr(x, "id", nueva_respuesta.id)
        mock_get_db_session.return_value = iter([mock_session])
        
        respuesta_data = RespuestaCreate(
            pregunta_id=1,
            respuesta="Respuesta nueva",
            vocacion="Vocación A"
        )
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        result = create_respuesta_service(respuesta_data, current_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Respuesta creada exitosamente.")
        self.assertEqual(result["data"]["id"], nueva_respuesta.id)
        mock_session.commit.assert_called_once()

    @patch("app.services.respuesta_service.get_db_session")
    def test_create_respuesta_service_not_admin(self, mock_get_db_session):
        respuesta_data = RespuestaCreate(
            pregunta_id=1,
            respuesta="Respuesta nueva",
            vocacion="Vocación A"
        )
        with self.assertRaises(HTTPException) as context:
            create_respuesta_service(respuesta_data, {"user_id": 1, "tipo_usuario": "comun"})
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("No tiene los privilegios", context.exception.detail)

    @patch("app.services.respuesta_service.get_db_session")
    def test_create_respuesta_service_question_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la pregunta no existe
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        respuesta_data = RespuestaCreate(
            pregunta_id=999,
            respuesta="Respuesta nueva",
            vocacion="Vocación A"
        )
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        with self.assertRaises(HTTPException) as context:
            create_respuesta_service(respuesta_data, current_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("La pregunta especificada no existe", context.exception.detail)

    @patch("app.services.respuesta_service.get_db_session")
    def test_create_respuesta_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.side_effect = Exception("Unexpected error")
        mock_get_db_session.return_value = iter([mock_session])
        
        respuesta_data = RespuestaCreate(
            pregunta_id=1,
            respuesta="Respuesta nueva",
            vocacion="Vocación A"
        )
        with self.assertRaises(HTTPException) as context:
            create_respuesta_service(respuesta_data, {"user_id": 1, "tipo_usuario": "admin"})
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Unexpected error")

    # --- Tests para update_respuesta_service ---
    @patch("app.services.respuesta_service.get_db_session")
    def test_update_respuesta_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        dummy_respuesta_editable = SimpleNamespace(
            id=20,
            pregunta_id=1,
            respuesta="Respuesta original",
            vocacion="Vocación B"
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_respuesta_editable
        mock_get_db_session.return_value = iter([mock_session])
        
        update_data = RespuestaUpdate(
            respuesta="Respuesta actualizada",
            vocacion="Vocación Actualizada"
        )
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        result = update_respuesta_service(update_data, dummy_respuesta_editable.id, current_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Respuesta actualizada exitosamente.")
        self.assertEqual(dummy_respuesta_editable.respuesta, "Respuesta actualizada")
        self.assertEqual(dummy_respuesta_editable.vocacion, "Vocación Actualizada")
        mock_session.commit.assert_called_once()

    @patch("app.services.respuesta_service.get_db_session")
    def test_update_respuesta_service_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            update_respuesta_service(RespuestaUpdate(respuesta="Test"), 20, {"user_id": 1, "tipo_usuario": "comun"})
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("No tiene los privilegios", context.exception.detail)

    @patch("app.services.respuesta_service.get_db_session")
    def test_update_respuesta_service_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            update_respuesta_service(RespuestaUpdate(respuesta="Updated"), 999, {"user_id": 1, "tipo_usuario": "admin"})
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("La respuesta especificada no existe", context.exception.detail)

    @patch("app.services.respuesta_service.get_db_session")
    def test_update_respuesta_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            update_respuesta_service(RespuestaUpdate(respuesta="Updated"), 20, {"user_id": 1, "tipo_usuario": "admin"})
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")

    # --- Tests para delete_respuesta_service ---
    @patch("app.services.respuesta_service.get_db_session")
    def test_delete_respuesta_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la respuesta existe y no tiene asociaciones de respuesta de usuario
        dummy_respuesta_to_delete = SimpleNamespace(
            id=30,
            pregunta_id=1,
            respuesta="Respuesta a eliminar",
            vocacion="Vocación X",
            respuestas_de_usuario=[]
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_respuesta_to_delete
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "admin"}
        result = delete_respuesta_service(30, current_user)
        self.assertIn("message", result)
        self.assertIn("eliminada exitosamente", result["message"])
        mock_session.commit.assert_called_once()

    @patch("app.services.respuesta_service.get_db_session")
    def test_delete_respuesta_service_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_respuesta_service(999, {"user_id": 1, "tipo_usuario": "admin"})
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("La respuesta especificada no existe", context.exception.detail)

    @patch("app.services.respuesta_service.get_db_session")
    def test_delete_respuesta_service_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            delete_respuesta_service(dummy_respuesta.id, {"user_id": 1, "tipo_usuario": "comun"})
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("No tiene los privilegios", context.exception.detail)

    @patch("app.services.respuesta_service.get_db_session")
    def test_delete_respuesta_service_with_associations(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la respuesta tiene asociaciones (no se puede eliminar)
        dummy_respuesta_with_assoc = SimpleNamespace(
            id=40,
            pregunta_id=1,
            respuesta="Respuesta con asociaciones",
            vocacion="Vocación Y",
            respuestas_de_usuario=[{"id": 101}]
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_respuesta_with_assoc
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_respuesta_service(40, {"user_id": 1, "tipo_usuario": "admin"})
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("No se puede eliminar la respuesta", context.exception.detail)

    @patch("app.services.respuesta_service.get_db_session")
    def test_delete_respuesta_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_respuesta
        mock_session.delete.side_effect = Exception("Delete error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_respuesta_service(dummy_respuesta.id, {"user_id": 1, "tipo_usuario": "admin"})
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Delete error")
