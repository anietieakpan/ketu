# routes.py

from flask import render_template, Response, jsonify, request, send_from_directory, current_app
from app.detection import bp
from app.detection.detector import LicensePlateDetector
import cv2
import numpy as np
from flask import current_app
import traceback
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from app.database.factory import DatabaseFactory

def get_detector():
    if 'detector' not in current_app.extensions:
        detector = LicensePlateDetector(DatabaseFactory)
        detector.initialize_databases()
        current_app.extensions['detector'] = detector
        # current_app.extensions['detector'] = LicensePlateDetector()
    return current_app.extensions['detector']

# detector = LicensePlateDetector()

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

@bp.route('/detected_plates')
def detected_plates():
    detector = get_detector()
    plates = detector.get_detected_plates()
    return jsonify(plates)

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

        
@bp.route('/db_info')
def db_info():
    timeseries_db = DatabaseFactory.get_database('timeseries')
    info = {
        'url': timeseries_db.url,
        'org': timeseries_db.org,
        'bucket': timeseries_db.bucket
    }
    return jsonify(info)
                   
                   
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

            
# def generate_frames():
#     detector = get_detector()
#     try:
#         while detector.is_processing:
#             frame = detector.get_frame()
#             if frame is None:
#                 break
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#     finally:
#         detector.stop_video_capture()



