from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)


class Car(Base):
    __tablename__ = "cars"
    
    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String(50), unique=True, index=True, nullable=False)
    owner_name = Column(String(100), nullable=False)
    owner_lastname = Column(String(100), nullable=False)
    owner_phone = Column(String(20), nullable=False)
    building = Column(String(50), nullable=False)  # Edificio requerido
    apartment = Column(Integer, nullable=False)    # Apartamento requerido
    payment_status = Column(String(20), nullable=False)  # "Vigente" o "No Vigente"
    
    admin_id = Column(Integer, ForeignKey("admins.id"))
    admin = relationship("Admin")
    
    # Relación con User
    user = relationship("User", back_populates="car", uselist=False)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String(50), unique=True, index=True, nullable=False)  # Número de placa como nombre de usuario
    password = Column(String(255), nullable=False)  # Contraseña, igual al número de placa
    car_id = Column(Integer, ForeignKey("cars.id"), unique=True)
    
    # Relación inversa con Car
    car = relationship("Car", back_populates="user")