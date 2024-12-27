# Raspberry Pi Setup Guide

## Hardware Setup

### Required Components
- Raspberry Pi 5 (8GB RAM recommended)
- Raspberry Pi Camera Module V3
- USB-C Power Supply (5V/5A)
- MicroSD Card (32GB+ Class 10)
- Active Cooling Solution
- Case with camera mount
- (Optional) SSD for improved database performance

### Physical Installation

1. Camera Module Installation
```bash
# Power off Raspberry Pi
sudo shutdown -h now

# Physical Installation Steps:
1. Locate the camera connector on the Raspberry Pi
2. Gently lift the connector clip
3. Insert camera ribbon cable (blue side facing contacts)
4. Press connector clip down firmly
5. Route cable to avoid interference
```

2. Cooling Solution
```bash
# Install cooling components in this order:
1. Apply thermal paste to CPU
2. Attach heatsink
3. Mount cooling fan
4. Connect fan to GPIO pins (refer to pin diagram)

# Fan pin connections:
- Red wire: 5V (Pin 4)
- Black wire: Ground (Pin 6)
- Yellow wire (if present): GPIO 14 (Pin 8)
```

3. Storage Setup
```bash
# Format SSD (if using)
sudo fdisk -l
sudo mkfs.ext4 /dev/sda1

# Mount SSD
sudo mkdir /mnt/ssd
sudo mount /dev/sda1 /mnt/ssd

# Add to fstab for automatic mounting
sudo nano /etc/fstab
# Add line:
/dev/sda1 /mnt/ssd ext4 defaults,noatime 0 1
```

## Software Setup

### Operating System Installation

1. Download and Install OS
```bash
# Using Raspberry Pi Imager:
1. Download Raspberry Pi Imager
2. Insert MicroSD card
3. Select "Raspberry Pi OS (64-bit)"
4. Configure:
   - Enable SSH
   - Set username/password
   - Configure WiFi
   - Set locale settings
5. Write to SD card
```

2. Initial System Configuration
```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    python3-pip \
    python3-opencv \
    sqlite3 \
    libopencv-dev \
    python3-picamera2 \
    git \
    cmake \
    build-essential
```

### Camera Configuration

1. Enable Camera Interface
```bash
# Using raspi-config
sudo raspi-config
# Navigate to:
# Interface Options -> Camera -> Enable

# Reboot system
sudo reboot
```

2. Test Camera
```bash
# Basic camera test
libcamera-hello
libcamera-jpeg -o test.jpg

# Check camera status
vcgencmd get_camera

# Expected output:
# supported=1 detected=1
```

3. Camera Settings
```python
# Example camera configuration
from picamera2 import Picamera2

def setup_camera():
    camera = Picamera2()
    config = camera.create_preview_configuration(
        main={"size": (1920, 1080)},
        controls={
            "FrameRate": 30.0,
            "AwbEnable": True,
            "AeEnable": True,
            "AnalogueGain": 1.0
        }
    )
    camera.configure(config)
    return camera
```

## System Optimization

### Performance Tuning

1. Memory Configuration
```bash
# Edit /boot/config.txt
sudo nano /boot/config.txt

# Add/modify:
gpu_mem=128
arm_boost=1
over_voltage=2
```

2. Storage Optimization
```bash
# Add to /etc/sysctl.conf
vm.swappiness=10
vm.cache_pressure=50
vm.dirty_background_ratio=5
vm.dirty_ratio=10
```

3. Process Priority
```bash
# Set process priority
sudo nice -n -20 python3 main.py

# Or in service file:
[Service]
Nice=-20
IOSchedulingClass=realtime
```

### Network Configuration

1. Static IP Setup
```bash
# Edit dhcpcd.conf
sudo nano /etc/dhcpcd.conf

# Add:
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1
```

2. WiFi Optimization
```bash
# Edit wpa_supplicant.conf
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# Add:
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YourNetwork"
    psk="YourPassword"
    priority=1
}
```

## Monitoring Setup

### System Monitoring

1. Temperature Monitoring
```bash
# Create monitoring script
nano monitor_temp.sh

#!/bin/bash
while true; do
    temp=$(vcgencmd measure_temp)
    echo "$(date): $temp" >> temp_log.txt
    sleep 300
done

# Make executable
chmod +x monitor_temp.sh
```

2. Resource Monitoring
```bash
# Install monitoring tools
sudo apt install -y htop iotop

# Create monitoring service
sudo nano /etc/systemd/system/resource-monitor.service

[Unit]
Description=Resource Monitoring Service

[Service]
ExecStart=/usr/bin/python3 /opt/license-plate-detector/scripts/monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Would you like me to continue with the next documentation file or expand any section of this one?