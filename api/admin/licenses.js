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
      .select(`
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
      `)
      .order('created_at', { ascending: false });

    if (error) throw error;

    // Transform to match frontend expectations
    const transformedRows = (data || []).map(row => ({
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
