from pydantic import BaseModel
from typing import Optional

class AdminBase(BaseModel):
    username: str


class AdminCreate(AdminBase):
    password: str


class Admin(AdminBase):
    id: int

    class Config:
        orm_mode = True


class CarBase(BaseModel):
    license_plate: str
    owner_name: str
    owner_lastname: str
    owner_phone: str
    building: str   
    apartment: int  
    payment_status: str  # "Vigente" o "No Vigente"
    admin_id: int 

class CarCreate(CarBase):
    pass


class Car(CarBase):
    id: int
    admin_id: Optional[int] = None

    class Config:
        orm_mode = True


class CarUpdate(BaseModel):
    license_plate: Optional[str]
    owner_name: Optional[str]
    owner_lastname: Optional[str]
    owner_phone: Optional[str]
    building: Optional[str]
    apartment: Optional[int]
    payment_status: Optional[str]                  



class UserBase(BaseModel):
    plate_number: str


class UserCreate(UserBase):
    password: str  


class User(UserBase):
    id: int
    car_id: int
    password: str  

    class Config:
        orm_mode = True