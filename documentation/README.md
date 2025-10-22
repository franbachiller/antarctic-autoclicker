# Antarctic Auto-Clicker v2.0

A professional, modular auto-clicker application with advanced timing systems, security features, and comprehensive monitoring.

## 🐧 Features

### Core Features
- **Advanced Auto-Clicking**: Precision timing with microsecond accuracy
- **Multiple Click Types**: Single, double, and triple clicks
- **Configurable Timing**: Human-like delays and jitter patterns
- **Profile Management**: Save and load different click configurations
- **Real-time Monitoring**: System resource and performance tracking

### Security & Licensing
- **Hardware ID Validation**: Secure device fingerprinting
- **AES-256 Encryption**: Protected configuration and session data
- **Online License Management**: Cloud-based activation system
- **Anti-Tampering**: Runtime integrity checks

### Advanced Features
- **Burst Variations**: Complex timing patterns for race conditions
- **Thread Optimization**: Real-time priority and CPU affinity
- **Performance Monitoring**: Detailed metrics and health checks
- **Modular Architecture**: Clean, maintainable codebase

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Windows 10+ or Linux
- Internet connection for license activation

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/antarctic-clicker.git
   cd antarctic-clicker
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### First Time Setup

1. Launch the application
2. Enter your license key when prompted
3. Configure your click settings
4. Press F3 to capture target coordinates
5. Press F2 to start clicking

## 📖 Usage

### Hotkeys
- **F2**: Start/Stop clicking burst
- **F3**: Capture mouse coordinates
- **F5**: Toggle auto-burst mode

### Configuration
- **Clicks**: Number of clicks per burst (1-1000)
- **Interval**: Delay between clicks in milliseconds
- **Duration**: Burst duration in seconds
- **Type**: Single, double, or triple clicks
- **Button**: Left, right, middle, X1, or X2

### Advanced Timing
Enable "Burst Variations" for race condition scenarios:
- **Race Condition Master**: 100 rapid clicks with microsecond timing
- **Timing Critical**: Complex burst patterns
- **Precision Burst**: Variable burst sizes with controlled delays

## 🏗️ Architecture

```
antarctic-clicker/
├── src/
│   ├── core/           # Core clicking engine
│   │   ├── clicker.py  # Main clicker logic
│   │   ├── timing.py   # Advanced timing systems
│   │   └── window.py   # Window management
│   ├── gui/            # User interface
│   │   ├── main.py     # Main GUI application
│   │   └── components/ # UI components
│   ├── config/         # Configuration management
│   │   ├── manager.py  # Config handling
│   │   ├── profiles.py # Profile management
│   │   └── environment.py # Environment settings
│   ├── utils/          # Utilities
│   │   ├── logger.py   # Structured logging
│   │   ├── security.py # Security functions
│   │   ├── validators.py # Input validation
│   │   └── performance.py # Performance monitoring
│   ├── monitoring/     # Health and metrics
│   │   ├── health.py   # Health checks
│   │   └── metrics.py  # Metrics collection
│   └── tests/          # Unit tests
├── auth-server/        # License server
├── main.py            # Application entry point
└── requirements.txt   # Dependencies
```

## 🔧 Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src

# Code formatting
black src/
flake8 src/

# Type checking
mypy src/
```

### Running Tests

```bash
# Run all tests
python -m pytest src/tests/

# Run specific test
python -m pytest src/tests/test_config.py::TestClickConfig::test_default_values

# Run with coverage
python -m pytest --cov=src --cov-report=html
```

### Building

```bash
# Create executable
pyinstaller --onefile --windowed main.py

# Create obfuscated build
pyarmor build --output obfuscated main.py
```

## 🔒 Security

### Encryption
- AES-256-CBC for data encryption
- PBKDF2 key derivation with 100,000 iterations
- Secure random IV generation

### Hardware ID
- Multi-factor device fingerprinting
- CPU, motherboard, and disk identifiers
- Timestamp-based salting

### Runtime Protection
- Debugger detection
- VM environment detection
- Process integrity checks
- Anti-tampering measures

## 📊 Monitoring

### Health Checks
- System resource monitoring
- Memory usage tracking
- Network connectivity tests
- Configuration validation

### Performance Metrics
- CPU and memory usage
- Response time tracking
- Operation throughput
- Thread utilization

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["python", "main.py"]
```

### CI/CD Pipeline

The project includes GitHub Actions for:
- Automated testing
- Code quality checks
- Security scanning
- Release builds

## 📝 API Documentation

### License Server API

#### POST /api/activate
Activate a license key.

**Request:**
```json
{
  "licenseKey": "ANTARCTIC-XXXX-XXXX-XXXX",
  "hwid": "device_hardware_id"
}
```

**Response:**
```json
{
  "success": true,
  "message": "License activated successfully",
  "data": {
    "sessionToken": "jwt_token",
    "expiresAt": "2024-12-31T23:59:59Z",
    "licenseType": "premium"
  }
}
```

#### POST /api/validate
Validate a session token.

**Request:**
```json
{
  "sessionToken": "jwt_token",
  "hwid": "device_hardware_id"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **Pytest** for testing
- 100% test coverage requirement

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support, please contact the development team or create an issue in the repository.

## 🗺️ Roadmap

### Version 2.1
- [ ] Multi-language support
- [ ] Plugin system
- [ ] Advanced macro recording
- [ ] Cloud synchronization

### Version 2.2
- [ ] Machine learning optimization
- [ ] Advanced anti-detection
- [ ] Cross-platform mobile support
- [ ] Hardware acceleration

---

**Made with ❤️ by the Antarctic Team**
