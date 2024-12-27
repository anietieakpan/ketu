# Contributing to License Plate Detection System

## Getting Started

### Development Environment Setup
1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/yourusername/license-plate-detector.git
cd license-plate-detector
```

3. Set up development environment:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

## Development Workflow

### Branch Naming Convention
- Feature: `feature/description`
- Bug Fix: `fix/description`
- Documentation: `docs/description`
- Performance: `perf/description`

### Commit Guidelines
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- perf: Performance improvements

### Pull Request Process
1. Create feature branch
2. Make changes
3. Run tests
4. Update documentation
5. Submit PR

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions focused

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_detector.py

# Run with coverage
pytest --cov=src tests/
```

### Writing Tests
```python
# Example test
def test_plate_detection():
    detector = PlateDetector()
    result = detector.detect(test_image)
    assert result.confidence > 0.5
    assert len(result.detections) > 0
```

## Documentation

### Documentation Standards
- Use Markdown
- Include code examples
- Provide configuration examples
- Add cross-references

### Building Documentation
```bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Build documentation
cd docs
make html
```
