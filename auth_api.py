from flask import Blueprint, request, jsonify
from db_models import User
from db_config import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
import bcrypt

auth_api = Blueprint('auth_api', __name__)

@auth_api.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}), 400

    session = SessionLocal()
    try:
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            return jsonify({"error": "ชื่อผู้ใช้นี้มีอยู่แล้ว"}), 400

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(username=username, password=hashed_pw)
        session.add(new_user)
        session.commit()

        return jsonify({"message": "สมัครสมาชิกสำเร็จ"})
    except SQLAlchemyError:
        session.rollback()
        return jsonify({"error": "เกิดข้อผิดพลาดในระบบ"}), 500
    finally:
        session.close()

@auth_api.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({"message": "เข้าสู่ระบบสำเร็จ"})
        else:
            return jsonify({"error": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"}), 401
    except SQLAlchemyError:
        return jsonify({"error": "เกิดข้อผิดพลาดในระบบ"}), 500
    finally:
        session.close()

