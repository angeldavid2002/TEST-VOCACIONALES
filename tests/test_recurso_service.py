import unittest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace

from fastapi import HTTPException
from sqlalchemy import func

from app.services.recurso_service import (
    register_recurso_service,
    edit_recurso_service,
    delete_recurso_service,
    list_recursos_service,
    get_total_recursos,
)
from app.models.mdl_recurso import RecursoCreate, RecursoUpdate
from app.config import config

# Objeto dummy para simular un recurso existente
dummy_recurso = SimpleNamespace(
    id=100,
    nombre="Recurso Dummy",
    tipo="Tutorial",
    autor="Autor Dummy",
    plataforma="Plataforma X",
    enlace="http://dummy.com"
)

# Dummy current_user para administrador y para usuario no admin
admin_user = {"tipo_usuario": "admin"}
non_admin_user = {"tipo_usuario": "comun"}

class TestRecursoService(unittest.TestCase):

    @patch("app.services.recurso_service.get_db_session")
    def test_register_recurso_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que al agregar el recurso y refrescarlo se le asigna un id
        # Usamos side_effect en refresh para asignar dummy id
        def refresh_side_effect(instance):
            instance.id = dummy_recurso.id
        mock_session.refresh.side_effect = refresh_side_effect
        mock_get_db_session.return_value = iter([mock_session])
        
        recurso_data = RecursoCreate(
            nombre="Nuevo Recurso",
            tipo="Tutorial",
            autor="Nuevo Autor",
            plataforma="Plataforma Y",
            enlace="http://nuevorecurso.com"
        )
        result = register_recurso_service(recurso_data, admin_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Recurso registrado exitosamente")
        self.assertEqual(result["id"], dummy_recurso.id)
        mock_session.commit.assert_called_once()

    @patch("app.services.recurso_service.get_db_session")
    def test_register_recurso_not_admin(self, mock_get_db_session):
        recurso_data = RecursoCreate(
            nombre="Nuevo Recurso",
            tipo="Tutorial",
            autor="Nuevo Autor",
            plataforma="Plataforma Y",
            enlace="http://nuevorecurso.com"
        )
        with self.assertRaises(HTTPException) as context:
            register_recurso_service(recurso_data, non_admin_user)
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("No tiene los privilegios", context.exception.detail)

    @patch("app.services.recurso_service.get_db_session")
    def test_register_recurso_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.add.side_effect = Exception("Unexpected error")
        mock_get_db_session.return_value = iter([mock_session])
        
        recurso_data = RecursoCreate(
            nombre="Error Recurso",
            tipo="Tutorial",
            autor="Error Autor",
            plataforma="Plataforma Z",
            enlace="http://error.com"
        )
        with self.assertRaises(HTTPException) as context:
            register_recurso_service(recurso_data, admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.recurso_service.get_db_session")
    def test_edit_recurso_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que se encuentra el recurso existente
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_recurso
        mock_get_db_session.return_value = iter([mock_session])
        
        update_data = RecursoUpdate(
            nombre="Recurso Actualizado",
            tipo="Curso",
            autor="Autor Actualizado",
            plataforma="Plataforma Actualizada",
            enlace="http://actualizado.com"
        )
        result = edit_recurso_service(dummy_recurso.id, update_data, admin_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Recurso actualizado exitosamente")
        self.assertEqual(dummy_recurso.nombre, "Recurso Actualizado")
        self.assertEqual(dummy_recurso.tipo, "Curso")
        self.assertEqual(dummy_recurso.autor, "Autor Actualizado")
        self.assertEqual(dummy_recurso.plataforma, "Plataforma Actualizada")
        self.assertEqual(dummy_recurso.enlace, "http://actualizado.com")
        mock_session.commit.assert_called_once()

    @patch("app.services.recurso_service.get_db_session")
    def test_edit_recurso_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que no se encuentra el recurso
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        update_data = RecursoUpdate(nombre="Nuevo Nombre")
        with self.assertRaises(HTTPException) as context:
            edit_recurso_service(999, update_data, admin_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Recurso no encontrado", context.exception.detail)

    @patch("app.services.recurso_service.get_db_session")
    def test_edit_recurso_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            edit_recurso_service(dummy_recurso.id, RecursoUpdate(nombre="Test"), non_admin_user)
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("No tiene los privilegios", context.exception.detail)

    @patch("app.services.recurso_service.get_db_session")
    def test_edit_recurso_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            edit_recurso_service(dummy_recurso.id, RecursoUpdate(nombre="Test"), admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.recurso_service.get_db_session")
    def test_delete_recurso_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que el recurso existe
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_recurso
        mock_get_db_session.return_value = iter([mock_session])
        
        result = delete_recurso_service(dummy_recurso.id, admin_user)
        self.assertIn("message", result)
        self.assertIn("eliminado exitosamente", result["message"])
        mock_session.commit.assert_called_once()

    @patch("app.services.recurso_service.get_db_session")
    def test_delete_recurso_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que no se encuentra el recurso
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_recurso_service(999, admin_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Recurso no encontrado", context.exception.detail)

    @patch("app.services.recurso_service.get_db_session")
    def test_delete_recurso_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            delete_recurso_service(dummy_recurso.id, non_admin_user)
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("No tiene los privilegios", context.exception.detail)

    @patch("app.services.recurso_service.get_db_session")
    def test_delete_recurso_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que se encuentra el recurso
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_recurso
        # Forzar excepción en delete o commit
        mock_session.delete.side_effect = Exception("Delete error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_recurso_service(dummy_recurso.id, admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.recurso_service.get_db_session")
    def test_list_recursos_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que existen dos recursos
        dummy_recurso2 = SimpleNamespace(
            id=200,
            nombre="Recurso 2",
            tipo="Curso",
            autor="Autor 2",
            plataforma="Plataforma 2",
            enlace="http://recurso2.com"
        )
        mock_session.query.return_value.all.return_value = [dummy_recurso, dummy_recurso2]
        mock_get_db_session.return_value = iter([mock_session])
        
        result = list_recursos_service()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].nombre, dummy_recurso.nombre)
        self.assertEqual(result[1].nombre, dummy_recurso2.nombre)

    @patch("app.services.recurso_service.get_db_session")
    def test_list_recursos_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            list_recursos_service()
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.recurso_service.get_db_session")
    def test_get_total_recursos_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que el count devuelve 5
        mock_session.query.return_value.filter.return_value = None  # No se utiliza en este caso
        mock_session.query.return_value.scalar.return_value = 5
        mock_get_db_session.return_value = iter([mock_session])
        
        result = get_total_recursos()
        self.assertIn("total_recursos", result)
        self.assertEqual(result["total_recursos"], 5)

    @patch("app.services.recurso_service.get_db_session")
    def test_get_total_recursos_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Count error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            get_total_recursos()
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)
