from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.food_model import Base

class DatabaseManager:
    def __init__(self, db_path="sqlite:///nutriscan.db"):
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.Session() 