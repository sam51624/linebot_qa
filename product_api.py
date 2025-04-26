from flask import Blueprint, request, jsonify
from db_config import SessionLocal
from db_models import Product
from sqlalchemy.exc import SQLAlchemyError

product_api = Blueprint('product_api', __name__)

@product_api.route('/products', methods=['GET'])
def get_all_products():
    session = SessionLocal()
    try:
        products = session.query(Product).all()
        result = [
            {
                "sku": p.sku,
                "name": p.name,
                "price": float(p.price),
                "stock_quantity": p.stock_quantity
            } for p in products
        ]
        return jsonify(result)
    finally:
        session.close()

@product_api.route('/products', methods=['POST'])
def add_product():
    data = request.json
    session = SessionLocal()
    try:
        product = Product(
            sku=data["sku"],
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", ""),
            cost_price=data.get("cost_price", 0),
            price=data["price"],
            stock_quantity=data.get("stock_quantity", 0),
            available_stock=data.get("available_stock", 0),
            image_url=data.get("image_url", "")
        )
        session.add(product)
        session.commit()
        return jsonify({"message": "เพิ่มสินค้าสำเร็จ ✅"}), 201
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()
