import { sql } from '@vercel/postgres';
import crypto from 'crypto';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Key');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const adminKey = req.headers['x-admin-key'];
  if (!adminKey || adminKey.trim() !== process.env.ADMIN_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    // First ensure the licenses table exists
    await sql`CREATE TABLE IF NOT EXISTS licenses (
      id SERIAL PRIMARY KEY,
      license_key VARCHAR(255) UNIQUE NOT NULL,
      license_type VARCHAR(50) NOT NULL,
      status VARCHAR(20) DEFAULT 'active',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      expires_at TIMESTAMP,
      last_used TIMESTAMP,
      usage_count INTEGER DEFAULT 0,
      notes TEXT,
      is_banned BOOLEAN DEFAULT false,
      hwid VARCHAR(255),
      max_devices INTEGER DEFAULT 1,
      ip_address VARCHAR(45)
    )`;

    // Create indexes if they don't exist
    await sql`CREATE INDEX IF NOT EXISTS idx_licenses_key ON licenses(license_key)`;
    await sql`CREATE INDEX IF NOT EXISTS idx_licenses_status ON licenses(status)`;
    await sql`CREATE INDEX IF NOT EXISTS idx_licenses_expires ON licenses(expires_at)`;

    const { licenseType, count = 1, notes } = req.body;

    const durations = {
      week: 7,
      month: 30,
      '3months': 90,
      '6months': 180,
      year: 365,
      lifetime: 36500
    };

    const days = durations[licenseType] || 30;
    const licenses = [];

    for (let i = 0; i < count; i++) {
      const key = `ANTARCTIC-${crypto.randomBytes(4).toString('hex').toUpperCase()}-${crypto.randomBytes(4).toString('hex').toUpperCase()}-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;

      const { rows } = await sql`
        INSERT INTO licenses (license_key, license_type, status, expires_at, notes, created_at, is_banned, usage_count, max_devices)
        VALUES (${key}, ${licenseType}, 'active', NOW() + INTERVAL '${days} days', ${notes || null}, NOW(), false, 0, 1)
        RETURNING *
      `;

      licenses.push(rows[0]);
    }

    res.json({ licenses });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
