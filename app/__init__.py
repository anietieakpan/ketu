# app/__init__.py

from flask import Flask
from config import Config
import os
from influxdb_client import InfluxDBClient
import logging
from app.database import DatabaseFactory

import signal

def handle_broken_pipe(signum, frame):
    """Handle broken pipe errors gracefully"""
    sys.stderr.close()

# def create_app(config_class=Config):
#     # Add at the start of create_app function
#     signal.signal(signal.SIGPIPE, handle_broken_pipe)
    

logger = logging.getLogger(__name__)

def test_database_connections(app):
    """Test both database connections"""
    with app.app_context():
        # Test InfluxDB
        client = InfluxDBClient(
            url=Config.INFLUXDB_URL,
            token=Config.INFLUXDB_TOKEN,
            org=Config.INFLUXDB_ORG
        )
        try:
            health = client.health()
            if health.status == "pass":
                logger.info("Successfully connected to InfluxDB")
            else:
                logger.warning("Failed to connect to InfluxDB")
        except Exception as e:
            logger.error(f"Error connecting to InfluxDB: {e}")
        finally:
            client.close()

        # Test PostgreSQL
        try:
            postgres = DatabaseFactory.get_database('postgres')
            postgres.disconnect()
            logger.info("Successfully connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    signal.signal(signal.SIGPIPE, handle_broken_pipe)
    app = Flask(__name__, static_url_path='/static', static_folder='static')
    app.config.from_object(config_class)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.static_folder + '/js', exist_ok=True)
    os.makedirs(app.static_folder + '/css', exist_ok=True)

    # Initialize databases within application context
    with app.app_context():
        try:
            logger.info("Initializing databases")
            databases = DatabaseFactory.get_all_databases()
            if databases:
                logger.info("Databases initialized successfully")
                app.databases = databases
            else:
                logger.warning("Failed to initialize databases")
        except Exception as e:
            logger.error(f"Error during database initialization: {str(e)}", exc_info=True)

    # Register blueprints
    from app.detection import bp as detection_bp
    app.register_blueprint(detection_bp)

    # Test database connections
    test_database_connections(app)

    return app