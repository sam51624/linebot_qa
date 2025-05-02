from flask import Blueprint, request, jsonify
from db_config import SessionLocal
from db_models import User
import bcrypt
from sqlalchemy.exc import IntegrityError

auth_api = Blueprint("auth_api", __name__)

@auth_api.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "กรอกข้อมูลไม่ครบ"}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    session = SessionLocal()

    try:
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            return jsonify({"error": "ชื่อผู้ใช้นี้มีอยู่แล้ว"}), 400

        user = User(username=username, password=hashed_pw)
        session.add(user)
        session.commit()
        return jsonify({"message": "สมัครสมาชิกสำเร็จ"}), 201

    except IntegrityError as e:
        session.rollback()
        print("⚠️ IntegrityError:", e)
        return jsonify({"error": "ชื่อผู้ใช้นี้มีอยู่แล้ว หรือข้อมูลไม่ถูกต้อง"}), 400

    except Exception as e:
        session.rollback()
        print("🔥 Unexpected error:", e)
        return jsonify({"error": "เกิดข้อผิดพลาดในระบบ", "detail": str(e)}), 500

    finally:
        session.close()

