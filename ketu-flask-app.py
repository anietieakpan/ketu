import cv2
import numpy as np
from nomeroff_net import pipeline
from nomeroff_net.tools import unzip
from pathlib import Path
import time
import tempfile
import warnings
import torch.nn.functional as functional
import os
import sys
import traceback
from flask import Flask, render_template, Response, jsonify

# Set environment variable for display
os.environ["QT_QPA_PLATFORM"] = "xcb"

# Suppress specific PyTorch warnings
warnings.filterwarnings('ignore', category=UserWarning, message='Implicit dimension choice for softmax.*')
warnings.filterwarnings('ignore', category=UserWarning, message='Creating a tensor from a list of numpy.ndarrays is extremely slow.*')

class LicensePlateDetector:
    def __init__(self):
        # Create output directory
        Path('output').mkdir(exist_ok=True)
        print("Loading pipeline...")
        self.detector = pipeline("number_plate_detection_and_reading", image_loader="opencv")
        # Create a temporary directory for frame processing
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Video capture and processing attributes
        self.cap = None
        self.current_frame = None
        self.is_processing = False
        self.detected_plates = []

    def process_frame(self, frame, frame_size=None):
        """Process a single frame and return the visualization and detections"""
        try:
            # Resize frame if specified
            if frame_size:
                frame = cv2.resize(frame, frame_size)
            
            # Save frame to temporary file
            temp_frame_path = str(self.temp_dir / "temp_frame.jpg")
            # Use lower JPEG quality for faster I/O
            cv2.imwrite(temp_frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            
            # Process with nomeroff-net
            results = self.detector([temp_frame_path])
            (images, bboxs, points, zones,
             region_ids, region_names,
             count_lines, confidences, texts) = unzip(results)

            # Create a copy for visualization
            visualization = frame.copy()
            detections = []

            # Draw the detections
            if bboxs and len(bboxs[0]) > 0:
                for i, bbox in enumerate(bboxs[0]):
                    # Get coordinates
                    x1 = int(bbox[0])
                    y1 = int(bbox[1])
                    x2 = int(bbox[2])
                    y2 = int(bbox[3])
                    det_confidence = float(bbox[4])

                    # Draw bounding box
                    cv2.rectangle(visualization, (x1, y1), (x2, y2), (0, 255, 0), 3)

                    # Get corresponding text
                    if texts and len(texts[0]) > i:
                        text = texts[0][i]
                        if isinstance(text, list):
                            text = ' '.join(text)
                        
                        # Store detection
                        detection_info = {
                            'text': text,
                            'confidence': det_confidence,
                            'bbox': (x1, y1, x2, y2)
                        }
                        detections.append(detection_info)

                        # Draw text with confidence
                        label = f"{text} ({det_confidence:.2f})"
                        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]

                        # Draw text background
                        cv2.rectangle(visualization,
                                    (x1, y1 - text_size[1] - 10),
                                    (x1 + text_size[0], y1),
                                    (0, 255, 0),
                                    -1)
                        
                        # Draw text
                        cv2.putText(visualization,
                                  label,
                                  (x1, y1 - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX,
                                  1.0,
                                  (0, 0, 0),
                                  2)

            return visualization, detections

        except Exception as e:
            print(f"Error in process_frame: {str(e)}")
            traceback.print_exc()
            return frame.copy(), []

    def start_video_capture(self, video_path):
        """Start video capture for streaming"""
        # Reset detected plates
        self.detected_plates = []

        # Release any existing capture
        if self.cap:
            self.cap.release()
        
        # Open the video file
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Started video capture. FPS: {self.fps}, Resolution: {self.frame_width}x{self.frame_height}")
        self.is_processing = True
        return self

    def get_frame(self):
        """Capture and process next frame"""
        if not self.cap or not self.is_processing:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            self.is_processing = False
            return None
        
        # Process the frame (resize to 640 width for performance)
        target_width = 640
        target_height = int(self.frame_height * (target_width / self.frame_width))
        frame_size = (target_width, target_height)
        
        processed_frame, detections = self.process_frame(frame, frame_size)
        
        # Store unique detections
        if detections:
            for det in detections:
                # Only add if not already in the list
                if not any(existing['text'] == det['text'] for existing in self.detected_plates):
                    self.detected_plates.append(det)
        
        # Encode the frame for streaming
        ret, jpeg = cv2.imencode('.jpg', processed_frame)
        return jpeg.tobytes()

    def stop_video_capture(self):
        """Stop video capture"""
        if self.cap:
            self.cap.release()
        self.is_processing = False

    def get_detected_plates(self):
        """Return list of detected plates"""
        return self.detected_plates

# Flask App
app = Flask(__name__)
detector = LicensePlateDetector()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    """Generate frames for streaming"""
    try:
        while detector.is_processing:
            frame = detector.get_frame()
            if frame is None:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        detector.stop_video_capture()

@app.route('/start_video')
def start_video():
    """Start video processing"""
    video_path = "/home/aniix/alprs/deneme.mp4"  # Update this path
    try:
        detector.start_video_capture(video_path)
        return "Video started"
    except Exception as e:
        return f"Error starting video: {str(e)}", 500

@app.route('/stop_video')
def stop_video():
    """Stop video processing"""
    detector.stop_video_capture()
    return "Video stopped"

@app.route('/detected_plates')
def detected_plates():
    """Get list of detected plates"""
    plates = detector.get_detected_plates()
    return jsonify(plates)

def create_html_template():
    """Create HTML template for the Flask app"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>License Plate Detection</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            max-width: 1000px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        #video-container {
            max-width: 100%;
            margin: 20px auto;
            border: 2px solid #333;
        }
        .controls {
            margin: 20px 0;
        }
        button {
            padding: 10px 20px;
            margin: 0 10px;
            font-size: 16px;
        }
        #plates-list {
            margin-top: 20px;
            text-align: left;
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
        }
    </style>
</head>
<body>
    <h1>License Plate Detection</h1>
    
    <div class="controls">
        <button onclick="startVideo()">Start Video</button>
        <button onclick="stopVideo()">Stop Video</button>
        <button onclick="refreshPlates()">Refresh Detected Plates</button>
    </div>

    <div id="video-container">
        <img id="video-feed" src="" alt="Video Stream">
    </div>

    <div id="plates-list">
        <h2>Detected Plates</h2>
        <ul id="plates-ul"></ul>
    </div>

    <script>
        const videoFeed = document.getElementById('video-feed');
        const platesUl = document.getElementById('plates-ul');

        function startVideo() {
            fetch('/start_video')
                .then(response => {
                    if (response.ok) {
                        videoFeed.src = '/video_feed';
                    }
                })
                .catch(error => console.error('Error:', error));
        }

        function stopVideo() {
            fetch('/stop_video')
                .then(response => {
                    if (response.ok) {
                        videoFeed.src = '';
                    }
                })
                .catch(error => console.error('Error:', error));
        }

        function refreshPlates() {
            fetch('/detected_plates')
                .then(response => response.json())
                .then(plates => {
                    // Clear existing list
                    platesUl.innerHTML = '';
                    
                    // Add new plates
                    plates.forEach(plate => {
                        const li = document.createElement('li');
                        li.textContent = `Plate: ${plate.text} (Confidence: ${plate.confidence.toFixed(2)})`;
                        platesUl.appendChild(li);
                    });
                })
                .catch(error => console.error('Error:', error));
        }

        // Automatically refresh plates every 5 seconds
        setInterval(refreshPlates, 5000);
    </script>
</body>
</html>
    """
    return html_content

# Save the HTML template
Path('templates').mkdir(exist_ok=True)
with open('templates/index.html', 'w') as f:
    f.write(create_html_template())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)