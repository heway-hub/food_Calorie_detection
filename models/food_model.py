from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class FoodEntry(Base):
    __tablename__ = 'food_entries'
    
    id = Column(Integer, primary_key=True)
    food_name = Column(String(100), nullable=False)
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    image_path = Column(String(255))
    timestamp = Column(DateTime) 