# Changelog

All notable changes to Antarctic Autoclicker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions workflow for automated releases
- Comprehensive API documentation
- Architecture documentation
- Contributing guidelines
- Requirements.txt for dependency management

### Changed
- README.md rewritten for professional presentation
- Improved project structure documentation

## [1.0.0] - 2024-01-01

### Added
- Initial release
- Advanced autoclicker with multiple timing modes
- License validation system with Supabase backend
- Latency compensation for online games
- Profile management system
- Modern GUI with CustomTkinter
- PyArmor code obfuscation
- Anti-debugging security features
- Admin panel for license management
- Public website
- Automated build and release scripts

### Features
- Single, double, and triple click modes
- Timing algorithms: Markov, Gaussian, Acceleration, Perfect Machine
- Real-time RTT measurement via DevTools Protocol
- Automatic latency compensation
- HWID-based license binding
- Offline grace period (1 hour)
- Session encryption (AES-128)
- Rate limiting on API endpoints
- Hotkey support (F2, F3, F5)
- Auto-burst mode with left click

### Security
- PyArmor Level 5 obfuscation on critical modules
- Anti-debugging mechanisms
- HWID binding for licenses
- Encrypted session storage
- Secure API communication (HTTPS)

### Infrastructure
- Vercel serverless deployment
- Supabase PostgreSQL database
- GitHub releases integration
- Automated compilation pipeline

[Unreleased]: https://github.com/Narfbach/antarctic-autoclicker/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Narfbach/antarctic-autoclicker/releases/tag/v1.0.0
