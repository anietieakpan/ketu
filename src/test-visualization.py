import cv2
import numpy as np

# Test window
test_img = np.zeros((300,300,3), np.uint8)
cv2.imshow('Test', test_img)
cv2.waitKey(0)
cv2.destroyAllWindows()