from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models, schemas, database
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gestión de Mascotas",
    description="Microservicio encargado del registro de Dueños y Mascotas",
    version="1.0.0"
)

# Post un dueño
@app.post("/duenos/", response_model=schemas.Dueno, status_code=status.HTTP_201_CREATED, tags=["Dueños"])
def crear_dueno(dueno: schemas.DuenoCreate, db: Session = Depends(get_db)):
    db_dueno = models.Dueno(
        nombre=dueno.nombre, 
        telefono=dueno.telefono, 
        correo=dueno.correo
    )
    db.add(db_dueno)
    db.commit()
    db.refresh(db_dueno)
    return db_dueno

# Get todos los dueños
@app.get("/duenos/", response_model=List[schemas.Dueno], tags=["Dueños"])
def listar_duenos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Dueno).offset(skip).limit(limit).all()

# Post mascota 
@app.post("/mascotas/", response_model=schemas.Mascota, status_code=status.HTTP_201_CREATED, tags=["Mascotas"])
def crear_mascota(mascota: schemas.MascotaCreate, db: Session = Depends(get_db)):
    dueno_existe = db.query(models.Dueno).filter(models.Dueno.id == mascota.id_dueno).first()
    if not dueno_existe:
        raise HTTPException(status_code=404, detail="El ID del dueño proporcionado no existe")
    
    db_mascota = models.Mascota(
        nombre=mascota.nombre,
        especie=mascota.especie,
        raza=mascota.raza,
        id_dueno=mascota.id_dueno
    )
    db.add(db_mascota)
    db.commit()
    db.refresh(db_mascota)
    return db_mascota

# Get mascota por id
@app.get("/mascotas/{mascota_id}", response_model=schemas.Mascota, tags=["Mascotas"])
def obtener_mascota(mascota_id: int, db: Session = Depends(get_db)):
    db_mascota = db.query(models.Mascota).filter(models.Mascota.id == mascota_id).first()
    if db_mascota is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return db_mascota


# --- HEALTH CHECK (Para AWS y Balanceador) ---

@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "operativo", "microservicio": "vethouse-pets"}