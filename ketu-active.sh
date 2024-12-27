PyQtWebEngine==5.15.6
PyQt5==5.15.10
gmpy2
spyder




# Get your venv site-packages path
SITE_PACKAGES=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")

# Create symlinks
sudo ln -s /usr/lib/python3/dist-packages/picamera2 $SITE_PACKAGES/
sudo ln -s /usr/lib/python3/dist-packages/libcamera $SITE_PACKAGES/



# In _process_camera function, before detector.process_frame:
frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)