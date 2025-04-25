# db_models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DECIMAL, Text, ForeignKey, TIMESTAMP
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    sku = Column(String(100), unique=True, nullable=False)
    name = Column(Text)
    description = Column(Text)
    category = Column(String)
    cost_price = Column(DECIMAL)
    price = Column(DECIMAL)
    stock_quantity = Column(Integer)
    available_stock = Column(Integer)
    image_url = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
