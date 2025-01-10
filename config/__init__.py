import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB limit

    
    # InfluxDB configuration
    INFLUXDB_URL = 'http://localhost:8086'
    INFLUXDB_TOKEN = '1boLA7YZq6dvUrc2Mlomus7dAJawm3ZbskadawaS1g5gb65fISVYNbUuVJ05cWhuiIDvKsw94UU-35fP5xHZaA=='
    INFLUXDB_ORG = 'ketu-ai'
    INFLUXDB_BUCKET = 'license_plate_detections'

    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///your_database.db'  #
    
    
    
    FRAME_SKIP = 2
    RESIZE_WIDTH = 640
    RESIZE_HEIGHT = 480
    CONFIDENCE_THRESHOLD = 0.5
    MAX_DETECTIONS_PER_FRAME = 5
    PROCESS_EVERY_N_SECONDS = 1 
    
    # app.config['UPLOAD_FOLDER'] = 'uploads'
    # app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit
    
    
    
#    INFLUXDB_URL = os.environ.get('INFLUXDB_URL') or 'http://localhost:8086'
#     INFLUXDB_TOKEN = os.environ.get('INFLUXDB_TOKEN') or '1boLA7YZq6dvUrc2Mlomus7dAJawm3ZbskadawaS1g5gb65fISVYNbUuVJ05cWhuiIDvKsw94UU-35fP5xHZaA=='
#     INFLUXDB_ORG = os.environ.get('INFLUXDB_ORG') or 'ketu-ai'
#     INFLUXDB_BUCKET = os.environ.get('INFLUXDB_BUCKET') or 'license_plate_detections' 