import { sql } from '@vercel/postgres';

export default async function handler(req, res) {
  // CORS
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
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE status = 'active' AND (expires_at IS NULL OR expires_at > NOW())) as active,
        COUNT(*) FILTER (WHERE status = 'expired' OR (expires_at IS NOT NULL AND expires_at <= NOW())) as expired,
        COUNT(*) FILTER (WHERE status = 'banned' OR is_banned = true) as banned
      FROM licenses
    `;

    res.json({
      total: parseInt(rows[0].total),
      active: parseInt(rows[0].active),
      expired: parseInt(rows[0].expired),
      banned: parseInt(rows[0].banned)
    });
  } catch (error) {
    // Fallback: Return mock data if database fails
    res.json({
      total: 0,
      active: 0,
      expired: 0,
      banned: 0
    });
  }
}
