# from flask import Blueprint, jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity

# from models import User, GatePass

# # =================================================
# # BLUEPRINT (NO url_prefix, NO CORS HERE)
# # =================================================
# student_bp = Blueprint("student_bp", __name__)

# # =================================================
# # STUDENT PROFILE (DASHBOARD HEADER)
# # =================================================
# @student_bp.route("/profile", methods=["GET"])
# @jwt_required()
# def profile():
#     try:
#         student_id = int(get_jwt_identity())
#     except (TypeError, ValueError):
#         return jsonify({
#             "success": False,
#             "message": "Invalid or expired token"
#         }), 401

#     student = User.query.get(student_id)

#     if not student or student.role != "student":
#         return jsonify({
#             "success": False,
#             "message": "Access denied"
#         }), 403

#     return jsonify({
#         "success": True,
#         "user": {
#             "name": student.name,
#             "college_id": student.college_id,
#             "department": student.department,
#             "year": student.year,
#             "section": student.section
#         }
#     }), 200


# # =================================================
# # STUDENT GATEPASS STATUS
# # =================================================
# @student_bp.route("/status", methods=["GET"])
# @jwt_required()
# def student_status():
#     try:
#         student_id = int(get_jwt_identity())
#     except (TypeError, ValueError):
#         return jsonify({
#             "success": False,
#             "message": "Invalid or expired token"
#         }), 401

#     student = User.query.get(student_id)

#     if not student or student.role != "student":
#         return jsonify({
#             "success": False,
#             "message": "Access denied"
#         }), 403

#     gatepasses = (
#         GatePass.query
#         .filter(GatePass.student_id == student.id)
#         .order_by(GatePass.created_at.desc())
#         .all()
#     )

#     return jsonify({
#         "success": True,
#         "gatepasses": [
#             {
#                 "id": gp.id,
#                 "reason": gp.reason,
#                 "status": gp.status,
#                 "created_at": gp.created_at.isoformat(),

#                 # QR is visible ONLY after HOD approval
#                 "qr_token": gp.qr_token if gp.status in ["PendingSecurity", "Out"] else None
#             }
#             for gp in gatepasses
#         ]
#     }), 200









from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, GatePass

student_bp = Blueprint("student_bp", __name__)


# =================================================
# STUDENT PROFILE
# =================================================
@student_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():

    student_id = int(get_jwt_identity())
    student = User.query.get(student_id)

    if not student or student.role != "student":
        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    return jsonify({
        "success": True,
        "user": {
            "name": student.name,
            "college_id": student.college_id,
            "department": student.department,
            "year": student.year,
            "section": student.section
        }
    }), 200


# =================================================
# STUDENT GATEPASS STATUS / HISTORY
# =================================================
@student_bp.route("/status", methods=["GET"])
@jwt_required()
def student_status():

    student_id = int(get_jwt_identity())
    student = User.query.get(student_id)

    if not student or student.role != "student":
        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    gatepasses = (
        GatePass.query
        .filter(GatePass.student_id == student.id)
        .order_by(GatePass.created_at.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "gatepasses": [
            {
                "id": gp.id,
                "reason": gp.reason,
                "status": gp.status,
                "created_at": gp.created_at.isoformat(),
                "is_used": gp.is_used,

                # QR visible only when approved and not used
                "qr_token": gp.qr_token if gp.status == "Approved" else None
            }
            for gp in gatepasses
        ]
    }), 200