import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';

const supabaseUrl = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  throw new Error('Missing Supabase environment variables');
}

const supabase = createClient(supabaseUrl, supabaseKey);

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Key');

  if (req.method === 'OPTIONS') return res.status(200).end();

  // Auth - Check multiple possible header names and env var names
  const adminKey = req.headers['x-admin-key'] || req.headers['X-Admin-Key'] || req.headers['admin-key'];
  const expectedKey = process.env.ADMIN_KEY || process.env.VITE_ADMIN_KEY || process.env.NEXT_PUBLIC_ADMIN_KEY;

  if (!adminKey || adminKey.trim() !== expectedKey) {
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
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + days);

    const licenses = [];

    for (let i = 0; i < count; i++) {
      const key = `ANTARCTIC-${crypto.randomBytes(4).toString('hex').toUpperCase()}-${crypto.randomBytes(4).toString('hex').toUpperCase()}-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;

      const { data, error } = await supabase
        .from('licenses')
        .insert({
          license_key: key,
          license_type: licenseType,
          status: 'active',
          expires_at: expiresAt.toISOString(),
          notes: notes || null,
          is_banned: false,
          usage_count: 0,
          max_devices: 1
        })
        .select()
        .single();

      if (error) throw error;
      licenses.push(data);
    }

    res.json({ licenses });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
