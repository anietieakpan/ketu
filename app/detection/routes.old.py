# routes.py
# app/detection/routes.py

from flask import render_template, Response, jsonify, request, send_from_directory, current_app
from app.detection import bp
from app.detection.detector import LicensePlateDetector
import cv2
import numpy as np
import traceback
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from app.database.factory import DatabaseFactory
import pytz
import logging

logger = logging.getLogger(__name__)

def get_detector():
    if 'detector' not in current_app.extensions:
        detector = LicensePlateDetector(DatabaseFactory)
        detector.initialize_databases()
        current_app.extensions['detector'] = detector
    return current_app.extensions['detector']


# Existing routes remain unchanged
@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/video_feed')
def video_feed():
    return Response(generate_frames(current_app._get_current_object()), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No video file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'success': 'Video uploaded successfully', 'filepath': filepath})

@bp.route('/start_video', methods=['POST'])
def start_video():
    try:
        video_path = request.json.get('videoPath')
        if not video_path:
            return jsonify({'error': 'No video path provided'}), 400
        
        detector = get_detector()        
        detector.start_video_capture(video_path)
        return jsonify({'success': 'Video started'})
    except Exception as e:
        return jsonify({'error': f'Error starting video: {str(e)}'}), 500

@bp.route('/stop_video')
def stop_video():
    detector = get_detector()  
    detector.stop_video_capture()
    return jsonify({'success': 'Video stopped'})

# New or updated routes for vehicle detection features
@bp.route('/detected_plates')
def detected_plates():
    """Get all detected plates with vehicle details"""
    detector = get_detector()
    plates = detector.get_detected_plates()
    return jsonify(plates)

@bp.route('/recent_detections')
def get_recent_detections():
    """Get recent detections with vehicle details"""
    try:
        # Get query parameters with defaults
        hours = request.args.get('hours', default=24, type=int)
        include_vehicle = request.args.get('include_vehicle', default=True, type=bool)
        
        # Calculate time range
        end_time = datetime.now(pytz.UTC)
        start_time = end_time - timedelta(hours=hours)
        
        # Get database instance
        db = DatabaseFactory.get_database('postgres')
        
        # Get detections
        detections = db.get_detections(
            start_time=start_time,
            end_time=end_time,
            include_vehicle_details=include_vehicle
        )
        
        return jsonify({
            'status': 'success',
            'count': len(detections),
            'detections': detections
        })
        
    except Exception as e:
        logger.error(f"Error getting recent detections: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
        
@bp.route('/vehicle/statistics')
def get_vehicle_statistics():
    """Get aggregated vehicle detection statistics"""
    try:
        db = DatabaseFactory.get_database('postgres')
        stats = db.get_vehicle_statistics()
        
        return jsonify({
            'status': 'success',
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting vehicle statistics: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/vehicle/search')
def search_vehicles():
    """Search vehicles based on criteria"""
    try:
        # Get search parameters
        make = request.args.get('make')
        model = request.args.get('model')
        color = request.args.get('color')
        type_ = request.args.get('type')
        days = request.args.get('days', default=30, type=int)
        
        # Calculate time range
        end_time = datetime.now(pytz.UTC)
        start_time = end_time - timedelta(days=days)
        
        # Build query conditions
        conditions = []
        params = {'start_time': start_time, 'end_time': end_time}
        
        if make:
            conditions.append("vehicle_make = :make")
            params['make'] = make
        if model:
            conditions.append("vehicle_model = :model")
            params['model'] = model
        if color:
            conditions.append("vehicle_color = :color")
            params['color'] = color
        if type_:
            conditions.append("vehicle_type = :type")
            params['type'] = type_
        
        # Get database and execute search
        db = DatabaseFactory.get_database('postgres')
        vehicles = db.search_vehicles(conditions, params)
        
        return jsonify({
            'status': 'success',
            'count': len(vehicles),
            'vehicles': vehicles
        })
        
    except Exception as e:
        logger.error(f"Error searching vehicles: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
        
        
@bp.route('/vehicle/colors')
def get_vehicle_colors():
    """Get list of detected vehicle colors with counts"""
    try:
        db = DatabaseFactory.get_database('postgres')
        colors = db.get_vehicle_colors()
        
        return jsonify({
            'status': 'success',
            'colors': colors
        })
        
    except Exception as e:
        logger.error(f"Error getting vehicle colors: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/vehicle/makes')
def get_vehicle_makes():
    """Get hierarchical list of makes with their models"""
    try:
        db = DatabaseFactory.get_database('postgres')
        makes = db.get_vehicle_makes_and_models()
        
        return jsonify({
            'status': 'success',
            'makes': makes
        })
        
    except Exception as e:
        logger.error(f"Error getting vehicle makes: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
        


@bp.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image file selected'}), 400
    
    if file:
        try:
            image_stream = file.read()
            image_array = np.frombuffer(image_stream, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if image is None:
                return jsonify({'error': 'Failed to decode image'}), 400
            
            detector = get_detector()
            encoded_image, detections = detector.process_image(image)

            # encoded_image, detections = detector.process_image(image)
            
            if encoded_image is None:
                return jsonify({'error': 'Error processing image'}), 500
            
            
            return jsonify({
                'image': encoded_image,
                'detections': detections
            })
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            traceback.print_exc()
            return jsonify({'error': f'Error processing image: {str(e)}'}), 500

            
@bp.route('/start_camera')
def start_camera():
    try:
        detector = get_detector()  
        detector.start_camera_capture()
        return jsonify({'success': 'Camera started'})
    except Exception as e:
        return jsonify({'error': f'Error starting camera: {str(e)}'}), 500

@bp.route('/stop_camera')
def stop_camera():
    detector = get_detector()  
    detector.stop_camera_capture()
    return jsonify({'success': 'Camera stopped'})

@bp.route('/camera_feed')
def camera_feed():
    detector = get_detector() 
    def generate():
        # detector = get_detector() 
        while detector.is_processing:
            frame = detector.get_camera_frame()
            if frame is None:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


# ... (include all other routes from the original app.py)

@bp.route('/update_config', methods=['POST'])
def update_config():
    data = request.json
    detector = get_detector()  
    detector.update_config(data)
    valid_keys = ['FRAME_SKIP', 'RESIZE_WIDTH', 'RESIZE_HEIGHT', 'CONFIDENCE_THRESHOLD', 'MAX_DETECTIONS_PER_FRAME', 'PROCESS_EVERY_N_SECONDS']
    
    for key, value in data.items():
        if key in valid_keys:
            current_app.config[key] = value
    
    return jsonify({"message": "Configuration updated successfully"})


@bp.route('/get_config')
def get_config():
    config = {
        'FRAME_SKIP': current_app.config['FRAME_SKIP'],
        'RESIZE_WIDTH': current_app.config['RESIZE_WIDTH'],
        'RESIZE_HEIGHT': current_app.config['RESIZE_HEIGHT'],
        'CONFIDENCE_THRESHOLD': current_app.config['CONFIDENCE_THRESHOLD'],
        'MAX_DETECTIONS_PER_FRAME': current_app.config['MAX_DETECTIONS_PER_FRAME'],
        'PROCESS_EVERY_N_SECONDS': current_app.config['PROCESS_EVERY_N_SECONDS']
    }
    return jsonify(config)



@bp.route('/recent_detections')
def recent_detections():
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)  # Get detections from the last hour
    
    timeseries_db = DatabaseFactory.get_database('timeseries')
    detections = timeseries_db.get_detections(start_time, end_time)
    
    return jsonify(detections)


@bp.route('/test_db_insert')
def test_db_insert():
    timeseries_db = DatabaseFactory.get_database('timeseries')
    timeseries_db.connect()
    
    test_data = {
        'text': 'TEST123',
        'confidence': 0.95,
        'timestamp': datetime.now()
    }
    
    try:
        timeseries_db.insert_detection(test_data)
        return jsonify({'status': 'success', 'message': 'Test data inserted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        timeseries_db.disconnect()
        
        
@bp.route('/test_static')
def test_static():
    """Test route to verify static files are loading"""
    return """
    <html>
        <head>
            <link rel="stylesheet" href="/static/css/styles.css">
        </head>
        <body>
            <h1>Static File Test</h1>
            <script src="/static/js/application.js"></script>
            <div id="status"></div>
            <script>
                document.getElementById('status').textContent = 'JavaScript loaded successfully!';
            </script>
        </body>
    </html>
    """

        
@bp.route('/db_info')
def db_info():
    timeseries_db = DatabaseFactory.get_database('timeseries')
    info = {
        'url': timeseries_db.url,
        'org': timeseries_db.org,
        'bucket': timeseries_db.bucket
    }
    return jsonify(info)


# Add this to app/detection/routes.py

@bp.errorhandler(Exception)
def handle_error(error):
    """Global error handler for the blueprint"""
    logger.error(f"Error in detection routes: {str(error)}", exc_info=True)
    return jsonify({
        'status': 'error',
        'message': str(error)
    }), 500

def get_db():
    """Get database instance with error handling"""
    try:
        db = DatabaseFactory.get_database('postgres')
        if db is None:
            raise RuntimeError("Failed to get database instance")
        return db
    except Exception as e:
        logger.error(f"Error getting database: {str(e)}")
        raise

@bp.route('/vehicle/makes', methods=['GET'])
def get_vehicle_makes():
    """Get hierarchical list of makes with their models"""
    try:
        db = get_db()
        makes = db.get_vehicle_makes_and_models()
        
        return jsonify({
            'status': 'success',
            'makes': makes
        })
        
    except Exception as e:
        logger.error(f"Error getting vehicle makes: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
                   
                   

def generate():
    detector = get_detector()  
    try:
        while detector.is_processing:
            frame = detector.get_camera_frame()
            if frame is None:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        detector.stop_camera_capture()

                   
def generate_frames(app):
    with app.app_context():
        # current_app.app_context():
        detector = get_detector()
        try:
            while detector.is_processing:
                frame = detector.get_frame()
                if frame is None:
                    break
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        finally:
            detector.stop_video_capture()

            


