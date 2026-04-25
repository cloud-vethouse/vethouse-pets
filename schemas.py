from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date # IMPORTANTE: Para validar AAAA-MM-DD
from models import SexoEnum


# --- ESQUEMAS DE MASCOTAS ---
class MascotaBase(BaseModel):
    nombre: str
    especie: str
    raza: Optional[str] = None
    sexo: SexoEnum
    fecha_nacimiento: date
    peso: float 
    esterilizado: bool
    observaciones_generales: Optional[str] = None

class MascotaCreate(MascotaBase):
    id_dueno: int 

class Mascota(MascotaBase):
    id: int

    class Config:
        from_attributes = True 

# --- ESQUEMAS DE DUEÑOS ---
class DuenoBase(BaseModel):
    nombre: str
    telefono: str
    correo: EmailStr

class DuenoCreate(DuenoBase):
    pass

class Dueno(DuenoBase):
    id: int
    mascotas: List[Mascota] = []

    class Config:
        from_attributes = True


class DuenoListItem(DuenoBase):
    id: int

    class Config:
        from_attributes = True