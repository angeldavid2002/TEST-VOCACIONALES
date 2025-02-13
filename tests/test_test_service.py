import unittest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from datetime import datetime, timezone

from fastapi import HTTPException
from app.services.test_service import (
    create_test_service,
    list_tests_service,
    get_test_by_id_service,
    delete_test_service,
    update_test_service,
)
from app.models.mdl_test import TestCreate
from app.config import config

# Dummy usuarios
admin_user = {"user_id": 1, "tipo_usuario": "admin"}
dummy_usuario = {"user_id": 2, "tipo_usuario": "comun"}  # usuario no admin

# Dummy test sin preguntas (para eliminación exitosa)
dummy_test = SimpleNamespace(
    id=100,
    nombre="Test 100",
    descripcion="Descripción del test",
    fecha_creacion=datetime(2025, 1, 1, tzinfo=timezone.utc),
    fecha_actualizacion=datetime(2025, 1, 1, tzinfo=timezone.utc)
)

# Dummy test con preguntas (para probar eliminación fallida)
dummy_test_with_questions = SimpleNamespace(
    id=101,
    nombre="Test con preguntas",
    descripcion="Descripción test con preguntas",
    fecha_creacion=datetime(2025, 1, 1, tzinfo=timezone.utc),
    fecha_actualizacion=datetime(2025, 1, 1, tzinfo=timezone.utc)
)

class TestTestService(unittest.TestCase):

    # --- Tests para create_test_service ---
    @patch("app.services.test_service.get_db_session")
    def test_create_test_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        def refresh_side_effect(instance):
            instance.id = dummy_test.id
        mock_session.refresh.side_effect = refresh_side_effect
        mock_get_db_session.return_value = iter([mock_session])
        
        test_data = TestCreate(
            nombre="Nuevo Test",
            descripcion="Descripción del nuevo test"
        )
        result = create_test_service(test_data, admin_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Test registrado exitosamente.")
        self.assertEqual(result["data"]["id"], dummy_test.id)
        mock_session.commit.assert_called_once()

    @patch("app.services.test_service.get_db_session")
    def test_create_test_service_not_admin(self, mock_get_db_session):
        test_data = TestCreate(
            nombre="Nuevo Test",
            descripcion="Descripción del nuevo test"
        )
        with self.assertRaises(HTTPException) as context:
            create_test_service(test_data, dummy_usuario)
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("No tiene los privilegios necesarios", context.exception.detail)

    @patch("app.services.test_service.get_db_session")
    def test_create_test_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.add.side_effect = Exception("Unexpected error")
        mock_get_db_session.return_value = iter([mock_session])
        test_data = TestCreate(
            nombre="Error Test",
            descripcion="Descripción Error Test"
        )
        with self.assertRaises(HTTPException) as context:
            create_test_service(test_data, admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Unexpected error")

    # --- Tests para list_tests_service ---
    @patch("app.services.test_service.get_db_session")
    def test_list_tests_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        dummy_test_detail = SimpleNamespace(
            id=100,
            nombre="Test 100",
            descripcion="Descripción test",
            fecha_creacion=datetime(2025, 1, 1, tzinfo=timezone.utc),
            fecha_actualizacion=datetime(2025, 1, 1, tzinfo=timezone.utc),
            total_preguntas=2
        )
        # Simular cadena de llamadas
        mock_query = MagicMock()
        mock_query.outerjoin.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [dummy_test_detail]
        mock_session.query.return_value = mock_query
        mock_get_db_session.return_value = iter([mock_session])
        result = list_tests_service()
        self.assertIsInstance(result, dict)
        self.assertIn("data", result)
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["id"], dummy_test_detail.id)
        self.assertEqual(result["data"][0]["total_preguntas"], dummy_test_detail.total_preguntas)

    @patch("app.services.test_service.get_db_session")
    def test_list_tests_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("List query error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            list_tests_service()
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "List query error")

    # --- Tests para get_test_by_id_service ---
    @patch("app.services.test_service.get_db_session")
    def test_get_test_by_id_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        dummy_test_detail = SimpleNamespace(
            id=100,
            nombre="Test 100",
            descripcion="Descripción test",
            fecha_creacion=datetime(2025, 1, 1, tzinfo=timezone.utc),
            fecha_actualizacion=datetime(2025, 1, 1, tzinfo=timezone.utc),
            total_preguntas=3
        )
        mock_query = MagicMock()
        mock_query.outerjoin.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.first.return_value = dummy_test_detail
        mock_session.query.return_value = mock_query
        mock_get_db_session.return_value = iter([mock_session])
        result = get_test_by_id_service(100)
        self.assertEqual(result["id"], dummy_test_detail.id)
        self.assertEqual(result["total_preguntas"], dummy_test_detail.total_preguntas)

    @patch("app.services.test_service.get_db_session")
    def test_get_test_by_id_service_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.outerjoin.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.first.return_value = None
        mock_session.query.return_value = mock_query
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            get_test_by_id_service(999)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Test no encontrado", context.exception.detail)

    @patch("app.services.test_service.get_db_session")
    def test_get_test_by_id_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Get test error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            get_test_by_id_service(100)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error al consultar el test", context.exception.detail)

    # --- Tests para delete_test_service ---
    @patch("app.services.test_service.get_db_session")
    def test_delete_test_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que el test existe y count() devuelve 0
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_test
        # Para la segunda llamada (Preguntas) configuramos count() como entero 0:
        def count_side_effect():
            return 0
        # Usamos side_effect en el método count de la segunda llamada:
        mock_session.query.return_value.filter.return_value.count.side_effect = count_side_effect
        mock_get_db_session.return_value = iter([mock_session])
        result = delete_test_service(100, admin_user)
        self.assertIn("message", result)
        self.assertIn("eliminado exitosamente", result["message"])
        mock_session.commit.assert_called_once()

    @patch("app.services.test_service.get_db_session")
    def test_delete_test_service_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            delete_test_service(100, dummy_usuario)
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.test_service.get_db_session")
    def test_delete_test_service_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            delete_test_service(999, admin_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("El test especificado no existe", context.exception.detail)

    @patch("app.services.test_service.get_db_session")
    def test_delete_test_service_with_questions(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_test_with_questions
        # Simular que count() devuelve 3 (preguntas asociadas)
        mock_session.query.return_value.filter.return_value.count.return_value = 3
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            delete_test_service(dummy_test_with_questions.id, admin_user)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("No se puede eliminar el test", context.exception.detail)

    @patch("app.services.test_service.get_db_session")
    def test_delete_test_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_test
        # Para que la validación de preguntas asociadas no interfiera, forzamos count() a devolver 0
        mock_session.query.return_value.filter.return_value.count.return_value = 0
        mock_session.delete.side_effect = Exception("Delete error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            delete_test_service(dummy_test.id, admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Delete error")

    # --- Tests para update_test_service ---
    @patch("app.services.test_service.get_db_session")
    def test_update_test_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        dummy_test_editable = SimpleNamespace(
            id=100,
            nombre="Test Original",
            descripcion="Descripción original",
            fecha_creacion=datetime(2025, 1, 1, tzinfo=timezone.utc),
            fecha_actualizacion=datetime(2025, 1, 1, tzinfo=timezone.utc)
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_test_editable
        mock_get_db_session.return_value = iter([mock_session])
        
        test_data = TestCreate(
            nombre="Test Actualizado",
            descripcion="Descripción actualizada"
        )
        result = update_test_service(100, test_data, admin_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Test actualizado exitosamente.")
        self.assertEqual(dummy_test_editable.nombre, "Test Actualizado")
        self.assertEqual(dummy_test_editable.descripcion, "Descripción actualizada")
        mock_session.commit.assert_called_once()

    @patch("app.services.test_service.get_db_session")
    def test_update_test_service_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            update_test_service(100, TestCreate(nombre="Test", descripcion="Desc"), dummy_usuario)
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.test_service.get_db_session")
    def test_update_test_service_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            update_test_service(999, TestCreate(nombre="Test", descripcion="Desc"), admin_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("El test especificado no existe", context.exception.detail)

    @patch("app.services.test_service.get_db_session")
    def test_update_test_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.side_effect = Exception("Update error")
        mock_get_db_session.return_value = iter([mock_session])
        with self.assertRaises(HTTPException) as context:
            update_test_service(100, TestCreate(nombre="Test", descripcion="Desc"), admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

if __name__ == '__main__':
    unittest.main()
