import { sql } from '@vercel/postgres';

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Key');

  if (req.method === 'OPTIONS') return res.status(200).end();

  // Auth
  const adminKey = req.headers['x-admin-key'];
  if (adminKey && adminKey.trim() !== process.env.ADMIN_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
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
    res.status(500).json({ error: error.message });
  }
}
