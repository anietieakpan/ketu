import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB limit
    
    FRAME_SKIP = 2
    RESIZE_WIDTH = 640
    RESIZE_HEIGHT = 480
    CONFIDENCE_THRESHOLD = 0.5
    MAX_DETECTIONS_PER_FRAME = 5
    PROCESS_EVERY_N_SECONDS = 1 
    
    # app.config['UPLOAD_FOLDER'] = 'uploads'
    # app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit