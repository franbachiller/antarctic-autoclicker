import { sql } from '@vercel/postgres';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    const { licenseKey } = req.body;
    
    const { rows } = await sql`
      SELECT * FROM licenses WHERE license_key = ${licenseKey}
    `;
    
    if (rows.length === 0) {
      return res.json({ valid: false, reason: 'Invalid license key' });
    }
    
    const license = rows[0];
    
    if (license.is_banned) {
      return res.json({ valid: false, reason: 'License banned' });
    }
    
    if (new Date(license.expires_at) < new Date()) {
      return res.json({ valid: false, reason: 'License expired' });
    }
    
    await sql`
      UPDATE licenses 
      SET usage_count = usage_count + 1, last_used = NOW() 
      WHERE license_key = ${licenseKey}
    `;
    
    res.json({ 
      valid: true, 
      expiresAt: license.expires_at,
      licenseType: license.license_type
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
