
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import pytz

Base = declarative_base()

IST = pytz.timezone("Asia/Kolkata")

class FitnessClass(Base):
    __tablename__ = "fitness_classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    datetime = Column(DateTime, nullable=False)
    instructor = Column(String, nullable=False)
    available_slots = Column(Integer, default=10)

    bookings = relationship("Booking", back_populates="fitness_class")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("fitness_classes.id"))
    client_name = Column(String, nullable=False)
    client_email = Column(String, nullable=False)

    fitness_class = relationship("FitnessClass", back_populates="bookings")
