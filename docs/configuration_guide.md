# Configuration Guide

## Configuration Files

### Main Configuration (config.yaml)
```yaml
# System Configuration
system:
  debug_mode: false
  log_level: INFO
  timezone: UTC

# Camera Configuration
camera:
  resolution: [1920, 1080]
  framerate: 30
  rotation: 0
  auto_exposure: true
  gain: 1.0

# Detection Configuration
detection:
  min_confidence: 0.5
  frame_skip: 2
  max_plate_size: [200, 100]
  min_plate_size: [50, 25]
  detection_interval: 100  # milliseconds

# Analysis Configuration
analysis:
  window_minutes: 30
  min_detections: 5
  pattern_threshold: 0.7
  alert_threshold: 0.8
  cooldown_period: 300  # seconds

# Database Configuration
database:
  path: data/license_plates.db
  backup_path: data/backups
  max_connections: 5
  timeout: 30
  retention_days: 30

# Storage Configuration
storage:
  max_size_gb: 50
  cleanup_threshold: 0.9
  backup_enabled: true
  backup_interval: 86400  # seconds

# Performance Configuration
performance:
  max_cpu_percent: 80
  max_memory_percent: 70
  batch_size: 10
  worker_threads: 4

# Security Configuration
security:
  encryption_enabled: true
  key_path: config/keys
  access_control: true
  allowed_ips: [
    "192.168.1.0/24"
  ]
```

### Alert Configuration (alerts.yaml)
```yaml
alerts:
  # Email Alerts
  email:
    enabled: true
    smtp_server: smtp.example.com
    smtp_port: 587
    username: alerts@example.com
    recipients: [
      "admin@example.com"
    ]

  # SMS Alerts
  sms:
    enabled: false
    provider: twilio
    numbers: [
      "+1234567890"
    ]

  # Telegram Alerts
  telegram:
    enabled: true
    bot_token: "your_bot_token"
    chat_ids: [
      "123456789"
    ]

# Alert Conditions
conditions:
  high_following:
    threshold: 0.9
    cooldown: 300
    channels: [email, telegram]

  system_performance:
    cpu_threshold: 90
    memory_threshold: 85
    channels: [email]

  error_conditions:
    max_retries: 3
    notification_threshold: 5
    channels: [email, telegram]
```

### Backup Configuration (backup.yaml)
```yaml
backup:
  # Database Backup
  database:
    enabled: true
    interval: 86400  # daily
    retain_count: 7
    compress: true
    verify: true

  # Configuration Backup
  config:
    enabled: true
    interval: 604800  # weekly
    retain_count: 4

  # Log Backup
  logs:
    enabled: true
    interval: 86400
    retain_count: 14
    compress: true

  # Storage
  storage:
    local_path: /mnt/backup
    remote_enabled: false
    remote_path: s3://bucket/backup
    
  # Scheduling
  schedule:
    database: "0 0 * * *"  # midnight
    config: "0 0 * * 0"    # sunday midnight
    logs: "0 2 * * *"      # 2 AM
```

## Configuration Management

### Loading Configuration
```python
class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _validate_config(self):
        self._validate_camera_config()
        self._validate_detection_config()
        self._validate_analysis_config()
        self._validate_security_config()

    def get_config(self) -> Dict[str, Any]:
        return self.config.copy()

    def update_config(self, updates: Dict[str, Any]):
        self.config.update(updates)
        self._validate_config()
        self._save_config()
```

### Configuration Validation
```python
class ConfigValidator:
    def validate_camera_config(self, config: Dict[str, Any]):
        required_keys = ['resolution', 'framerate']
        self._check_required_keys(config, required_keys)
        
        # Validate resolution
        width, height = config['resolution']
        assert 640 <= width <= 3840, "Invalid width"
        assert 480 <= height <= 2160, "Invalid height"
        
        # Validate framerate
        assert 1 <= config['framerate'] <= 60, "Invalid framerate"

    def validate_detection_config(self, config: Dict[str, Any]):
        required_keys = ['min_confidence', 'frame_skip']
        self._check_required_keys(config, required_keys)
        
        # Validate confidence
        assert 0 <= config['min_confidence'] <= 1, "Invalid confidence"
        
        # Validate frame skip
        assert config['frame_skip'] > 0, "Invalid frame skip"
```

### Configuration Updates
```python
class ConfigUpdater:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.backup_manager = ConfigBackupManager()

    async def update_config(self, updates: Dict[str, Any]):
        # Backup current config
        await self.backup_manager.backup_config()
        
        try:
            # Apply updates
            new_config = self.config_manager.get_config()
            new_config.update(updates)
            
            # Validate
            ConfigValidator().validate_config(new_config)
            
            # Save
            self.config_manager.update_config(new_config)
            
        except Exception as e:
            # Rollback
            await self.backup_manager.restore_latest()
            raise ConfigurationError(f"Update failed: {str(e)}")
```
