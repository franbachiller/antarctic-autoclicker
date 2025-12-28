# Screenshots and Demo

## Application Interface

### Main Window
The main application features a modern dark-themed interface built with CustomTkinter.

**Key sections:**
- License activation and status
- Click configuration (interval, clicks, timing mode)
- Latency compensation controls
- Profile management
- Real-time statistics

### License Activation
Users activate the application by entering their license key. The system validates against the Supabase backend and binds the license to the hardware ID.

### Timing Modes

**Markov Chain Mode:**
- Realistic human-like click patterns
- State-based transitions
- Natural variation

**Gaussian Mode:**
- Normal distribution around target interval
- Configurable standard deviation
- Smooth timing variation

**Acceleration Mode:**
- Progressive speed increase
- Configurable acceleration rate
- Useful for race conditions

**Perfect Machine Mode:**
- Zero-variance timing
- Mathematical precision
- Exact intervals

### Latency Compensation

**Connection Interface:**
- DevTools port input
- Connection status indicator
- Real-time RTT display

**Statistics Display:**
- Current RTT
- Average RTT
- Min/Max RTT
- Half-RTT (compensation value)

**Calibration:**
- 10-second automatic calibration
- Optimal offset calculation
- Compensation multiplier adjustment (0.0 - 2.0)

### Profile Management
- Save current configuration
- Load saved profiles
- Quick switching between setups
- Profile naming and organization

### Admin Panel

**License Management:**
- View all licenses
- Create new licenses (1 day, 7 days, 30 days, lifetime)
- Ban/unban licenses
- Delete licenses
- View statistics

**Statistics Dashboard:**
- Total licenses
- Active licenses
- Banned licenses
- Expired licenses
- Licenses by type breakdown

## Demo Video

A demo video showing the application in action would be placed here.

**Recommended content:**
1. Application startup and license activation
2. Configuration of click settings
3. Latency compensation setup and calibration
4. Profile creation and switching
5. Real-time operation demonstration

## Technical Demonstrations

### High-Precision Timing
The application uses Windows QueryPerformanceCounter for sub-millisecond timing accuracy.

### Latency Compensation
Real-time RTT measurement via Chrome DevTools Protocol, with automatic timing adjustment.

### Security Features
- Code obfuscation with PyArmor
- Anti-debugging mechanisms
- Encrypted session storage
- HWID binding

## Use Cases

### Gaming
- Competitive advantage in click-based games
- Latency compensation for online play
- Consistent timing for race conditions

### Automation
- Repetitive task automation
- Precise timing requirements
- Profile-based configurations

### Testing
- UI testing automation
- Performance testing
- Stress testing applications

## Performance Metrics

**Timing Accuracy:**
- Sub-millisecond precision
- Consistent intervals
- Low jitter

**Resource Usage:**
- Low CPU utilization
- Minimal memory footprint
- Efficient threading

**Network Performance:**
- Fast license validation
- Minimal API calls
- Offline grace period

## Future Screenshots

As new features are added, screenshots will be included here to demonstrate:
- New UI components
- Additional timing modes
- Enhanced statistics
- Improved admin panel
