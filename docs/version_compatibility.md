# Version Compatibility Matrix

## Hardware Compatibility

### Raspberry Pi Models
| Model | Status | Min Version | Notes |
|-------|--------|-------------|--------|
| Pi 5 | ✅ Recommended | 1.0.0 | Full support |
| Pi 4 | ✅ Supported | 1.0.0 | Limited performance |
| Pi 3 | ⚠️ Limited | 1.0.0 | Not recommended |
| Pi Zero | ❌ Unsupported | N/A | Insufficient resources |

### Camera Modules
| Module | Status | Min Version | Notes |
|--------|--------|-------------|--------|
| Pi Camera V3 | ✅ Recommended | 1.0.0 | Full support |
| Pi Camera V2 | ✅ Supported | 1.0.0 | Limited features |
| USB Cameras | ⚠️ Limited | 1.1.0 | Case-by-case |

## Software Compatibility

### Operating Systems
| OS | Version | Status | Notes |
|----|---------|--------|-------|
| Raspberry Pi OS | 64-bit | ✅ Recommended | Full support |
| Raspberry Pi OS | 32-bit | ⚠️ Limited | Not recommended |
| Ubuntu Server | 22.04+ | ✅ Supported | ARM64 only |
| Debian | 11+ | ✅ Supported | ARM64 only |

### Python Versions
| Version | Status | Notes |
|---------|--------|-------|
| 3.9+ | ✅ Recommended | Full support |
| 3.8 | ✅ Supported | Minimum version |
| 3.7 | ❌ Unsupported | Too old |

### Dependencies
| Package | Version | Status |
|---------|---------|--------|
| OpenCV | 4.6+ | Required |
| SQLite | 3.35+ | Required |
| NumPy | 1.20+ | Required |
| PyYAML | 5.4+ | Required |
