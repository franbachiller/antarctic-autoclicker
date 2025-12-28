# API Documentation

## Overview

The Antarctic API is built on Vercel Serverless Functions and provides endpoints for license management, validation, and administration.

**Base URL**: `https://antarctic-autoclicker.vercel.app/api`

## Authentication

All admin endpoints require authentication via the `X-Admin-Password` header.

```javascript
headers: {
  'X-Admin-Password': 'your_admin_password'
}
```

## Endpoints

### License Activation

**POST** `/activate`

Activates a license key and binds it to a hardware ID.

**Request Body:**
```json
{
  "licenseKey": "XXXX-XXXX-XXXX-XXXX",
  "hwid": "64-character-hex-string"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "License activated successfully",
  "sessionToken": "session-token-string",
  "licenseType": "7_days",
  "expiresAt": "2024-01-15T12:00:00Z"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Invalid license key"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid request
- `401` - Invalid license
- `403` - License banned or expired
- `429` - Rate limit exceeded

---

### Session Validation

**POST** `/validate`

Validates an active session token.

**Request Body:**
```json
{
  "sessionToken": "session-token-string",
  "hwid": "64-character-hex-string"
}
```

**Response (Success):**
```json
{
  "valid": true,
  "message": "Session valid",
  "expiresAt": "2024-01-15T12:00:00Z",
  "licenseType": "7_days"
}
```

**Response (Error):**
```json
{
  "valid": false,
  "error": "Session expired"
}
```

---

### Admin: List Licenses

**GET** `/admin/licenses`

Returns all licenses in the database.

**Headers:**
```
X-Admin-Password: your_admin_password
```

**Response:**
```json
{
  "success": true,
  "licenses": [
    {
      "id": 1,
      "license_key": "XXXX-XXXX-XXXX-XXXX",
      "license_type": "7_days",
      "hwid": "hardware-id",
      "is_active": true,
      "is_banned": false,
      "created_at": "2024-01-01T00:00:00Z",
      "activated_at": "2024-01-01T12:00:00Z",
      "expires_at": "2024-01-08T12:00:00Z"
    }
  ]
}
```

---

### Admin: Create License

**POST** `/admin/create-license`

Creates a new license.

**Headers:**
```
X-Admin-Password: your_admin_password
```

**Request Body:**
```json
{
  "licenseType": "7_days",
  "quantity": 1
}
```

**License Types:**
- `1_day`
- `7_days`
- `30_days`
- `lifetime`

**Response:**
```json
{
  "success": true,
  "licenses": [
    {
      "license_key": "XXXX-XXXX-XXXX-XXXX",
      "license_type": "7_days"
    }
  ]
}
```

---

### Admin: Delete License

**DELETE** `/admin/delete-license`

Deletes a license from the database.

**Headers:**
```
X-Admin-Password: your_admin_password
```

**Request Body:**
```json
{
  "licenseKey": "XXXX-XXXX-XXXX-XXXX"
}
```

**Response:**
```json
{
  "success": true,
  "message": "License deleted successfully"
}
```

---

### Admin: Ban License

**POST** `/admin/ban-license`

Bans or unbans a license.

**Headers:**
```
X-Admin-Password: your_admin_password
```

**Request Body:**
```json
{
  "licenseKey": "XXXX-XXXX-XXXX-XXXX",
  "banned": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "License banned successfully"
}
```

---

### Admin: Statistics

**GET** `/admin/stats`

Returns system statistics.

**Headers:**
```
X-Admin-Password: your_admin_password
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_licenses": 150,
    "active_licenses": 45,
    "banned_licenses": 5,
    "expired_licenses": 100,
    "licenses_by_type": {
      "1_day": 20,
      "7_days": 80,
      "30_days": 40,
      "lifetime": 10
    }
  }
}
```

## Rate Limiting

All endpoints are protected by rate limiting:

- **Activation**: 5 requests per minute per IP
- **Validation**: 20 requests per minute per IP
- **Admin**: 30 requests per minute per IP

Exceeded rate limits return:
```json
{
  "error": "Rate limit exceeded. Please try again later."
}
```

## Error Handling

All errors follow this format:

```json
{
  "success": false,
  "error": "Error message description"
}
```

Common error messages:
- `Invalid license key`
- `License already activated`
- `License expired`
- `License banned`
- `Invalid session token`
- `HWID mismatch`
- `Rate limit exceeded`

## Database Schema

### Licenses Table

```sql
CREATE TABLE licenses (
  id SERIAL PRIMARY KEY,
  license_key VARCHAR(19) UNIQUE NOT NULL,
  license_type VARCHAR(20) NOT NULL,
  hwid VARCHAR(64),
  is_active BOOLEAN DEFAULT FALSE,
  is_banned BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  activated_at TIMESTAMP,
  expires_at TIMESTAMP
);
```

### Indexes

```sql
CREATE INDEX idx_license_key ON licenses(license_key);
CREATE INDEX idx_hwid ON licenses(hwid);
CREATE INDEX idx_is_active ON licenses(is_active);
```

## Security Considerations

1. **HTTPS Only**: All API calls must use HTTPS
2. **HWID Binding**: Licenses are bound to hardware IDs
3. **Session Tokens**: Time-limited session tokens for validation
4. **Rate Limiting**: Prevents brute force attacks
5. **Admin Authentication**: Separate password for admin operations
6. **Input Validation**: All inputs are sanitized and validated

## Client Implementation

Example client implementation in Python:

```python
import requests
import hashlib

class AuthClient:
    def __init__(self, server_url):
        self.server_url = server_url
    
    def activate(self, license_key, hwid):
        response = requests.post(
            f"{self.server_url}/api/activate",
            json={
                'licenseKey': license_key,
                'hwid': hwid
            },
            timeout=10
        )
        return response.json()
    
    def validate(self, session_token, hwid):
        response = requests.post(
            f"{self.server_url}/api/validate",
            json={
                'sessionToken': session_token,
                'hwid': hwid
            },
            timeout=10
        )
        return response.json()
```

## Support

For API issues or questions, contact the development team.
