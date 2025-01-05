# detector.py

# from app.models.detection import Detection
# from app import db

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
from picamera2 import Picamera2
from flask import current_app
import time

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

        self.frame_count = 0
        self.last_process_time = 0
        self.frame_skip = 2
        self.resize_width = 640
        self.resize_height = 480
        self.confidence_threshold = 0.5
        self.max_detections_per_frame = 5
        self.process_every_n_seconds = 1


    
    # def process_frame(self, frame, frame_size=None):
    #     try:
    #         self.frame_count += 1
    #         current_time = time.time()

    #         if (self.frame_count % current_app.config['FRAME_SKIP'] != 0 or
    #             current_time - self.last_process_time < current_app.config['PROCESS_EVERY_N_SECONDS']):
    #             return frame, []

    #         self.last_process_time = current_time

    #         if frame_size:
    #             frame = cv2.resize(frame, frame_size)
    #         else:
    #             frame = cv2.resize(frame, (current_app.config['RESIZE_WIDTH'], current_app.config['RESIZE_HEIGHT']))

    #         temp_frame_path = str(self.temp_dir / "temp_frame.jpg")
    #         cv2.imwrite(temp_frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 80])

    #         results = self.detector([temp_frame_path])
    #         (images, bboxs, points, zones,
    #         region_ids, region_names,
    #         count_lines, confidences, texts) = unzip(results)

    #         visualization = frame.copy()
    #         detections = []

    #         if bboxs and len(bboxs[0]) > 0:
    #             for i, bbox in enumerate(bboxs[0][:current_app.config['MAX_DETECTIONS_PER_FRAME']]):
    #                 x1, y1, x2, y2 = map(int, bbox[:4])
    #                 det_confidence = float(bbox[4])

    #                 if det_confidence < current_app.config['CONFIDENCE_THRESHOLD']:
    #                     continue

    #                 cv2.rectangle(visualization, (x1, y1), (x2, y2), (0, 255, 0), 3)

    #                 if texts and len(texts[0]) > i:
    #                     text = texts[0][i]
    #                 if isinstance(text, list):
    #                     text = ' '.join(text)

    #                 detection_info = {
    #                     'text': text,
    #                     'confidence': det_confidence,
    #                     'bbox': (x1, y1, x2, y2)
    #                 }
    #                 detections.append(detection_info)

    #                 label = f"{text} ({det_confidence:.2f})"
    #                 text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
    #                 cv2.rectangle(visualization,
    #                             (x1, y1 - text_size[1] - 10),
    #                             (x1 + text_size[0], y1),
    #                             (0, 255, 0),
    #                             -1)

    #                 cv2.putText(visualization,
    #                           label,
    #                           (x1, y1 - 10),
    #                           cv2.FONT_HERSHEY_SIMPLEX,
    #                           1.0,
    #                           (0, 0, 0),
    #                           2)

    #         return visualization, detections
    #     except Exception as e:
    #         print(f"Error in process_frame: {str(e)}")
    #         traceback.print_exc()
    #         return frame.copy(), []
        
        
        
    # def process_frame(self, frame, frame_size=None):
    #     try:
    #         if frame_size:
    #             frame = cv2.resize(frame, frame_size)
        
    #         temp_frame_path = str(self.temp_dir / "temp_frame.jpg")
    #         cv2.imwrite(temp_frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        
    #         results = self.detector([temp_frame_path])
    #         (images, bboxs, points, zones,
    #         region_ids, region_names,
    #         count_lines, confidences, texts) = unzip(results)

    #         visualization = frame.copy()
    #         detections = []

    #         if bboxs and len(bboxs[0]) > 0:
    #             for i, bbox in enumerate(bboxs[0]):
    #                 x1, y1, x2, y2 = map(int, bbox[:4])
    #                 det_confidence = float(bbox[4])

    #                 cv2.rectangle(visualization, (x1, y1), (x2, y2), (0, 255, 0), 3)

    #                 if texts and len(texts[0]) > i:
    #                     text = texts[0][i]
    #                     if isinstance(text, list):
    #                         text = ' '.join(text)
                    
    #                     detection_info = {
    #                         'text': text,
    #                         'confidence': det_confidence,
    #                         'bbox': (x1, y1, x2, y2)
    #                     }
    #                     detections.append(detection_info)

    #                     label = f"{text} ({det_confidence:.2f})"
    #                     text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]

    #                     cv2.rectangle(visualization,
    #                             (x1, y1 - text_size[1] - 10),
    #                             (x1 + text_size[0], y1),
    #                             (0, 255, 0),
    #                             -1)
                    
    #                     cv2.putText(visualization,
    #                           label,
    #                           (x1, y1 - 10),
    #                           cv2.FONT_HERSHEY_SIMPLEX,
    #                           1.0,
    #                           (0, 0, 0),
    #                           2)

    #         return visualization, detections

    #     except Exception as e:
    #         print(f"Error in process_frame: {str(e)}")
    #         traceback.print_exc()
    #         return frame.copy(), []
        
        
    
    def process_frame(self, frame, frame_size=None):
        try:
            if frame_size:
                frame = cv2.resize(frame, frame_size)
            else:
                frame = cv2.resize(frame, (self.resize_width, self.resize_height))

            temp_frame_path = str(self.temp_dir / "temp_frame.jpg")
            cv2.imwrite(temp_frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 80])

            results = self.detector([temp_frame_path])
            (images, bboxs, points, zones,
            region_ids, region_names,
            count_lines, confidences, texts) = unzip(results)

            visualization = frame.copy()
            detections = []

            if bboxs and len(bboxs[0]) > 0:
                for i, bbox in enumerate(bboxs[0][:self.max_detections_per_frame]):
                    x1, y1, x2, y2 = map(int, bbox[:4])
                    det_confidence = float(bbox[4])

                    if det_confidence < self.confidence_threshold:
                        continue

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
    
        self.frame_count += 1
        current_time = time.time()
        
        
        # processed_frame = frame
        detections = []
        

        if (self.frame_count % self.frame_skip == 0 and
            current_time - self.last_process_time >= self.process_every_n_seconds):
                self.last_process_time = current_time
                target_width = self.resize_width
                target_height = int(self.frame_height * (target_width / self.frame_width))
                frame_size = (target_width, target_height)
                processed_frame, detections = self.process_frame(frame, frame_size)
        
        if detections:
            for det in detections:
                if not any(existing['text'] == det['text'] for existing in self.detected_plates):
                    self.detected_plates.append(det)
        else:
            processed_frame = frame

        ret, jpeg = cv2.imencode('.jpg', processed_frame)
        return jpeg.tobytes()
    
    

    def stop_video_capture(self):
        if self.cap:
            self.cap.release()
        self.is_processing = False

    def get_detected_plates(self):
        return self.detected_plates
    
    

    def start_camera_capture(self):
        if hasattr(self, 'picam2') and self.picam2 is not None:
            print("Camera already initialized, stopping previous instance")
            self.stop_camera_capture()
    
        try:
            self.detected_plates = []
            self.picam2 = Picamera2()
            print("Picamera2 instance created")
            self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
            print("Camera configured")
            self.picam2.start()
            print("Camera started")
            self.is_processing = True
            print("Camera capture started successfully")
            return self
        except Exception as e:
            print(f"Error in start_camera_capture: {str(e)}")
            self.picam2 = None
            raise
        
        


    def get_camera_frame(self):
        if not self.is_processing:
            return None

        frame = self.picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

        self.frame_count += 1
        current_time = time.time()

        processed_frame = frame
        detections = []

        if (self.frame_count % self.frame_skip == 0 and
            current_time - self.last_process_time >= self.process_every_n_seconds):
            self.last_process_time = current_time
            processed_frame, detections = self.process_frame(frame)

        if detections:
            for det in detections:
                if not any(existing['text'] == det['text'] for existing in self.detected_plates):
                    self.detected_plates.append(det)

        ret, jpeg = cv2.imencode('.jpg', processed_frame)
        return jpeg.tobytes()



        
    def stop_camera_capture(self):
        if hasattr(self, 'picam2'):
            try:
                self.picam2.stop()
                self.picam2.close()
            except Exception as e:
                print(f"Error stopping camera: {str(e)}")
        self.is_processing = False
        self.picam2 = None  # Ensure the picam2 attribute is cleared
        
        
    def update_config(self, config):
        if 'FRAME_SKIP' in config:
            self.frame_skip = config['FRAME_SKIP']
        if 'RESIZE_WIDTH' in config:
            self.resize_width = config['RESIZE_WIDTH']
        if 'RESIZE_HEIGHT' in config:
            self.resize_height = config['RESIZE_HEIGHT']
        if 'CONFIDENCE_THRESHOLD' in config:
            self.confidence_threshold = config['CONFIDENCE_THRESHOLD']
        if 'MAX_DETECTIONS_PER_FRAME' in config:
            self.max_detections_per_frame = config['MAX_DETECTIONS_PER_FRAME']
        if 'PROCESS_EVERY_N_SECONDS' in config:
            self.process_every_n_seconds = config['PROCESS_EVERY_N_SECONDS']
