from flask import Blueprint, request, jsonify
from db_utils import create_order, get_or_create_customer_by_line_id
from sqlalchemy.exc import SQLAlchemyError

order_api = Blueprint('order_api', __name__)

# 🛒 สร้างคำสั่งซื้อใหม่
@order_api.route('/orders', methods=['POST'])
def create_new_order():
    data = request.json
    try:
        # 1. หา/สร้างลูกค้าจาก LINE userId
        customer = get_or_create_customer_by_line_id(
            line_user_id=data["line_user_id"],
            name=data.get("name")
        )
        
        # 2. สร้างออเดอร์
        order_id = create_order(
            order_number=data["order_number"],
            channel=data.get("channel", "line"),  # default = line
            customer_id=customer.id,
            items=data["items"]
        )

        return jsonify({
            "message": "สร้างออเดอร์สำเร็จ ✅",
            "order_id": order_id
        }), 201

    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400

