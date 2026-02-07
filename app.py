import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from models import db

from routes.auth_routes import auth_bp
from routes.gatepass_routes import gatepass_bp
from routes.student_routes import student_bp
from routes.faculty_routes import faculty_bp
from routes.hod_routes import hod_bp
from routes.security_routes import security_bp
from routes.notification_routes import notifications_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ==========================
    # CORS (CORRECT)
    # ==========================
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    # ==========================
    # EXTENSIONS
    # ==========================
    db.init_app(app)
    JWTManager(app)

    # ==========================
    # BLUEPRINTS
    # ==========================
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(gatepass_bp, url_prefix="/api/gatepass")
    app.register_blueprint(student_bp, url_prefix="/api/student")
    app.register_blueprint(faculty_bp, url_prefix="/api/faculty")
    app.register_blueprint(hod_bp, url_prefix="/api/hod")
    app.register_blueprint(security_bp, url_prefix="/api/security")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")

    # ==========================
    # HEALTH CHECK
    # ==========================
    @app.route("/", methods=["GET"])
    def home():
        return {"status": "Smart Gatepass Backend Running"}, 200

    return app


# ==========================
# RENDER ENTRY POINT
# ==========================
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)