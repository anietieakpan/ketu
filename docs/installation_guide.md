# Complete Installation Guide

## Prerequisites

### Hardware Requirements
- Raspberry Pi 5 (8GB RAM recommended)
- Raspberry Pi Camera Module V3
- Storage:
  - System: 32GB+ microSD (Class 10)
  - Database: SSD recommended
- Active cooling solution
- Power Supply: 5V/5A USB-C

### Software Requirements
- Raspberry Pi OS (64-bit)
- Python 3.8+
- OpenCV
- SQLite3

## Installation Steps

### 1. Base System Setup
```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install system dependencies
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-opencv \
    sqlite3 \
    libopencv-dev \
    python3-picamera2 \
    git \
    cmake \
    build-essential \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libhdf5-dev \
    libhdf5-serial-dev \
    libcblas-dev \
    libatlas-base-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev
```

### 2. Project Installation
```bash
# Clone repository
git clone https://github.com/username/license-plate-detector.git
cd license-plate-detector

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Verify installation
python3 -c "import cv2; print(cv2.__version__)"
python3 -c "import numpy; print(numpy.__version__)"
```

### 3. Database Setup
```bash
# Create data directory
sudo mkdir -p /var/lib/license-plate-detector/data
sudo chown -R pi:pi /var/lib/license-plate-detector

# Initialize database
python3 -m src.cli init-db

# Verify database
sqlite3 /var/lib/license-plate-detector/data/plates.db \
    "SELECT name FROM sqlite_master WHERE type='table';"
```

### 4. Camera Setup
```bash
# Enable camera interface
sudo raspi-config nonint do_camera 0

# Test camera
libcamera-hello
libcamera-jpeg -o test.jpg

# Verify camera permissions
sudo usermod -a -G video $USER
groups | grep video

# Test camera in Python
python3 -c """
from picamera2 import Picamera2
picam2 = Picamera2()
picam2.start()
print('Camera initialized successfully')
picam2.stop()
"""
```

### 5. Service Configuration

#### Create Service File
```bash
sudo tee /etc/systemd/system/plate-detector.service << EOF
[Unit]
Description=License Plate Detection Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/license-plate-detector
Environment="PYTHONPATH=/opt/license-plate-detector"
Environment="CONFIG_PATH=/etc/license-plate-detector/config.yaml"
ExecStart=/opt/license-plate-detector/venv/bin/python -m src.cli run
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

#### Configure Service
```bash
# Create configuration directory
sudo mkdir -p /etc/license-plate-detector
sudo chown -R pi:pi /etc/license-plate-detector

# Copy configuration
sudo cp config/config.yaml /etc/license-plate-detector/

# Enable and start service
sudo systemctl enable plate-detector
sudo systemctl start plate-detector
sudo systemctl status plate-detector
```

### 6. Logging Setup
```bash
# Create log directory
sudo mkdir -p /var/log/license-plate-detector
sudo chown -R pi:pi /var/log/license-plate-detector

# Configure log rotation
sudo tee /etc/logrotate.d/plate-detector << EOF
/var/log/license-plate-detector/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 pi pi
}
EOF
```

### 7. Security Configuration
```bash
# Set file permissions
sudo chmod 750 /opt/license-plate-detector
sudo chmod 640 /etc/license-plate-detector/config.yaml
sudo chmod 660 /var/log/license-plate-detector/*.log

# Configure firewall
sudo apt install -y ufw
sudo ufw allow ssh
sudo ufw allow 8080/tcp  # Web interface
sudo ufw enable
```

## Post-Installation Verification

### 1. System Checks
```python
def verify_installation():
    """Verify system installation"""
    checks = [
        check_python_version(),
        check_dependencies(),
        check_camera_access(),
        check_database_access(),
        check_service_status(),
        check_logging_setup()
    ]
    return all(checks)
```

### 2. Performance Testing
```bash
# Run system benchmark
python3 -m src.cli benchmark

# Monitor system resources
htop

# Check camera performance
python3 -m src.cli test-camera --duration 60

# Test database performance
python3 -m src.cli test-database
```

### 3. Error Checking
```bash
# Check system logs
sudo journalctl -u plate-detector -n 100

# Check application logs
tail -f /var/log/license-plate-detector/app.log

# Check for errors
grep ERROR /var/log/license-plate-detector/app.log
```

## Troubleshooting

### Common Installation Issues

1. Camera Issues
```bash
# Problem: Camera not detected
# Solution:
vcgencmd get_camera  # Check if camera is detected
sudo modprobe bcm2835-v4l2  # Load camera module
v4l2-ctl --list-devices  # List video devices
```

2. Database Issues
```bash
# Problem: Database permission errors
# Solution:
sudo chown -R pi:pi /var/lib/license-plate-detector
sudo chmod 750 /var/lib/license-plate-detector
sqlite3 /var/lib/license-plate-detector/data/plates.db "PRAGMA integrity_check;"
```

3. Service Issues
```bash
# Problem: Service fails to start
# Solution:
sudo systemctl status plate-detector  # Check status
sudo journalctl -u plate-detector -n 100  # Check logs
sudo systemctl restart plate-detector  # Restart service
```

4. Dependency Issues
```bash
# Problem: Missing dependencies
# Solution:
pip install --force-reinstall -r requirements.txt
pip check  # Check for dependency conflicts
python3 -m pip debug --verbose  # Debug pip issues
```

### Performance Issues

1. High CPU Usage
```bash
# Monitor CPU temperature
vcgencmd measure_temp

# Check process usage
top -u pi

# Adjust frame skip rate in config
```

2. Memory Issues
```bash
# Check memory usage
free -h

# Monitor memory
watch -n 1 "free -h"

# Adjust buffer sizes in config
```

3. Storage Issues
```bash
# Check disk usage
df -h

# Find large files
sudo find /var/lib/license-plate-detector -type f -size +100M

# Setup log rotation if needed
```

## Maintenance

### Regular Maintenance Tasks
```bash
# Daily checks
systemctl status plate-detector
df -h
free -h

# Weekly maintenance
sudo apt update && sudo apt upgrade -y
sqlite3 plates.db "VACUUM;"
find /var/log -name "*.gz" -mtime +14 -delete

# Monthly maintenance
pip install --upgrade -r requirements.txt
sudo apt autoremove
sudo apt clean
```

Would you like me to continue with completing the monitoring_optimization.md file?