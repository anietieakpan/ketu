# API Reference

## Core APIs

### Detection API
```python
class DetectionAPI:
    """
    Main detection API for license plate recognition
    
    Endpoints:
    - POST /detect: Process single image
    - POST /detect/stream: Process video stream
    - GET /detections: Get detection history
    """
    
    async def detect_plate(self, image):
        """
        Process single image for plate detection
        
        Args:
            image: np.ndarray of image data
            
        Returns:
            Dict containing detection results
        """
        pass
```

### Analysis API
```python
class AnalysisAPI:
    """
    Analysis API for pattern detection
    
    Endpoints:
    - GET /analysis/patterns: Get following patterns
    - POST /analysis/custom: Run custom analysis
    - GET /analysis/stats: Get analysis statistics
    """
    
    async def get_patterns(self, timeframe: str = '1h'):
        """
        Get following patterns for specified timeframe
        
        Args:
            timeframe: Time window for analysis
            
        Returns:
            List of detected patterns
        """
        pass
```

### Management API
```python
class ManagementAPI:
    """
    System management API
    
    Endpoints:
    - GET /system/status: Get system status
    - POST /system/config: Update configuration
    - GET /system/metrics: Get performance metrics
    """
    pass
```
