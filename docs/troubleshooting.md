# Troubleshooting Guide

## Common Issues

### Camera Issues
```bash
# Problem: Camera not detected
vcgencmd get_camera
# If output is 'supported=1 detected=0':
1. Check physical connection
2. Verify ribbon cable orientation
3. Check camera module in raspi-config

# Problem: Poor image quality
v4l2-ctl --list-ctrls
v4l2-ctl --set-ctrl brightness=128
v4l2-ctl --set-ctrl contrast=128
```

### Detection Issues
```python
# Problem: Low detection rate
def diagnose_detection():
    # Check image quality
    save_debug_image()
    # Check confidence scores
    log_confidence_stats()
    # Verify processing pipeline
    test_pipeline()
```

### Performance Issues
```bash
# Check system load
top -b -n 1

# Monitor temperature
watch -n 1 vcgencmd measure_temp

# Check storage
iostat -x 1
```

## Recovery Procedures

### Database Recovery
```bash
# Backup current database
cp license_plates.db license_plates.db.bak

# Check integrity
sqlite3 license_plates.db 'PRAGMA integrity_check;'

# Recover from backup
sqlite3 license_plates.db '.recover' | sqlite3 recovered.db
```

### System Recovery
```bash
# Emergency shutdown
sudo shutdown -h now

# Service recovery
sudo systemctl restart plate-detector
sudo systemctl status plate-detector
```

## Diagnostic Tools

### System Diagnostics
```python
class SystemDiagnostics:
    def run_diagnostics(self):
        self.check_camera()
        self.check_database()
        self.check_detection_system()
        self.check_analysis_system()
```

### Performance Analysis
```python
class PerformanceAnalyzer:
    def analyze_performance(self):
        self.check_cpu_usage()
        self.check_memory_usage()
        self.check_disk_io()
        self.check_network_latency()
```
