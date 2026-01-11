from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    price = Column(Float)
    category = Column(String, index=True)
    stock = Column(Integer, default=0)
    alert_threshold = Column(Integer, default=5)  # 🔔 NOUVEAU

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now)
    total = Column(Float)
    details = Column(String)

def create_tables(engine):
    Base.metadata.create_all(bind=engine)
