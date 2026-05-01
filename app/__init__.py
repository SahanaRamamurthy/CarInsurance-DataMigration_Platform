from flask import Flask
from flask_cors import CORS
from .routes import register_routes
import os


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "carinsure-secret-2024")
    CORS(app)
    register_routes(app)
    return app
