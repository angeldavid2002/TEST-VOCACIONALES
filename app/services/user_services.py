from email.message import EmailMessage
import secrets
import smtplib
import string
from fastapi import HTTPException
from ..db.database import get_db_session
from ..models.mdl_user import PasswordChangeRequest, UsuarioCreate, UsuarioUpdate
from ..schemas.sch_usuario import Usuario,Ciudad,Institucion
from .auth_service import *


def register_user(user: UsuarioCreate):
    db = next(get_db_session())
    try:
        # Validar si el email ya existe
        if db.query(Usuario).filter(Usuario.email == user.email).first():
            raise HTTPException(status_code=400, detail="El email ya está registrado.")

        # Validar si la ciudad existe
        if user.id_ciudad is not None:
            ciudad = db.query(Ciudad).filter(Ciudad.id == user.id_ciudad).first()
            if not ciudad:
                raise HTTPException(
                    status_code=400,
                    detail=f"La ciudad con id {user.id_ciudad} no existe.",
                )

        # Validar si la institución existe
        if user.id_institucion is not None:
            institucion = db.query(Institucion).filter(Institucion.id == user.id_institucion).first()
            if not institucion:
                raise HTTPException(
                    status_code=400,
                    detail=f"La institución con id {user.id_institucion} no existe.",
                )

        # Hashear la contraseña
        hashed_password = get_password_hash(user.password)

        # Crear usuario
        nuevo_usuario = Usuario(
            email=user.email,
            nombre=user.nombre, 
            sexo=user.sexo,
            contrasena=hashed_password,
            tipo_usuario="comun",
            id_ciudad=user.id_ciudad,
            id_institucion=user.id_institucion,
            fecha_registro=user.fecha_registro,
        )

        # Guardar en la base de datos
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return {"message": "Usuario registrado exitosamente"}
    except HTTPException as http_ex:
        # Propagar las excepciones HTTP específicas sin hacer un rollback
        raise http_ex
    except Exception as ex:
        # Aquí atrapamos cualquier otra excepción imprevista
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

def login_user(email: str, password: str):
    db = next(get_db_session())
    try:
        # Buscar usuario por email
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if not usuario:
            raise HTTPException(status_code=401, detail="El usuario no existe en la base de datos (Revise su correo)")

        # Verificar contraseña
        if not verify_password(password, usuario.contrasena):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        # Generar token JWT
        access_token = create_access_token(
            data={
                "user_id": usuario.id,
                "email": usuario.email,
                "tipo_usuario": usuario.tipo_usuario,
            }
        )

        return {"access_token": access_token, "token_type": "Bearer"}
    except HTTPException as http_ex:
        # Propagar las excepciones HTTP específicas
        raise http_ex
    except Exception as ex:
        # Propagar las excepciones HTTP no manejadas
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")

def get_user_data_service(current_user):
    # Verificar si el usuario tiene privilegios de acceso
    if not current_user or not current_user.get("user_id"):
        raise HTTPException(status_code=401, detail="No está autorizado.")

    db = next(get_db_session())
    try:
        # Buscar usuario en la base de datos
        usuario = db.query(Usuario).filter(Usuario.id == current_user["user_id"]).first()

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        # Devolver datos del usuario
        return {
            "ID": usuario.id,
            "Nombre": usuario.nombre,
            "Email": usuario.email,
            "Sexo": usuario.sexo,
            "Tipo_Usuario": usuario.tipo_usuario,
            "ID_Ciudad": usuario.id_ciudad,
            "ID_Institucion": usuario.id_institucion,
            "Fecha_Registro": usuario.fecha_registro,
        }
    except HTTPException as http_ex:
        # Propagar excepciones HTTP específicas
        raise http_ex
    except Exception as ex:
        # Propagar cualquier excepción inesperada
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()

def change_password_service(password_request:PasswordChangeRequest, current_user):
    db = next(get_db_session())
    try:
        # Buscar al usuario en la base de datos
        usuario = db.query(Usuario).filter(Usuario.id == current_user["user_id"]).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        # Verificar la contraseña actual
        if not verify_password(password_request.current_password, usuario.contrasena):
            raise HTTPException(
                status_code=403, detail="La contraseña actual es incorrecta."
            )

        # Validar que la nueva contraseña y su confirmación coincidan
        if password_request.new_password != password_request.confirm_password:
            raise HTTPException(
                status_code=400,
                detail="La nueva contraseña y la confirmación no coinciden.",
            )

        # Actualizar la contraseña del usuario
        usuario.contrasena = get_password_hash(password_request.new_password)
        db.commit()

        return {"message": "Contraseña actualizada exitosamente."}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()

def edit_user_service(user_data: UsuarioUpdate, current_user):
    # Extraer el ID del usuario actual desde el token
    user_id = current_user.get("user_id")

    db = next(get_db_session())
    try:
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        # Campos no permitidos para modificar
        campos_no_editables = {"email", "id", "tipo_usuario", "fecha_registro"}

        # Actualizar solo los campos permitidos y proporcionados
        for key, value in user_data.model_dump(exclude_unset=True).items():
            if key not in campos_no_editables:
                setattr(usuario, key, value)

        db.commit()
        db.refresh(usuario)

        return {
            "message": "Usuario actualizado exitosamente",
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "sexo": usuario.sexo,
                "email": usuario.email,
                "id_ciudad": usuario.id_ciudad,
                "id_institucion": usuario.id_institucion,
                "fecha_registro": usuario.fecha_registro,
            },
        }
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()

def reset_password_service(email: str):
    db = next(get_db_session())
    try:
        # Buscar al usuario por correo electrónico
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="El correo electrónico no está registrado.")
        
        # Generar una nueva contraseña aleatoria (por ejemplo, de 10 caracteres)
        alphabet = string.ascii_letters + string.digits
        new_password = ''.join(secrets.choice(alphabet) for _ in range(10))
        
        # Hashear la nueva contraseña
        hashed_password = get_password_hash(new_password)
        
        # Actualizar la contraseña del usuario en la base de datos
        usuario.contrasena = hashed_password
        db.commit()
        
        # Construir el mensaje de correo
        msg = EmailMessage()
        msg["Subject"] = "Restablecimiento de contraseña"
        msg["From"] = config.FROM_EMAIL
        msg["To"] = usuario.email
        msg.set_content(
            f"Hola {usuario.nombre},\n\n"
            f"Tu contraseña ha sido restablecida automáticamente. Tu nueva contraseña es:\n\n"
            f"{new_password}\n\n"
            "Te recomendamos cambiarla después de iniciar sesión.\n\n"
            "Saludos."
        )
        
        # Enviar el correo utilizando SMTP (autenticación básica)
        try:
            with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
                server.starttls()
                server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al enviar el correo: {str(e)}")
        
        return {
            "message": f"Se ha enviado un correo a {email} con tu nueva contraseña."
        }
    except HTTPException as http_ex:
        db.rollback()
        raise http_ex
    except Exception as ex:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(ex)}")
    finally:
        db.close()