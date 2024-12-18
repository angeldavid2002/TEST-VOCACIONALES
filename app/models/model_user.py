from pydantic import BaseModel

class UsuarioBase(BaseModel):
    nombre: str
    email: str
    tipo_usuario: str
    ciudad:int
    institucion:int

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioInDB(UsuarioBase):
    contrasena: str

class Usuario(UsuarioBase):
    id: int

    class Config:
        from_attributes = True
