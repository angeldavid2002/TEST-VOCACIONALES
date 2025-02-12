import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi import HTTPException
from app.services.institucion_service import (
    register_institucion_service,
    update_institucion_service,
    delete_institucion_service,
    list_instituciones_service
)
from app.models.mdl_institucion import InstitucionCreate, InstitucionUpdate
from app.config import config

# Objeto dummy para simular una institución existente (para update, delete y list)
dummy_institution = SimpleNamespace(
    id=1,
    nombre="Dummy Institution",
    direccion="Calle Falsa 123",
    telefono="1234567890",
    # Simulamos que no tiene usuarios asociados (lista vacía)
    usuarios=[]
)

# Dummy current_user para administrador y para usuario no admin
admin_user = {"tipo_usuario": "admin"}
non_admin_user = {"tipo_usuario": "comun"}

class TestInstitucionService(unittest.TestCase):

    @patch("app.services.institucion_service.get_db_session")
    def test_register_institucion_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que no existe una institución con ese nombre
        mock_session.query.return_value.filter.return_value.first.return_value = None
        # Simular que se asigna un id a la nueva institución al refrescarla
        dummy_new_inst = SimpleNamespace(id=10)
        mock_session.refresh.side_effect = lambda inst: setattr(inst, "id", dummy_new_inst.id)
        mock_get_db_session.return_value = iter([mock_session])
        
        inst_data = InstitucionCreate(
            nombre="New Institution",
            direccion="Av. Siempre Viva 123",
            telefono="555-1234"
        )
        result = register_institucion_service(inst_data, admin_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Institución registrada exitosamente")
        self.assertEqual(result["id"], dummy_new_inst.id)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch("app.services.institucion_service.get_db_session")
    def test_register_institucion_already_exists(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que ya existe una institución con ese nombre
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_institution
        mock_get_db_session.return_value = iter([mock_session])
        
        inst_data = InstitucionCreate(
            nombre="Dummy Institution",  # Nombre ya existente
            direccion="Otra dirección",
            telefono="000-0000"
        )
        with self.assertRaises(HTTPException) as context:
            register_institucion_service(inst_data, admin_user)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Ya existe una institución con el nombre", context.exception.detail)

    @patch("app.services.institucion_service.get_db_session")
    def test_register_institucion_not_admin(self, mock_get_db_session):
        inst_data = InstitucionCreate(
            nombre="New Institution",
            direccion="Av. Siempre Viva 123",
            telefono="555-1234"
        )
        with self.assertRaises(HTTPException) as context:
            register_institucion_service(inst_data, non_admin_user)
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("No tiene los privilegios", context.exception.detail)

    @patch("app.services.institucion_service.get_db_session")
    def test_register_institucion_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        # Forzar que first() lance una excepción inesperada
        mock_session.query.return_value.filter.return_value.first.side_effect = Exception("Unexpected error")
        mock_get_db_session.return_value = iter([mock_session])
        
        inst_data = InstitucionCreate(
            nombre="Error Institution",
            direccion="Error Street",
            telefono="000-0000"
        )
        with self.assertRaises(HTTPException) as context:
            register_institucion_service(inst_data, admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.institucion_service.get_db_session")
    def test_update_institucion_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la institución existe
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_institution
        mock_get_db_session.return_value = iter([mock_session])
        
        update_data = InstitucionUpdate(
            nombre="Updated Institution",
            direccion="Nueva dirección",
            telefono="111-2222"
        )
        result = update_institucion_service(1, update_data, admin_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Institución actualizada exitosamente")
        # Verificar que los campos se hayan actualizado
        self.assertEqual(dummy_institution.nombre, "Updated Institution")
        self.assertEqual(dummy_institution.direccion, "Nueva dirección")
        self.assertEqual(dummy_institution.telefono, "111-2222")
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch("app.services.institucion_service.get_db_session")
    def test_update_institucion_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que no se encuentra la institución
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        update_data = InstitucionUpdate(
            nombre="Updated Institution"
        )
        with self.assertRaises(HTTPException) as context:
            update_institucion_service(999, update_data, admin_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("No se encontró la institución con ID 999", context.exception.detail)

    @patch("app.services.institucion_service.get_db_session")
    def test_update_institucion_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            update_institucion_service(1, InstitucionUpdate(nombre="Updated Institution"), non_admin_user)
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("No tiene los privilegios", context.exception.detail)

    @patch("app.services.institucion_service.get_db_session")
    def test_update_institucion_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la institución existe
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_institution
        # Simular error durante commit
        mock_session.commit.side_effect = Exception("Commit error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            update_institucion_service(1, InstitucionUpdate(nombre="Fail Institution"), admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.institucion_service.get_db_session")
    def test_delete_institucion_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la institución existe y no tiene usuarios asociados
        dummy_institution_no_users = SimpleNamespace(
            id=1,
            nombre="Dummy Institution",
            direccion="Calle Falsa 123",
            telefono="1234567890",
            usuarios=[]  # Sin usuarios asociados
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_institution_no_users
        mock_get_db_session.return_value = iter([mock_session])
        
        result = delete_institucion_service(1, admin_user)
        self.assertIn("message", result)
        self.assertIn("eliminada exitosamente", result["message"])
        mock_session.commit.assert_called_once()

    @patch("app.services.institucion_service.get_db_session")
    def test_delete_institucion_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que no se encuentra la institución
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_institucion_service(999, admin_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("No se encontró la institución con ID 999", context.exception.detail)

    @patch("app.services.institucion_service.get_db_session")
    def test_delete_institucion_not_admin(self, mock_get_db_session):
        with self.assertRaises(HTTPException) as context:
            delete_institucion_service(1, non_admin_user)
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("No tiene los privilegios", context.exception.detail)

    @patch("app.services.institucion_service.get_db_session")
    def test_delete_institucion_with_users(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la institución existe pero tiene usuarios asociados
        dummy_institution_with_users = SimpleNamespace(
            id=1,
            nombre="Dummy Institution",
            direccion="Calle Falsa 123",
            telefono="1234567890",
            usuarios=[{"id": 10}]  # Tiene al menos un usuario asociado
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_institution_with_users
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_institucion_service(1, admin_user)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("No se puede eliminar la institución", context.exception.detail)

    @patch("app.services.institucion_service.get_db_session")
    def test_delete_institucion_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que la institución existe sin usuarios
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_institution
        # Simular que delete lanza una excepción
        mock_session.delete.side_effect = Exception("Delete error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_institucion_service(1, admin_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)

    @patch("app.services.institucion_service.get_db_session")
    def test_list_instituciones_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que hay dos instituciones en la base de datos
        dummy_inst2 = SimpleNamespace(
            id=2,
            nombre="Another Institution",
            direccion="Av. Principal 456",
            telefono="9876543210"
        )
        mock_session.query.return_value.all.return_value = [dummy_institution, dummy_inst2]
        mock_get_db_session.return_value = iter([mock_session])
        
        result = list_instituciones_service()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["total"], 2)
        self.assertEqual(len(result["instituciones"]), 2)
        self.assertEqual(result["instituciones"][0]["nombre"], dummy_institution.nombre)
        self.assertEqual(result["instituciones"][1]["nombre"], dummy_inst2.nombre)

    @patch("app.services.institucion_service.get_db_session")
    def test_list_instituciones_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            list_instituciones_service()
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Error interno", context.exception.detail)
