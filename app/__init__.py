from flask import Flask
from config import Config
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from app.detection import bp as detection_bp
    app.register_blueprint(detection_bp)

    return app

    
    # os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)