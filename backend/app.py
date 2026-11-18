import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from database import db
from models import User, Trek, Booking
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if type(dbapi_connection).__module__ == "sqlite3":
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

# Import route blueprints
from routes.auth_routes import auth_bp
from routes.trek_routes import trek_bp
from routes.booking_routes import booking_bp
from routes.staff_routes import staff_bp
from routes.admin_routes import admin_bp

FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for Vue SPA
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize Extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Custom JWT Error Handlers
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({"error": "Missing or invalid token. Please log in."}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({"error": "Signature verification failed. Please log in again."}), 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired. Please log in again."}), 401

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(trek_bp, url_prefix="/api/treks")
    app.register_blueprint(booking_bp, url_prefix="/api/bookings")
    app.register_blueprint(staff_bp, url_prefix="/api/staff")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # Serve Built Vue 3 Single Page Application
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        if path.startswith("api/"):
            return jsonify({"error": "Endpoint not found"}), 404
        
        file_path = os.path.join(FRONTEND_DIST, path)
        if path != "" and os.path.exists(file_path):
            return send_from_directory(FRONTEND_DIST, path)
            
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return send_from_directory(FRONTEND_DIST, "index.html")
            
        return jsonify({
            "service": "Trekking Management Application API (V2)",
            "status": "Running"
        }), 200

    return app

app = create_app()

def seed_admin():
    """Admin must pre-exist and be created programmatically after database creation."""
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                role="Admin",
                status="Approved",
                contact_details="admin@hikerssummit.com"
            )
            admin.set_password("admin@123")
            db.session.add(admin)
            db.session.commit()
            print("[Database] Programmatically created default Admin account (admin / admin@123)")

seed_admin()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
