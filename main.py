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

# Endpoints para dueños
# Post un dueño
@app.post("/api/v1/duenos/", response_model=schemas.Dueno, status_code=status.HTTP_201_CREATED, tags=["Dueños"])
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
@app.get("api/v1/duenos/", response_model=List[schemas.Dueno], tags=["Dueños"])
def listar_duenos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Dueno).offset(skip).limit(limit).all()

# Get dueño por id
@app.get("api/v1/duenos/{dueno_id}", response_model=schemas.Dueno, tags=["Dueños"])
def obtener_dueno(dueno_id: int, db: Session = Depends(get_db)):
    db_dueno = db.query(models.Dueno).filter(models.Dueno.id == dueno_id).first()
    if not db_dueno:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    return db_dueno

# Put (actualizar) un dueño
@app.put("api/v1/duenos/{dueno_id}", response_model=schemas.Dueno, tags=["Dueños"])
def actualizar_dueno(dueno_id: int, dueno_update: schemas.DuenoCreate, db: Session = Depends(get_db)):
    db_dueno = db.query(models.Dueno).filter(models.Dueno.id == dueno_id).first()
    if not db_dueno:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    
    db_dueno.nombre = dueno_update.nombre
    db_dueno.telefono = dueno_update.telefono
    db_dueno.correo = dueno_update.correo
    
    db.commit()
    db.refresh(db_dueno)
    return db_dueno

# Delete un dueño
@app.delete("/api/v1/duenos/{dueno_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Dueños"])
def eliminar_dueno(dueno_id: int, db: Session = Depends(get_db)):
    db_dueno = db.query(models.Dueno).filter(models.Dueno.id == dueno_id).first()
    if not db_dueno:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    
    db.delete(db_dueno)
    db.commit()
    return None


# --- ENDPOINTS PARA MASCOTAS ---
# Post mascota 
@app.post("/api/v1/mascotas/", response_model=schemas.Mascota, status_code=status.HTTP_201_CREATED, tags=["Mascotas"])
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

# Get todas las mascotas
@app.get("/api/v1/mascotas/", response_model=List[schemas.Mascota], tags=["Mascotas"])
def listar_mascotas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Mascota).offset(skip).limit(limit).all()

# Get mascota por id
@app.get("/api/v1/mascotas/{mascota_id}", response_model=schemas.Mascota, tags=["Mascotas"])
def obtener_mascota(mascota_id: int, db: Session = Depends(get_db)):
    db_mascota = db.query(models.Mascota).filter(models.Mascota.id == mascota_id).first()
    if db_mascota is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return db_mascota

# Put (actualizar) mascota
@app.put("/api/v1/mascotas/{mascota_id}", response_model=schemas.Mascota, tags=["Mascotas"])
def actualizar_mascota(mascota_id: int, mascota_update: schemas.MascotaCreate, db: Session = Depends(get_db)):
    db_mascota = db.query(models.Mascota).filter(models.Mascota.id == mascota_id).first()
    if not db_mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    
    # Validar que el nuevo id_dueno (si se cambia) exista
    dueno_existe = db.query(models.Dueno).filter(models.Dueno.id == mascota_update.id_dueno).first()
    if not dueno_existe:
        raise HTTPException(status_code=404, detail="El ID del dueño proporcionado no existe")

    db_mascota.nombre = mascota_update.nombre
    db_mascota.especie = mascota_update.especie
    db_mascota.raza = mascota_update.raza
    db_mascota.id_dueno = mascota_update.id_dueno
    
    db.commit()
    db.refresh(db_mascota)
    return db_mascota

# Delete mascota
@app.delete("/api/v1/mascotas/{mascota_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Mascotas"])
def eliminar_mascota(mascota_id: int, db: Session = Depends(get_db)):
    db_mascota = db.query(models.Mascota).filter(models.Mascota.id == mascota_id).first()
    if not db_mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    
    db.delete(db_mascota)
    db.commit()
    return None

# Get todas las mascotas de un dueño específico
@app.get("/api/v1/duenos/{dueno_id}/mascotas", response_model=List[schemas.Mascota], tags=["Dueños"])
def listar_mascotas_por_dueno(dueno_id: int, db: Session = Depends(get_db)):
    dueno = db.query(models.Dueno).filter(models.Dueno.id == dueno_id).first()
    if not dueno:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    return db.query(models.Mascota).filter(models.Mascota.id_dueno == dueno_id).all()


# --- HEALTH CHECK ---

@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "operativo", "microservicio": "vethouse-pets"}