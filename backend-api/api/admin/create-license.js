import { sql } from '@vercel/postgres';
import crypto from 'crypto';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Key');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const adminKey = req.headers['x-admin-key'];
  if (adminKey !== process.env.ADMIN_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
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
