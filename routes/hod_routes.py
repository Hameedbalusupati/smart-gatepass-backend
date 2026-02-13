from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import jwt

from models import db, GatePass, User
from config import Config

# =====================================================
# BLUEPRINT
# =====================================================
hod_bp = Blueprint("hod_bp", __name__)

QR_ALGORITHM = "HS256"


# =====================================================
# VIEW PENDING GATEPASSES (HOD – DEPARTMENT WISE)
# =====================================================
@hod_bp.route("/gatepasses/pending", methods=["GET"])
@jwt_required()
def hod_pending():

    hod_id = get_jwt_identity()
    hod = User.query.get(int(hod_id))

    if not hod or hod.role != "hod":
        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    if not hod.department:
        return jsonify({
            "success": False,
            "message": "HOD department not assigned"
        }), 400

    gatepasses = (
        GatePass.query
        .join(User, GatePass.student_id == User.id)
        .filter(
            GatePass.status == "PendingHOD",
            User.department == hod.department
        )
        .order_by(GatePass.created_at.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "gatepasses": [
            {
                "id": gp.id,
                "student_name": gp.student.name,
                "college_id": gp.student.college_id,
                "department": gp.student.department,
                "year": gp.student.year,
                "section": gp.student.section,
                "reason": gp.reason,
                "parent_mobile": gp.parent_mobile,
                "status": gp.status,
                "created_at": gp.created_at.isoformat()
            }
            for gp in gatepasses
        ]
    }), 200


# =====================================================
# APPROVE GATEPASS → GENERATE QR FOR STUDENT
# =====================================================
@hod_bp.route("/gatepasses/approve/<int:gatepass_id>", methods=["PUT"])
@jwt_required()
def hod_approve(gatepass_id):

    hod_id = get_jwt_identity()
    hod = User.query.get(int(hod_id))

    if not hod or hod.role != "hod":
        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    gp = GatePass.query.get(gatepass_id)

    if not gp or gp.status != "PendingHOD":
        return jsonify({
            "success": False,
            "message": "Gatepass not ready for approval"
        }), 400

    # =========================
    # UPDATE STATUS TO APPROVED
    # =========================
    gp.status = "Approved"
    gp.hod_id = hod.id

    # Reset usage flags
    gp.is_used = False
    gp.used_at = None

    # =========================
    # GENERATE QR TOKEN (10 MIN VALID)
    # =========================
    expiry_time = datetime.utcnow() + timedelta(minutes=10)

    qr_payload = {
        "gatepass_id": gp.id,
        "student_id": gp.student_id,
        "exp": expiry_time
    }

    gp.qr_token = jwt.encode(
        qr_payload,
        Config.QR_SECRET_KEY,
        algorithm=QR_ALGORITHM
    )

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Gatepass approved. QR generated for student."
    }), 200


# =====================================================
# REJECT GATEPASS
# =====================================================
@hod_bp.route("/gatepasses/reject/<int:gatepass_id>", methods=["PUT"])
@jwt_required()
def hod_reject(gatepass_id):

    hod_id = get_jwt_identity()
    hod = User.query.get(int(hod_id))

    if not hod or hod.role != "hod":
        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    gp = GatePass.query.get(gatepass_id)

    if not gp or gp.status != "PendingHOD":
        return jsonify({
            "success": False,
            "message": "Gatepass not rejectable"
        }), 400

    gp.status = "Rejected"
    gp.hod_id = hod.id

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Gatepass rejected successfully"
    }), 200