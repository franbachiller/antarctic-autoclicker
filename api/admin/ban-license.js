import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;

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
    const { licenseKey } = req.body;

    const { error } = await supabase
      .from('licenses')
      .update({ status: 'banned', is_banned: true })
      .eq('license_key', licenseKey);

    if (error) throw error;

    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
