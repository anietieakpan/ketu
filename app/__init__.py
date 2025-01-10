from flask import Flask
from config import Config
import os
from influxdb_client import InfluxDBClient
import logging
from app.database.factory import DatabaseFactory

def test_influxdb_connection():
    client = InfluxDBClient(
        url=Config.INFLUXDB_URL,
        token=Config.INFLUXDB_TOKEN,
        org=Config.INFLUXDB_ORG
    )
    try:
        health = client.health()
        if health.status == "pass":
            print("Successfully connected to InfluxDB")
        else:
            print("Failed to connect to InfluxDB")
    except Exception as e:
        print(f"Error connecting to InfluxDB: {e}")
    finally:
        client.close()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    logging.basicConfig(level=logging.INFO)
    
    with app.app_context():
        try:
            logging.info("Iniitializing databases")
            databases = DatabaseFactory.get_all_databases()
            if databases:
                logging.info("Databases initialized successfully")
                app.databases = databases
            else:
                logging.warning("Failed to initialize databases")
        except Exception as e:
            logging.error(f"Error during database initialization: {str(e)}", exc_info=True)
            
            

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    if not all([app.config.get('INFLUXDB_URL'), 
                app.config.get('INFLUXDB_TOKEN'),
                app.config.get('INFLUXDB_ORG'),
                app.config.get('INFLUXDB_BUCKET')]):
        print("Warning: InfluxDB configuration is incomplete")

    from app.detection import bp as detection_bp
    app.register_blueprint(detection_bp)
    
    # test influxdb connection
    test_influxdb_connection()

    return app

    