


  


    
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
