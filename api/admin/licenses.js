import { sql } from '@vercel/postgres';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Key');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const adminKey = req.headers['x-admin-key'];
  if (!adminKey || adminKey.trim() !== process.env.ADMIN_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
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
