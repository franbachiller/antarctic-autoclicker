import { sql } from '@vercel/postgres';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Key');

  if (req.method === 'OPTIONS') return res.status(200).end();

  // Auth - Check multiple possible header names and env var names
  const adminKey = req.headers['x-admin-key'] || req.headers['X-Admin-Key'] || req.headers['admin-key'];
  const expectedKey = process.env.ADMIN_KEY || process.env.VITE_ADMIN_KEY || process.env.NEXT_PUBLIC_ADMIN_KEY;

  if (!adminKey || adminKey.trim() !== expectedKey) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    // Test database connection first
    await sql`SELECT 1`;

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

    const { rows } = await sql`
      SELECT
        license_key,
        license_type,
        status,
        created_at,
        expires_at,
        last_used,
        usage_count,
        notes,
        is_banned,
        hwid,
        max_devices,
        ip_address
      FROM licenses
      ORDER BY created_at DESC
    `;

    // Transform to match frontend expectations
    const transformedRows = rows.map(row => ({
      license_key: row.license_key,
      license_type: row.license_type,
      status: row.status || (row.is_banned ? 'banned' : 'active'),
      created_at: row.created_at,
      expires_at: row.expires_at,
      last_used: row.last_used,
      usage_count: row.usage_count,
      notes: row.notes,
      is_banned: row.is_banned,
      hwid: row.hwid,
      max_devices: row.max_devices,
      ip_address: row.ip_address
    }));

    res.json(transformedRows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
