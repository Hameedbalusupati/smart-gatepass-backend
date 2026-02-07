from flask import Blueprint, jsonify
from datetime import datetime
import jwt

from models import db, GatePass, User
from config import Config


# =================================================
# BLUEPRINT (NO url_prefix, NO CORS HERE)
# =================================================
security_bp = Blueprint("security_bp", __name__)

QR_ALGORITHM = "HS256"


# =================================================
# SCAN QR CODE (SECURITY – ONE-TIME USE)
# =================================================
@security_bp.route("/scan/<string:qr_token>", methods=["GET"])
def scan_qr(qr_token):
    try:
        # 🔐 DECODE QR TOKEN
        decoded = jwt.decode(
            qr_token,
            Config.QR_SECRET_KEY,
            algorithms=[QR_ALGORITHM]
        )

        gatepass_id = decoded.get("gatepass_id")
        if not gatepass_id:
            return jsonify({
                "success": False,
                "message": "Invalid QR data"
            }), 400

        gatepass = GatePass.query.get(gatepass_id)
        if not gatepass:
            return jsonify({
                "success": False,
                "message": "Gatepass not found"
            }), 404

        # 🔒 ONE-TIME USE CHECK
        if gatepass.status != "Approved":
            return jsonify({
                "success": False,
                "message": "Gatepass already used or invalid"
            }), 400

        # =========================
        # MARK STUDENT AS OUT
        # =========================
        gatepass.status = "Out"
        gatepass.out_time = datetime.utcnow()
        db.session.commit()

        student = User.query.get(gatepass.student_id)

        return jsonify({
            "success": True,
            "action": "OUT",
            "student_name": student.name if student else None,
            "college_id": student.college_id if student else None,
            "department": student.department if student else None,
            "reason": gatepass.reason,
            "parent_mobile": gatepass.parent_mobile,
            "time": gatepass.out_time.isoformat()
        }), 200

    # ⛔ QR EXPIRED
    except jwt.ExpiredSignatureError:
        return jsonify({
            "success": False,
            "message": "QR Code expired"
        }), 410

    # ⛔ INVALID QR
    except jwt.InvalidTokenError:
        return jsonify({
            "success": False,
            "message": "Invalid QR Code"
        }), 400

    # ⛔ UNKNOWN ERROR
    except Exception as e:
        print("QR SCAN ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500