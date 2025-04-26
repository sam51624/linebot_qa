from flask import Blueprint, request, jsonify
from db_config import SessionLocal
from db_models import Product
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

product_api = Blueprint('product_api', __name__)

# 🔍 GET: ดึงสินค้าทั้งหมด
@product_api.route('/products', methods=['GET'])
def get_all_products():
    session = SessionLocal()
    try:
        products = session.query(Product).all()
        result = [
            {
                "id": p.id,
                "sku": p.sku,
                "name": p.name,
                "price": float(p.price),
                "stock_quantity": p.stock_quantity,
                "available_stock": p.available_stock,
                "category": p.category,
                "image_url": p.image_url
            }
            for p in products
        ]
        return jsonify(result)
    except Exception as e:
        print("[ERROR GET]", e)
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# ➕ POST: เพิ่มสินค้าใหม่
@product_api.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    session = SessionLocal()
    try:
        # เช็คว่ามี sku นี้ในระบบแล้วหรือยัง
        existing_product = session.query(Product).filter_by(sku=data["sku"]).first()
        if existing_product:
            return jsonify({"error": "มี SKU นี้อยู่ในระบบแล้ว ❗"}), 400

        product = Product(
            sku=data["sku"],
            name=data.get("name"),
            description=data.get("description", ""),
            category=data.get("category", ""),
            cost_price=data.get("cost_price", 0),
            price=data.get("price", 0),
            stock_quantity=data.get("stock_quantity", 0),
            available_stock=data.get("available_stock", 0),
            image_url=data.get("image_url", "")
        )
        session.add(product)
        session.commit()
        return jsonify({"message": "เพิ่มสินค้าสำเร็จ ✅", "product_id": product.id}), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"error": "เกิดข้อผิดพลาดเรื่องความซ้ำของข้อมูล"}), 400
    except SQLAlchemyError as e:
        session.rollback()
        print("[ERROR POST]", e)
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

