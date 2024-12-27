import cv2
import numpy as np
import time

def test_x11_opencv():
    try:
        # Create a simple image
        print("Creating test image...")
        img = np.zeros((300,300,3), dtype=np.uint8)
        img[:] = (255, 0, 0)  # Blue image
        
        print("Creating window...")
        cv2.namedWindow('X11 Test', cv2.WINDOW_NORMAL)
        
        print("Displaying image...")
        cv2.imshow('X11 Test', img)
        
        print("Window should be visible now. Waiting 5 seconds...")
        time.sleep(5)
        
        print("Cleaning up...")
        cv2.destroyAllWindows()
        
        print("Test completed successfully")
        return True
        
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    test_x11_opencv()