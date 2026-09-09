from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.admin import create_default_admin
from app.api import api_bp
from app.config import LocalDevelopmentConfig
from app.database import db


def create_app():
    app = Flask(__name__)
    
    app.config.from_object(LocalDevelopmentConfig)
    CORS(app) 
    jwt = JWTManager(app) 
    
    
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({"message": "Missing or invalid token"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({"message": "Invalid token"}), 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({"message": "Token has expired"}), 401
    
    db.init_app(app)
    app.register_blueprint(api_bp, url_prefix="/api")
    
    @app.route("/")
    def home():
        return "Server running"

    return app
    
app = create_app()
if __name__ == '__main__':
    
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")
            create_default_admin()
            print("Default admin created successfully!")
        except Exception as e:  # noqa: BLE001
            print(f"Error creating database: {e}")
    
    app.run(debug=True)
