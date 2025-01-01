import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB limit
    
    
    # app.config['UPLOAD_FOLDER'] = 'uploads'
    # app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit