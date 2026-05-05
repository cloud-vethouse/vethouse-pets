import enum
from sqlalchemy import Column, Integer, Float, String, Date, Boolean, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from database import Base


class SexoEnum(str, enum.Enum):
    MACHO = "Macho"
    HEMBRA = "Hembra"

class Dueno(Base):
    __tablename__ = "duenos"
    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String(8), unique=True, nullable=False)
    nombres = Column(String(100))
    telefono = Column(String(9), unique=True)
    correo = Column(String(100), unique=True)
    mascotas = relationship("Mascota", back_populates="propietario")

class Mascota(Base):
    __tablename__ = "mascotas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    especie = Column(String(50))
    raza = Column(String(50))
    sexo = Column(SqlEnum(SexoEnum), nullable=False)
    fecha_nacimiento = Column(Date)
    peso = Column(Float)
    esterilizado = Column(Boolean, default=False)
    observaciones_generales = Column(String(250))
    id_dueno = Column(Integer, ForeignKey("duenos.id"))
    
    propietario = relationship("Dueno", back_populates="mascotas")