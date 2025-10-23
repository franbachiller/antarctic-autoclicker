import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';

function generateLicenseKey() {
  const part1 = crypto.randomBytes(4).toString('hex').toUpperCase();
  const part2 = crypto.randomBytes(4).toString('hex').toUpperCase();
  const part3 = crypto.randomBytes(4).toString('hex').toUpperCase();
  return `${part1}-${part2}-${part3}`;
}

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Key');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Check admin key
  const adminKey = req.headers['x-admin-key'];
  const expectedKey = process.env.ADMIN_KEY;

  if (!adminKey || adminKey !== expectedKey) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  // Check if Supabase is configured
  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_ANON_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return res.status(500).json({ error: 'Supabase not configured' });
  }

  try {
    const supabase = createClient(supabaseUrl, supabaseKey);
    const { type = 'standard', count = 1, notes = '' } = req.body;

    const licenses = [];
    for (let i = 0; i < count; i++) {
      const licenseKey = generateLicenseKey();
      const expiresAt = type === 'trial' 
        ? new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // 30 days
        : null;

      licenses.push({
        license_key: licenseKey,
        license_type: type,
        expires_at: expiresAt,
        notes: notes || `Generated ${type} license`
      });
    }

    const { data, error } = await supabase
      .from('licenses')
      .insert(licenses)
      .select();

    if (error) throw error;

    res.json({ success: true, licenses: data });
  } catch (error) {
    console.error('Create license error:', error);
    res.status(500).json({ error: error.message });
  }
}

