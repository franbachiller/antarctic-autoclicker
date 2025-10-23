import { sql } from '@vercel/postgres';

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

    const { licenseKey } = req.body;
    await sql`DELETE FROM licenses WHERE license_key = ${licenseKey}`;
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
