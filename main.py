from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from datetime import datetime
import pytz
import re

from orm_classes import Base, FitnessClass, Booking
from pydantic import BaseModel, field_validator

DATABASE_URL = "sqlite:///./fitness_booking.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fitness Studio Booking API")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class ClassOut(BaseModel):
    id: int
    name: str
    datetime: datetime
    instructor: str
    available_slots: int

    class Config:
        from_attributes = True

class BookingRequest(BaseModel):
    class_id: int
    client_name: str
    client_email: str

    @field_validator('client_email')
    def validate_email_format(cls, v):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v

class BookingOut(BaseModel):
    id: int
    class_id: int
    client_name: str
    client_email: str

    @field_validator('client_email')
    def validate_email_format(cls, v):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v

    class Config:
        from_attributes = True

@app.on_event("startup")
def add_data():
    db = SessionLocal()
    if db.query(FitnessClass).first():
        db.close()
        return

    sample_classes = [
        FitnessClass(name="Yoga", datetime=pytz.timezone("Asia/Kolkata").localize(datetime(2025, 6, 10, 7, 0)), instructor="Ram", available_slots=5),
        FitnessClass(name="Zumba", datetime=pytz.timezone("Asia/Kolkata").localize(datetime(2025, 6, 10, 8, 0)), instructor="Rohit", available_slots=10),
        FitnessClass(name="HIIT", datetime=pytz.timezone("Asia/Kolkata").localize(datetime(2025, 6, 10, 9, 0)), instructor="Alice", available_slots=8),
    ]
    db.add_all(sample_classes)
    db.commit()
    db.close()

@app.get("/classes", response_model=List[ClassOut])
def get_classes(db: Session = Depends(get_db)):
    classes = db.query(FitnessClass).order_by(FitnessClass.datetime).all()
    return classes

@app.post("/book", response_model=BookingOut)
def book_class(request: BookingRequest, db: Session = Depends(get_db)):

    fitness_class = db.query(FitnessClass).filter(FitnessClass.id == request.class_id).first()
    if not fitness_class:
        raise HTTPException(status_code=404, detail="Fitness class not found")

    if fitness_class.available_slots <= 0:
        raise HTTPException(status_code=400, detail="No available slots")
    
    if not request.client_name.strip():
        raise HTTPException(status_code=422, detail="Client name must not be empty")

    same_booking = db.query(Booking).filter(Booking.id == request.class_id, Booking.client_email == request.client_email).first()

    if same_booking:
        raise HTTPException(
        status_code=409,
        detail="This class has already been booked by the client."
    )


    booking = Booking(
        class_id=request.class_id,
        client_name=request.client_name,
        client_email=request.client_email
    )

    fitness_class.available_slots -= 1
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    return booking

@app.get("/bookings", response_model=List[BookingOut])
def get_bookings(email: str = Query(..., description="Client email address", min_length=5, max_length=254), db: Session = Depends(get_db)):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    bookings = db.query(Booking).filter(Booking.client_email == email).all()
    if bookings == []:
        raise HTTPException(status_code=404, detail="No bookings found for this user")
    return bookings