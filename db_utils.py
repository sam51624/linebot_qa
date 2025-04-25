# db_utils.py
from db_config import SessionLocal
from db_models import Product

def get_product_by_sku(sku: str):
    session = SessionLocal()
    product = session.query(Product).filter(Product.sku == sku).first()
    session.close()
    return product
