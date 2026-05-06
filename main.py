from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_pagination(skip: int, limit: int, max_limit: int = 200):
    safe_skip = max(skip, 0)
    safe_limit = min(max(limit, 1), max_limit)
    return safe_skip, safe_limit

# Endpoints para dueños
# Post un dueño
@app.post("/api/v1/duenos", response_model=schemas.Dueno, status_code=status.HTTP_201_CREATED, tags=["Dueños"])
def crear_dueno(dueno: schemas.DuenoCreate, db: Session = Depends(get_db)):
    email_existe = db.query(models.Dueno).filter(models.Dueno.correo == dueno.correo).first()
    if email_existe:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    dni_existe = db.query(models.Dueno).filter(models.Dueno.dni == dueno.dni).first()
    if dni_existe:
        raise HTTPException(status_code=400, detail="El DNI ya está registrado")
    
    db_dueno = models.Dueno(
        dni = dueno.dni,
        nombres=dueno.nombres, 
        telefono=dueno.telefono, 
        correo=dueno.correo
    )
    db.add(db_dueno)
    db.commit()
    db.refresh(db_dueno)
    return db_dueno

# Get todos los dueños
@app.get("/api/v1/duenos", response_model=List[schemas.DuenoListItem], tags=["Dueños"])
def listar_duenos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    safe_skip, safe_limit = normalize_pagination(skip, limit)
    return db.query(models.Dueno).offset(safe_skip).limit(safe_limit).all()


@app.get("/api/v1/duenos/count", tags=["Dueños"])
def contar_duenos(db: Session = Depends(get_db)):
    return {"total": db.query(models.Dueno).count()}

# Get dueño por id
@app.get("/api/v1/duenos/{dueno_id}", response_model=schemas.Dueno, tags=["Dueños"])
def obtener_dueno(dueno_id: int, db: Session = Depends(get_db)):
    db_dueno = db.query(models.Dueno).filter(models.Dueno.id == dueno_id).first()
    if not db_dueno:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    return db_dueno

# Put (actualizar) un dueño
@app.put("/api/v1/duenos{dueno_id}", response_model=schemas.Dueno, tags=["Dueños"])
def actualizar_dueno(dueno_id: int, dueno_update: schemas.DuenoCreate, db: Session = Depends(get_db)):
    db_dueno = db.query(models.Dueno).filter(models.Dueno.id == dueno_id).first()
    if not db_dueno:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    
    db_dueno.nombres = dueno_update.nombres
    db_dueno.telefono = dueno_update.telefono
    db_dueno.correo = dueno_update.correo
    db_dueno.dni = dueno_update.dni
    
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
@app.post("/api/v1/mascotas", response_model=schemas.Mascota, status_code=status.HTTP_201_CREATED, tags=["Mascotas"])
def crear_mascota(mascota: schemas.MascotaCreate, db: Session = Depends(get_db)):
    dueno_existe = db.query(models.Dueno).filter(models.Dueno.id == mascota.id_dueno).first()
    if not dueno_existe:
        raise HTTPException(status_code=404, detail="El ID del dueño proporcionado no existe")
    
    db_mascota = models.Mascota(
        nombre=mascota.nombre,
        especie=mascota.especie,
        raza=mascota.raza,
        sexo=mascota.sexo,
        fecha_nacimiento=mascota.fecha_nacimiento,
        peso=mascota.peso,
        esterilizado=mascota.esterilizado,
        observaciones_generales=mascota.observaciones_generales,
        id_dueno=mascota.id_dueno
    )
    db.add(db_mascota)
    db.commit()
    db.refresh(db_mascota)
    return db_mascota

# Get todas las mascotas
@app.get("/api/v1/mascotas", response_model=List[schemas.Mascota], tags=["Mascotas"])
def listar_mascotas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    safe_skip, safe_limit = normalize_pagination(skip, limit)
    return db.query(models.Mascota).offset(safe_skip).limit(safe_limit).all()


@app.get("/api/v1/mascotas/count", tags=["Mascotas"])
def contar_mascotas(db: Session = Depends(get_db)):
    return {"total": db.query(models.Mascota).count()}

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
    db_mascota.sexo = mascota_update.sexo
    db_mascota.fecha_nacimiento = mascota_update.fecha_nacimiento
    db_mascota.peso = mascota_update.peso
    db_mascota.esterilizado = mascota_update.esterilizado
    db_mascota.observaciones_generales = mascota_update.observaciones_generales
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