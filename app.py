from flask import Flask, render_template, Response, jsonify, request, send_from_directory
from detector import LicensePlateDetector
import cv2
import numpy as np
import traceback
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

detector = LicensePlateDetector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    try:
        while detector.is_processing:
            frame = detector.get_frame()
            if frame is None:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        detector.stop_video_capture()

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No video file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'success': 'Video uploaded successfully', 'filepath': filepath})

@app.route('/start_video', methods=['POST'])
def start_video():
    try:
        video_path = request.json.get('videoPath')
        if not video_path:
            return jsonify({'error': 'No video path provided'}), 400
        
        detector.start_video_capture(video_path)
        return jsonify({'success': 'Video started'})
    except Exception as e:
        return jsonify({'error': f'Error starting video: {str(e)}'}), 500

@app.route('/stop_video')
def stop_video():
    detector.stop_video_capture()
    return jsonify({'success': 'Video stopped'})

@app.route('/detected_plates')
def detected_plates():
    plates = detector.get_detected_plates()
    return jsonify(plates)

@app.route('/process_image', methods=['POST'])
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

            encoded_image, detections = detector.process_image(image)
            
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

            
@app.route('/start_camera')
def start_camera():
    try:
        detector.start_camera_capture()
        return jsonify({'success': 'Camera started'})
    except Exception as e:
        return jsonify({'error': f'Error starting camera: {str(e)}'}), 500

@app.route('/stop_camera')
def stop_camera():
    detector.stop_camera_capture()
    return jsonify({'success': 'Camera stopped'})

@app.route('/camera_feed')
def camera_feed():
    def generate():
        while detector.is_processing:
            frame = detector.get_camera_frame()
            if frame is None:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


# @app.route('/camera_status')
# def camera_status():
#     return jsonify({'is_active': detector.is_camera_active()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

