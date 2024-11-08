from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import SessionLocal, engine
from passlib.context import CryptContext
from typing import Optional
#from pydantic import BaseModel

app = FastAPI()

# Inicializa el contexto de encriptación para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependencia para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    # Buscar al administrador por nombre de usuario
    admin = db.query(models.Admin).filter(models.Admin.username == username).first()
    if not admin or not verify_password(password, admin.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    # Devolver un mensaje de éxito o un identificador básico
    return {"message": "Inicio de sesión exitoso", "admin_id": admin.id}

# Endpoint para crear un admin
@app.post("/admins/", response_model=schemas.Admin)
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(admin.password)
    db_admin = models.Admin(username=admin.username, password=hashed_password)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

# Endpoint para crear un vehículo y un usuario normal
@app.post("/create_car/", response_model=schemas.Car)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    # verificamos que no exista el numero de placa del vehiculo
    existing_car = db.query(models.Car).filter(models.Car.license_plate == car.license_plate).first()
    if existing_car:
        raise HTTPException(status_code=400, detail="El número de placa ya existe.")

    # Crear el carro
    db_car = models.Car(**car.dict())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)

    # Crear el usuario normal asociado al carro
    hashed_password = pwd_context.hash(db_car.license_plate)
    db_user = models.User(
        plate_number=db_car.license_plate,
        password=hashed_password,
        car_id=db_car.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_car

# Endpoint para listar vehículos
@app.get("/cars/", response_model=list[schemas.Car])
def get_cars(db: Session = Depends(get_db)):
    return db.query(models.Car).all()


@app.get("/cars/search", response_model=list[schemas.Car])
def search_cars(
    license_plate: Optional[str] = Query(None),
    payment_status: Optional[str] = Query(None),
    owner_name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.Car)

    # Filtros opcionales
    if license_plate:
        query = query.filter(models.Car.license_plate.ilike(f"%{license_plate}%"))
    if payment_status:
        query = query.filter(models.Car.payment_status == payment_status)
    if owner_name:
        query = query.filter(models.Car.owner_name.ilike(f"%{owner_name}%"))

    results = query.all()
    return results


@app.get("/cars/{car_id}", response_model=schemas.Car)
def get_car_detail(car_id: int, db: Session = Depends(get_db)):
    # Buscar el carro por su id
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Carro no encontrado")

    return db_car




@app.put("/cars/{car_id}", response_model=schemas.Car)
def update_car(car_id: int, car: schemas.CarUpdate, db: Session = Depends(get_db)):
    # Buscar el carro por su id
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Carro no encontrado")

    # Actualizar los campos proporcionados en la solicitud
    update_data = car.dict(exclude_unset=True)
    if "license_plate" in update_data:
        new_plate = update_data["license_plate"]

        # Actualizar el nombre de usuario y la contraseña del usuario asociado
        db_user = db.query(models.User).filter(models.User.car_id == db_car.id).first()
        db_user.plate_number = new_plate
        db_user.password = pwd_context.hash(new_plate)

    for key, value in update_data.items():
        setattr(db_car, key, value)

    db.commit()
    db.refresh(db_car)
    return db_car


@app.delete("/cars/{car_id}", response_model=dict)
def delete_car(car_id: int, db: Session = Depends(get_db)):
    # Buscar el carro por su id
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Carro no encontrado")

    # Buscar y eliminar el usuario asociado al carro
    db_user = db.query(models.User).filter(models.User.car_id == car_id).first()
    if db_user:
        db.delete(db_user)
    
    # Eliminar el carro
    db.delete(db_car)
    db.commit()
    return {"detail": "Carro y usuario asociado eliminados exitosamente"}