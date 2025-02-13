import unittest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from datetime import datetime, timezone

from fastapi import HTTPException
from app.services.respuesta_usuario_service import (
    list_respuestas_usuario,
    create_respuesta_usuario_service,
    update_respuesta_usuario_service,
    delete_respuestas_usuario_admin_service
)
from app.models.mdl_respuesta_usuario import RespuestaDeUsuarioCreate, RespuestaDeUsuarioUpdate
from app.config import config

# Dummy objetos para simular registros y relaciones
admin_user = {"user_id": 1, "tipo_usuario": "admin"}
dummy_usuario = {"user_id": 1, "tipo_usuario": "comun"}

dummy_respuesta_usuario = SimpleNamespace(
    id=10,
    test_id=1,
    pregunta_id=2,
    respuesta_id=3,
    usuario_id=1,
    # Simulamos la relación para join
    pregunta=SimpleNamespace(enunciado="¿Cuál es tu meta?"),
    respuesta=SimpleNamespace(respuesta="Ser feliz")
)

# Dummy para la creación de respuesta de usuario: simulamos que las entidades relacionadas existen
dummy_test = SimpleNamespace(id=1)
dummy_pregunta = SimpleNamespace(id=2, test_id=1)
dummy_respuesta = SimpleNamespace(id=3, pregunta_id=2)

class TestRespuestaUsuarioService(unittest.TestCase):

    # --- Tests para list_respuestas_usuario ---
    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_list_respuestas_usuario_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [dummy_respuesta_usuario]
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "comun"}
        result = list_respuestas_usuario(test_id=1, current_user=current_user)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["id"], dummy_respuesta_usuario.id)
        self.assertEqual(result[0]["enunciado_pregunta"], dummy_respuesta_usuario.pregunta.enunciado)
        self.assertEqual(result[0]["respuesta_texto"], dummy_respuesta_usuario.respuesta.respuesta)

    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_list_respuestas_usuario_not_authorized(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            list_respuestas_usuario(test_id=1, current_user=None)
        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("No está autorizado", context.exception.detail)

    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_list_respuestas_usuario_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "comun"}
        with self.assertRaises(HTTPException) as context:
            list_respuestas_usuario(test_id=1, current_user=current_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("No hay respuestas asociadas", context.exception.detail)

    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_list_respuestas_usuario_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Unexpected query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        current_user = {"user_id": 1, "tipo_usuario": "comun"}
        with self.assertRaises(HTTPException) as context:
            list_respuestas_usuario(test_id=1, current_user=current_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Unexpected query error")

    # --- Tests para create_respuesta_usuario_service ---
    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_create_respuesta_usuario_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que las entidades relacionadas existen: test, pregunta y respuesta
        mock_session.query.return_value.filter.return_value.first.side_effect = [dummy_test, dummy_pregunta, dummy_respuesta]
        # Simular asignación de id en refresh
        nueva_respuesta = SimpleNamespace(id=50)
        mock_session.add.side_effect = lambda x: setattr(x, "id", nueva_respuesta.id)
        mock_get_db_session.return_value = iter([mock_session])
        
        respuesta_data = RespuestaDeUsuarioCreate(
            test_id=1,
            pregunta_id=2,
            respuesta_id=3
        )
        result = create_respuesta_usuario_service(respuesta_data, admin_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Respuesta creada exitosamente.")
        self.assertEqual(result["data"]["id"], nueva_respuesta.id)
        mock_session.commit.assert_called_once()

    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_create_respuesta_usuario_service_entity_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que alguna entidad no existe (por ejemplo, la pregunta)
        mock_session.query.return_value.filter.return_value.first.side_effect = [dummy_test, None, dummy_respuesta]
        mock_get_db_session.return_value = iter([mock_session])
        
        respuesta_data = RespuestaDeUsuarioCreate(
            test_id=1,
            pregunta_id=999,  # pregunta inexistente
            respuesta_id=3
        )
        with self.assertRaises(HTTPException) as context:
            create_respuesta_usuario_service(respuesta_data, admin_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("El test, la pregunta o la respuesta no existen", context.exception.detail)

    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_create_respuesta_usuario_service_relationship_mismatch(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular entidades existentes pero con relaciones erróneas: la pregunta tiene test_id distinto al del test
        mismatched_pregunta = SimpleNamespace(id=2, test_id=999)
        mock_session.query.return_value.filter.return_value.first.side_effect = [dummy_test, mismatched_pregunta, dummy_respuesta]
        mock_get_db_session.return_value = iter([mock_session])
        
        respuesta_data = RespuestaDeUsuarioCreate(
            test_id=1,
            pregunta_id=2,
            respuesta_id=3
        )
        with self.assertRaises(HTTPException) as context:
            create_respuesta_usuario_service(respuesta_data, admin_user)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Los IDs proporcionados no están relacionados entre sí", context.exception.detail)

    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_create_respuesta_usuario_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.side_effect = Exception("Unexpected error")
        mock_get_db_session.return_value = iter([mock_session])
        
        respuesta_data = RespuestaDeUsuarioCreate(
            test_id=1,
            pregunta_id=2,
            respuesta_id=3
        )
        with self.assertRaises(HTTPException) as context:
            create_respuesta_usuario_service(respuesta_data, admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Unexpected error")

    # --- Tests para update_respuesta_usuario_service ---
    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_update_respuesta_usuario_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        dummy_respuesta_usuario = SimpleNamespace(
            id=30,
            test_id=1,
            pregunta_id=2,
            respuesta_id=3,
            usuario_id=1
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_respuesta_usuario
        mock_get_db_session.return_value = iter([mock_session])
        
        update_data = RespuestaDeUsuarioUpdate(
            pregunta_id=2,
            respuesta_id=99
        )
        result = update_respuesta_usuario_service(update_data, test_id=1, current_user=admin_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Respuesta actualizada exitosamente.")
        self.assertEqual(dummy_respuesta_usuario.respuesta_id, 99)
        mock_session.commit.assert_called_once()

    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_update_respuesta_usuario_service_not_authorized(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            update_respuesta_usuario_service(RespuestaDeUsuarioUpdate(pregunta_id=2, respuesta_id=99), test_id=1, current_user=None)
        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("No está autorizado", context.exception.detail)

    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_update_respuesta_usuario_service_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        update_data = RespuestaDeUsuarioUpdate(pregunta_id=2, respuesta_id=99)
        with self.assertRaises(HTTPException) as context:
            update_respuesta_usuario_service(update_data, test_id=1, current_user=admin_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("No se encontró la respuesta de usuario", context.exception.detail)

    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_update_respuesta_usuario_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.side_effect = Exception("Update error")
        mock_get_db_session.return_value = iter([mock_session])
        
        update_data = RespuestaDeUsuarioUpdate(pregunta_id=2, respuesta_id=99)
        with self.assertRaises(HTTPException) as context:
            update_respuesta_usuario_service(update_data, test_id=1, current_user=admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Update error")

    # --- Tests para delete_respuestas_usuario_admin_service ---
    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_delete_respuestas_usuario_admin_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        dummy_respuestas = [SimpleNamespace(id=40), SimpleNamespace(id=41)]
        mock_session.query.return_value.filter.return_value.all.return_value = dummy_respuestas
        mock_get_db_session.return_value = iter([mock_session])
        
        result = delete_respuestas_usuario_admin_service(test_id=1, current_user=admin_user)
        self.assertIn("message", result)
        self.assertIn("eliminadas exitosamente", result["message"])
        mock_session.commit.assert_called_once()

    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_delete_respuestas_usuario_admin_service_not_admin(self, mock_get_db_session):
        dummy_usuario = {"user_id": 1, "tipo_usuario": "comun"}
        with self.assertRaises(HTTPException) as context:
            delete_respuestas_usuario_admin_service(test_id=1, current_user=dummy_usuario)
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("No tiene privilegios", context.exception.detail)

    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_delete_respuestas_usuario_admin_service_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_respuestas_usuario_admin_service(test_id=999, current_user=admin_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("No hay respuestas asociadas", context.exception.detail)

    @patch("app.services.respuesta_usuario_service.get_db_session")
    def test_delete_respuestas_usuario_admin_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.side_effect = Exception("Delete admin error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_respuestas_usuario_admin_service(test_id=1, current_user=admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Delete admin error")

if __name__ == '__main__':
    unittest.main()
