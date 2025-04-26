# 📦 ดึงออเดอร์ทั้งหมด
@order_api.route('/orders', methods=['GET'])
def get_all_orders():
    session = SessionLocal()
    try:
        orders = session.query(Order).all()
        result = []
        for order in orders:
            result.append({
                "order_number": order.order_number,
                "channel": order.channel,
                "customer_id": order.customer_id,
                "total_amount": float(order.total_amount),
                "status": order.status,
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else None
            })
        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

# 📦 ดึงรายละเอียดออเดอร์ พร้อมสินค้าในออเดอร์
@order_api.route('/orders/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    session = SessionLocal()
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({"error": "ไม่พบออเดอร์"}), 404

        items = session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        item_list = []
        for item in items:
            item_list.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": float(item.price),
                "cost_at_sale": float(item.cost_at_sale)
            })

        return jsonify({
            "order_number": order.order_number,
            "channel": order.channel,
            "customer_id": order.customer_id,
            "total_amount": float(order.total_amount),
            "status": order.status,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else None,
            "items": item_list
        }), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()
