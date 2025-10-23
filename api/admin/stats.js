import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  throw new Error('Missing Supabase environment variables');
}

const supabase = createClient(supabaseUrl, supabaseKey);

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
    const { data, error } = await supabase
      .from('licenses')
      .select('*', { count: 'exact', head: true });

    if (error) throw error;

    // Calculate stats from the data
    const total = data || 0;
    const active = data ? data.filter(license =>
      license.status === 'active' &&
      (!license.expires_at || new Date(license.expires_at) > new Date())
    ).length : 0;
    const expired = data ? data.filter(license =>
      license.status === 'expired' ||
      (license.expires_at && new Date(license.expires_at) <= new Date())
    ).length : 0;
    const banned = data ? data.filter(license =>
      license.status === 'banned' || license.is_banned
    ).length : 0;

    res.json({
      total,
      active,
      expired,
      banned
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
