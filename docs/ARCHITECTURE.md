# Architecture Overview

## System Architecture

Antarctic follows a client-server architecture with three main components:

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│  Desktop Client │ ◄─────► │  Vercel API      │ ◄─────► │  Supabase DB    │
│  (Python/Tk)    │  HTTPS  │  (Node.js)       │  SQL    │  (PostgreSQL)   │
│                 │         │                  │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
        │
        │ DevTools Protocol
        │
        ▼
┌─────────────────┐
│                 │
│  Game Client    │
│  (Browser)      │
│                 │
└─────────────────┘
```

## Component Details

### Desktop Client

**Technology**: Python 3.8+, CustomTkinter

**Responsibilities**:
- User interface and interaction
- Click automation logic
- License validation
- Latency measurement
- Configuration management
- Security and anti-debugging

**Key Modules**:
- `antarctic.py` - Main application and GUI
- `auth_client.py` - License authentication
- `latency_compensator.py` - Network latency handling
- `security.py` - Anti-debugging and protection

### Vercel API

**Technology**: Node.js, Vercel Serverless Functions

**Responsibilities**:
- License activation and validation
- Session management
- Admin operations
- Rate limiting
- Database queries

**Endpoints**:
- `/api/activate` - License activation
- `/api/validate` - Session validation
- `/api/admin/*` - Administrative functions

### Supabase Database

**Technology**: PostgreSQL

**Responsibilities**:
- License storage
- Session tracking
- User data persistence

**Tables**:
- `licenses` - License keys and metadata
- `sessions` - Active session tokens (optional)

## Data Flow

### License Activation

```
1. User enters license key
   │
   ▼
2. Client generates HWID
   │
   ▼
3. POST /api/activate
   │
   ▼
4. Server validates license
   │
   ▼
5. Server binds HWID
   │
   ▼
6. Server returns session token
   │
   ▼
7. Client encrypts and saves session
```

### Session Validation

```
1. Application starts
   │
   ▼
2. Client loads encrypted session
   │
   ▼
3. POST /api/validate
   │
   ▼
4. Server checks session validity
   │
   ▼
5. Server verifies HWID match
   │
   ▼
6. Server returns validation result
   │
   ▼
7. Client proceeds or requests activation
```

### Latency Compensation

```
1. Connect to game DevTools
   │
   ▼
2. Monitor WebSocket frames
   │
   ▼
3. Measure RTT from frame pairs
   │
   ▼
4. Calculate half-RTT
   │
   ▼
5. Apply compensation to click timing
```

## Security Architecture

### Client-Side Security

1. **Code Obfuscation**
   - PyArmor Level 5 on critical modules
   - String encryption
   - Control flow obfuscation

2. **Anti-Debugging**
   - Debugger detection
   - Process monitoring
   - Integrity checks

3. **Session Encryption**
   - AES-128 (Fernet) encryption
   - HWID-based key derivation
   - Secure local storage

### Server-Side Security

1. **Rate Limiting**
   - IP-based throttling
   - Endpoint-specific limits
   - Distributed denial-of-service protection

2. **Input Validation**
   - Schema validation
   - SQL injection prevention
   - XSS protection

3. **Authentication**
   - Admin password protection
   - Session token validation
   - HWID verification

## Deployment Architecture

### Client Deployment

```
Source Code (Python)
    │
    ▼
PyArmor Obfuscation
    │
    ▼
PyInstaller Compilation
    │
    ▼
Single Executable (Antarctic.exe)
    │
    ▼
GitHub Releases
```

### Server Deployment

```
Source Code (Node.js)
    │
    ▼
Vercel CLI / Git Push
    │
    ▼
Vercel Build Process
    │
    ▼
Serverless Functions
    │
    ▼
Production URL
```

## Scalability Considerations

### Client Scalability

- **Stateless Design**: No server-side session storage required
- **Local Caching**: Reduces API calls
- **Offline Mode**: Grace period for network issues

### Server Scalability

- **Serverless Functions**: Auto-scaling with demand
- **Database Indexing**: Optimized queries
- **CDN Distribution**: Global edge network
- **Connection Pooling**: Efficient database connections

## Performance Optimization

### Client Performance

1. **High-Precision Timing**
   - QueryPerformanceCounter API
   - Sub-millisecond accuracy
   - Busy-wait for critical delays

2. **Thread Optimization**
   - Real-time priority for click thread
   - CPU affinity settings
   - Minimal context switching

3. **Memory Management**
   - Efficient data structures
   - Minimal allocations in hot paths
   - Resource cleanup

### Server Performance

1. **Database Optimization**
   - Indexed queries
   - Connection pooling
   - Query result caching

2. **API Optimization**
   - Minimal response payloads
   - Compression enabled
   - Edge caching where applicable

## Monitoring and Logging

### Client Logging

- Local log files in `logs/` directory
- Debug mode for development
- Error reporting and stack traces

### Server Logging

- Vercel function logs
- Error tracking
- Performance metrics
- Rate limit violations

## Technology Choices

### Why Python for Client?

- Rich ecosystem for GUI (CustomTkinter)
- Excellent Windows API integration (ctypes)
- Easy compilation to executable (PyInstaller)
- Strong cryptography libraries

### Why Vercel for Backend?

- Serverless auto-scaling
- Global CDN distribution
- Zero-configuration deployment
- Generous free tier

### Why Supabase for Database?

- PostgreSQL compatibility
- Real-time capabilities
- Built-in authentication
- Generous free tier
- Easy integration with Vercel

## Future Architecture Considerations

### Potential Improvements

1. **WebSocket Support**
   - Real-time license revocation
   - Live admin monitoring
   - Instant updates

2. **Microservices**
   - Separate auth service
   - Dedicated admin service
   - Analytics service

3. **Caching Layer**
   - Redis for session storage
   - Reduced database load
   - Faster validation

4. **Multi-Region Deployment**
   - Regional database replicas
   - Lower latency globally
   - Better disaster recovery
