from flask import Blueprint, request, jsonify
from db_utils import create_order, get_or_create_customer_by_line_id
from db_models import Customer, Order, OrderItem  # <-- ✅ ต้อง import มาด้วย
from sqlalchemy.exc import SQLAlchemyError
from db_config import SessionLocal

order_api = Blueprint('order_api', __name__)

# 🛒 สร้างคำสั่งซื้อใหม่
@order_api.route('/orders', methods=['POST'])
def create_new_order():
    data = request.json
    session = SessionLocal()
    try:
        # 1. หา/สร้างลูกค้าจาก LINE userId
        customer = session.query(Customer).filter(Customer.line_user_id == data["line_user_id"]).first()
        if not customer:
            customer = Customer(
                line_user_id=data["line_user_id"],
                name=data.get("name")
            )
            session.add(customer)
            session.flush()  # ให้ได้ customer.id ทันที

        # 2. สร้างออเดอร์
        total = sum(item['price'] * item['quantity'] for item in data["items"])
        order = Order(
            order_number=data["order_number"],
            channel=data.get("channel", "line"),
            customer_id=customer.id,
            total_amount=total,
            status='new'
        )
        session.add(order)
        session.flush()

        for item in data["items"]:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                price=item["price"],
                cost_at_sale=item.get("cost_at_sale", 0)
            )
            session.add(order_item)

        session.commit()

        return jsonify({
            "message": "สร้างออเดอร์สำเร็จ ✅",
            "order_id": order.id
        }), 201

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()
