# app/detection/vehicle_classifier.py

import cv2
import numpy as np
from typing import Dict, Optional, Tuple
import logging
import os
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class VehicleClassifier:
    """Service for classifying vehicle characteristics from images"""
    
    def __init__(self, confidence_threshold: float = 0.6):
        self.confidence_threshold = confidence_threshold
        # Store detected vehicle crops
        self.vehicle_images_path = Path("data/vehicle_images")
        self.vehicle_images_path.mkdir(parents=True, exist_ok=True)

    def process_vehicle_image(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict:
        """
        Process a vehicle image to extract make, model, color, etc.
        For now, returns mock data until ML model is integrated
        """
        try:
            x1, y1, x2, y2 = bbox
            vehicle_crop = image[y1:y2, x1:x2]
            
            # Save vehicle crop
            image_path = self._save_vehicle_image(vehicle_crop)
            
            # TODO: Replace with actual ML model predictions
            # This is a mock implementation
            mock_predictions = {
                'make': 'Unknown',
                'model': 'Unknown',
                'color': self._detect_dominant_color(vehicle_crop),
                'type': 'sedan',  # Default type
                'year': None,
                'confidence_scores': {
                    'make': 0.0,
                    'model': 0.0,
                    'color': 0.8,
                    'type': 0.7
                },
                'image_path': str(image_path) if image_path else None
            }
            
            return mock_predictions
            
        except Exception as e:
            logger.error(f"Error processing vehicle image: {str(e)}")
            return None

    def _detect_dominant_color(self, image: np.ndarray) -> str:
        """Detect dominant color of vehicle"""
        try:
            # Resize for faster processing
            small = cv2.resize(image, (64, 64))
            pixels = small.reshape(-1, 3)
            
            # Calculate average color
            avg_color = np.mean(pixels, axis=0)
            
            # Simple color classification
            colors = {
                'white': [255, 255, 255],
                'black': [0, 0, 0],
                'red': [255, 0, 0],
                'blue': [0, 0, 255],
                'green': [0, 255, 0],
                'silver': [192, 192, 192],
                'gray': [128, 128, 128]
            }
            
            # Find closest color
            min_dist = float('inf')
            closest_color = 'unknown'
            
            for color_name, color_value in colors.items():
                dist = np.linalg.norm(avg_color - color_value)
                if dist < min_dist:
                    min_dist = dist
                    closest_color = color_name
                    
            return closest_color
            
        except Exception as e:
            logger.error(f"Error detecting color: {str(e)}")
            return 'unknown'

    def _save_vehicle_image(self, image: np.ndarray) -> Optional[Path]:
        """Save vehicle crop image"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = self.vehicle_images_path / f"vehicle_{timestamp}.jpg"
            
            cv2.imwrite(str(image_path), image)
            return image_path
            
        except Exception as e:
            logger.error(f"Error saving vehicle image: {str(e)}")
            return None