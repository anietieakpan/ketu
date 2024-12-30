import cv2
import numpy as np
from nomeroff_net import pipeline
from nomeroff_net.tools import unzip
from pathlib import Path
import tempfile
import warnings
import os
import base64
import traceback

warnings.filterwarnings('ignore', category=UserWarning, message='Implicit dimension choice for softmax.*')
warnings.filterwarnings('ignore', category=UserWarning, message='Creating a tensor from a list of numpy.ndarrays is extremely slow.*')

class LicensePlateDetector:
    def __init__(self):
        Path('output').mkdir(exist_ok=True)
        print("Loading pipeline...")
        self.detector = pipeline("number_plate_detection_and_reading", image_loader="opencv")
        self.temp_dir = Path(tempfile.mkdtemp())
        
        self.cap = None
        self.current_frame = None
        self.is_processing = False
        self.detected_plates = []

    def process_frame(self, frame, frame_size=None):
        try:
            if frame_size:
                frame = cv2.resize(frame, frame_size)
            
            temp_frame_path = str(self.temp_dir / "temp_frame.jpg")
            cv2.imwrite(temp_frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            
            results = self.detector([temp_frame_path])
            (images, bboxs, points, zones,
             region_ids, region_names,
             count_lines, confidences, texts) = unzip(results)

            visualization = frame.copy()
            detections = []

            if bboxs and len(bboxs[0]) > 0:
                for i, bbox in enumerate(bboxs[0]):
                    x1, y1, x2, y2 = map(int, bbox[:4])
                    det_confidence = float(bbox[4])

                    cv2.rectangle(visualization, (x1, y1), (x2, y2), (0, 255, 0), 3)

                    if texts and len(texts[0]) > i:
                        text = texts[0][i]
                        if isinstance(text, list):
                            text = ' '.join(text)
                        
                        detection_info = {
                            'text': text,
                            'confidence': det_confidence,
                            'bbox': (x1, y1, x2, y2)
                        }
                        detections.append(detection_info)

                        label = f"{text} ({det_confidence:.2f})"
                        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]

                        cv2.rectangle(visualization,
                                    (x1, y1 - text_size[1] - 10),
                                    (x1 + text_size[0], y1),
                                    (0, 255, 0),
                                    -1)
                        
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

    def process_image(self, image):
        try:
            temp_image_path = str(self.temp_dir / "temp_image.jpg")
            cv2.imwrite(temp_image_path, image)

            results = self.detector([temp_image_path])
            (images, bboxs, points, zones,
             region_ids, region_names,
             count_lines, confidences, texts) = unzip(results)

            visualization = image.copy()
            detections = []

            if bboxs and len(bboxs[0]) > 0:
                for i, bbox in enumerate(bboxs[0]):
                    x1, y1, x2, y2 = map(int, bbox[:4])
                    det_confidence = float(bbox[4])

                    cv2.rectangle(visualization, (x1, y1), (x2, y2), (0, 255, 0), 3)

                    if texts and len(texts[0]) > i:
                        text = texts[0][i]
                        if isinstance(text, list):
                            text = ' '.join(text)
                        
                        detection_info = {
                            'text': text,
                            'confidence': det_confidence,
                            'bbox': (x1, y1, x2, y2)
                        }
                        detections.append(detection_info)

                        label = f"{text} ({det_confidence:.2f})"
                        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]

                        cv2.rectangle(visualization,
                                    (x1, y1 - text_size[1] - 10),
                                    (x1 + text_size[0], y1),
                                    (0, 255, 0),
                                    -1)
                        
                        cv2.putText(visualization,
                                  label,
                                  (x1, y1 - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX,
                                  1.0,
                                  (0, 0, 0),
                                  2)

            _, buffer = cv2.imencode('.jpg', visualization)
            encoded_image = base64.b64encode(buffer).decode('utf-8')

            return encoded_image, detections

        except Exception as e:
            print(f"Error in process_image: {str(e)}")
            traceback.print_exc()
            return None, []

    def start_video_capture(self, video_path):
        self.detected_plates = []

        if self.cap:
            self.cap.release()
        
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Started video capture. FPS: {self.fps}, Resolution: {self.frame_width}x{self.frame_height}")
        self.is_processing = True
        return self

    def get_frame(self):
        if not self.cap or not self.is_processing:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            self.is_processing = False
            return None
        
        target_width = 640
        target_height = int(self.frame_height * (target_width / self.frame_width))
        frame_size = (target_width, target_height)
        
        processed_frame, detections = self.process_frame(frame, frame_size)
        
        if detections:
            for det in detections:
                if not any(existing['text'] == det['text'] for existing in self.detected_plates):
                    self.detected_plates.append(det)
        
        ret, jpeg = cv2.imencode('.jpg', processed_frame)
        return jpeg.tobytes()

    def stop_video_capture(self):
        if self.cap:
            self.cap.release()
        self.is_processing = False

    def get_detected_plates(self):
        return self.detected_plates