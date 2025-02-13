import unittest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from datetime import datetime, timezone

from fastapi import HTTPException
from pydantic import ValidationError

from app.services.resena_service import (
    create_resena_service,
    get_resenas_paginated_desc_service,
    get_resenas_paginated_asc_service,
    get_resenas_by_rating_service,
    get_resenas_by_user_id_service,
    get_average_rating_service,
    edit_resena_service,
    delete_resena_service
)
from app.models.mdl_resena import ResenaCreate
from app.config import config

# Dummy objetos para simular registros en la base de datos
dummy_resena = SimpleNamespace(
    id=10,
    id_usuario=1,
    comentario="Esta es una reseña",
    puntuacion=4,
    fecha_creacion=datetime(2025, 1, 1, tzinfo=timezone.utc)
)

# Dummy para join: simulamos que al unir con Usuario, obtenemos un nombre de usuario
dummy_resena_with_usuario = SimpleNamespace(
    id=10,
    comentario="Esta es una reseña",
    puntuacion=4,
    fecha_creacion=datetime(2025, 1, 1, tzinfo=timezone.utc),
    nombre_usuario="Test User"
)

# Dummy current_user para propietario y admin
dummy_user = {"user_id": 1, "tipo_usuario": "comun"}
admin_user = {"user_id": 1, "tipo_usuario": "admin"}

class TestResenaService(unittest.TestCase):

    # --- Tests para create_resena_service ---
    @patch("app.services.resena_service.get_db_session")
    def test_create_resena_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Al refrescar, se asigna un id al nuevo registro
        def refresh_side_effect(instance):
            instance.id = dummy_resena.id
        mock_session.refresh.side_effect = refresh_side_effect
        mock_get_db_session.return_value = iter([mock_session])
        
        resena_data = ResenaCreate(
            comentario="Muy buena experiencia",
            puntuacion=4
        )
        result = create_resena_service(resena_data, dummy_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Reseña registrada exitosamente")
        self.assertEqual(result["data"]["id"], dummy_resena.id)
        mock_session.commit.assert_called_once()

    @patch("app.services.resena_service.get_db_session")
    def test_create_resena_service_invalid_rating(self, mock_get_db_session):
        # Este test espera que el modelo lance un error de validación de Pydantic
        with self.assertRaises(ValidationError):
            ResenaCreate(
                comentario="Experiencia mala",
                puntuacion=6  # Valor inválido, debe estar entre 1 y 5
            )

    @patch("app.services.resena_service.get_db_session")
    def test_create_resena_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.add.side_effect = Exception("Unexpected error")
        mock_get_db_session.return_value = iter([mock_session])
        
        resena_data = ResenaCreate(
            comentario="Experiencia regular",
            puntuacion=3
        )
        with self.assertRaises(HTTPException) as context:
            create_resena_service(resena_data, dummy_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Unexpected error")

    # --- Tests para get_resenas_paginated_desc_service ---
    @patch("app.services.resena_service.get_db_session")
    def test_get_resenas_paginated_desc_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        # Simular que se encuentran reseñas
        mock_session.query.return_value.join.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [dummy_resena_with_usuario]
        mock_get_db_session.return_value = iter([mock_session])
        
        result = get_resenas_paginated_desc_service(page=1, limit=5)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["id"], dummy_resena_with_usuario.id)
        self.assertEqual(result[0]["nombre_usuario"], dummy_resena_with_usuario.nombre_usuario)

    @patch("app.services.resena_service.get_db_session")
    def test_get_resenas_paginated_desc_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            get_resenas_paginated_desc_service(page=1, limit=5)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")

    # --- Tests para get_resenas_paginated_asc_service ---
    @patch("app.services.resena_service.get_db_session")
    def test_get_resenas_paginated_asc_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.join.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [dummy_resena_with_usuario]
        mock_get_db_session.return_value = iter([mock_session])
        
        result = get_resenas_paginated_asc_service(page=1, limit=5)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["id"], dummy_resena_with_usuario.id)

    @patch("app.services.resena_service.get_db_session")
    def test_get_resenas_paginated_asc_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            get_resenas_paginated_asc_service(page=1, limit=5)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")

    # --- Tests para get_resenas_by_rating_service ---
    @patch("app.services.resena_service.get_db_session")
    def test_get_resenas_by_rating_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.join.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [dummy_resena_with_usuario]
        mock_get_db_session.return_value = iter([mock_session])
        
        result = get_resenas_by_rating_service(rating=4, page=1, limit=5)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["puntuacion"], 4)

    @patch("app.services.resena_service.get_db_session")
    def test_get_resenas_by_rating_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            get_resenas_by_rating_service(rating=4, page=1, limit=5)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")

    # --- Tests para get_resenas_by_user_id_service ---
    @patch("app.services.resena_service.get_db_session")
    def test_get_resenas_by_user_id_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [dummy_resena_with_usuario]
        mock_get_db_session.return_value = iter([mock_session])
        
        result = get_resenas_by_user_id_service(user_id=1)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["nombre_usuario"], dummy_resena_with_usuario.nombre_usuario)

    @patch("app.services.resena_service.get_db_session")
    def test_get_resenas_by_user_id_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            get_resenas_by_user_id_service(user_id=1)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")

    # --- Tests para get_average_rating_service ---
    @patch("app.services.resena_service.get_db_session")
    def test_get_average_rating_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.scalar.return_value = 3.5
        mock_get_db_session.return_value = iter([mock_session])
        
        result = get_average_rating_service()
        self.assertEqual(result, 3.5)

    @patch("app.services.resena_service.get_db_session")
    def test_get_average_rating_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            get_average_rating_service()
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")

    # --- Tests para edit_resena_service ---
    @patch("app.services.resena_service.get_db_session")
    def test_edit_resena_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        dummy_resena_editable = SimpleNamespace(
            id=10,
            id_usuario=1,
            comentario="Reseña original",
            puntuacion=3,
            fecha_creacion=datetime(2025, 1, 1, tzinfo=timezone.utc)
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_resena_editable
        mock_get_db_session.return_value = iter([mock_session])
        
        resena_update_data = ResenaCreate(
            comentario="Reseña actualizada",
            puntuacion=5
        )
        result = edit_resena_service(10, resena_update_data, dummy_user)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Reseña actualizada exitosamente")
        self.assertEqual(dummy_resena_editable.comentario, "Reseña actualizada")
        self.assertEqual(dummy_resena_editable.puntuacion, 5)
        mock_session.commit.assert_called_once()

    @patch("app.services.resena_service.get_db_session")
    def test_edit_resena_service_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        resena_update_data = ResenaCreate(
            comentario="Actualizada",
            puntuacion=4
        )
        with self.assertRaises(HTTPException) as context:
            edit_resena_service(999, resena_update_data, dummy_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Reseña no encontrada", context.exception.detail)

    @patch("app.services.resena_service.get_db_session")
    def test_edit_resena_service_not_owner(self, mock_get_db_session):
        mock_session = MagicMock()
        dummy_resena_not_owner = SimpleNamespace(
            id=10,
            id_usuario=2,  # Propietario distinto
            comentario="Reseña original",
            puntuacion=3,
            fecha_creacion=datetime(2025, 1, 1, tzinfo=timezone.utc)
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_resena_not_owner
        mock_get_db_session.return_value = iter([mock_session])
        
        resena_update_data = ResenaCreate(
            comentario="Actualizada",
            puntuacion=4
        )
        with self.assertRaises(HTTPException) as context:
            edit_resena_service(10, resena_update_data, dummy_user)
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("No está autorizado para editar", context.exception.detail)

    @patch("app.services.resena_service.get_db_session")
    def test_edit_resena_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        resena_update_data = ResenaCreate(
            comentario="Actualizada",
            puntuacion=4
        )
        with self.assertRaises(HTTPException) as context:
            edit_resena_service(10, resena_update_data, dummy_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")

    # --- Tests para delete_resena_service ---
    @patch("app.services.resena_service.get_db_session")
    def test_delete_resena_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        dummy_resena_to_delete = SimpleNamespace(
            id=10,
            id_usuario=1,
            comentario="Reseña a eliminar",
            puntuacion=3,
            fecha_creacion=datetime(2025, 1, 1, tzinfo=timezone.utc)
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_resena_to_delete
        mock_get_db_session.return_value = iter([mock_session])
        
        result = delete_resena_service(10, dummy_user)
        self.assertIn("message", result)
        self.assertIn("eliminada exitosamente", result["message"])
        mock_session.commit.assert_called_once()

    @patch("app.services.resena_service.get_db_session")
    def test_delete_resena_service_not_found(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_resena_service(999, dummy_user)
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Reseña no encontrada", context.exception.detail)

    @patch("app.services.resena_service.get_db_session")
    def test_delete_resena_service_not_owner(self, mock_get_db_session):
        mock_session = MagicMock()
        dummy_resena_not_owner = SimpleNamespace(
            id=10,
            id_usuario=2,
            comentario="Reseña a eliminar",
            puntuacion=3,
            fecha_creacion=datetime(2025, 1, 1, tzinfo=timezone.utc)
        )
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_resena_not_owner
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_resena_service(10, dummy_user)
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("No está autorizado para eliminar", context.exception.detail)

    @patch("app.services.resena_service.get_db_session")
    def test_delete_resena_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = dummy_resena
        mock_session.delete.side_effect = Exception("Delete error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            delete_resena_service(dummy_resena.id, dummy_user)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Delete error")

    # --- Tests para get_average_rating_service ---
    @patch("app.services.resena_service.get_db_session")
    def test_get_average_rating_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.scalar.return_value = 3.5
        mock_get_db_session.return_value = iter([mock_session])
        
        result = get_average_rating_service()
        self.assertEqual(result, 3.5)

    @patch("app.services.resena_service.get_db_session")
    def test_get_average_rating_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            get_average_rating_service()
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")

    # --- Tests para get_resenas_by_rating_service ---
    @patch("app.services.resena_service.get_db_session")
    def test_get_resenas_by_rating_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.join.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [dummy_resena_with_usuario]
        mock_get_db_session.return_value = iter([mock_session])
        
        result = get_resenas_by_rating_service(rating=4, page=1, limit=5)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["puntuacion"], 4)

    @patch("app.services.resena_service.get_db_session")
    def test_get_resenas_by_rating_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            get_resenas_by_rating_service(rating=4, page=1, limit=5)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")

    # --- Tests para get_resenas_by_user_id_service ---
    @patch("app.services.resena_service.get_db_session")
    def test_get_resenas_by_user_id_service_success(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [dummy_resena_with_usuario]
        mock_get_db_session.return_value = iter([mock_session])
        
        result = get_resenas_by_user_id_service(user_id=1)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["nombre_usuario"], dummy_resena_with_usuario.nombre_usuario)

    @patch("app.services.resena_service.get_db_session")
    def test_get_resenas_by_user_id_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            get_resenas_by_user_id_service(user_id=1)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")

    # --- Tests para get_resenas_paginated_desc_service ---
    @patch("app.services.resena_service.get_db_session")
    def test_get_resenas_paginated_desc_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            get_resenas_paginated_desc_service(page=1, limit=5)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")

    # --- Tests para get_resenas_paginated_asc_service ---
    @patch("app.services.resena_service.get_db_session")
    def test_get_resenas_paginated_asc_service_unexpected_exception(self, mock_get_db_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Query error")
        mock_get_db_session.return_value = iter([mock_session])
        
        with self.assertRaises(HTTPException) as context:
            get_resenas_paginated_asc_service(page=1, limit=5)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Query error")
