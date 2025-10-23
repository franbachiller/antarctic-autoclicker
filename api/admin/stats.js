import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

console.log('=== SUPABASE CONFIG DEBUG ===');
console.log('SUPABASE_URL:', supabaseUrl ? 'SET' : 'NOT SET');
console.log('SUPABASE_ANON_KEY:', supabaseKey ? 'SET' : 'NOT SET');

// Create supabase client only if credentials are available
let supabase = null;
if (supabaseUrl && supabaseKey) {
  supabase = createClient(supabaseUrl, supabaseKey);
}

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Key');

  if (req.method === 'OPTIONS') return res.status(200).end();

  // Auth - Check multiple possible header names and env var names
  const adminKey = req.headers['x-admin-key'] || req.headers['X-Admin-Key'] || req.headers['admin-key'];
  const expectedKey = process.env.ADMIN_KEY || process.env.VITE_ADMIN_KEY || process.env.NEXT_PUBLIC_ADMIN_KEY;

  console.log('=== AUTH DEBUG ===');
  console.log('All headers:', JSON.stringify(req.headers, null, 2));
  console.log('Admin key received:', adminKey ? `"${adminKey}"` : 'null');
  console.log('Expected key:', expectedKey ? `"${expectedKey}"` : 'null');
  console.log('Key lengths - received:', adminKey ? adminKey.length : 0, 'expected:', expectedKey ? expectedKey.length : 0);
  console.log('All env vars with ADMIN:', Object.keys(process.env).filter(k => k.includes('ADMIN')));
  console.log('All env vars with SUPABASE:', Object.keys(process.env).filter(k => k.includes('SUPABASE')));

  if (!adminKey || adminKey.trim() !== expectedKey) {
    console.log('AUTH FAILED - returning 401');
    return res.status(401).json({ error: 'Unauthorized' });
  }

  console.log('AUTH SUCCESS - proceeding');

  // If Supabase is not configured, return mock data
  if (!supabase) {
    console.log('Supabase not configured, returning mock data');
    return res.json({
      total: 0,
      active: 0,
      expired: 0,
      banned: 0,
      _note: 'Configure SUPABASE_URL and SUPABASE_ANON_KEY in Vercel to see real data'
    });
  }

  try {
    // Get total count
    const { count: totalCount, error: countError } = await supabase
      .from('licenses')
      .select('*', { count: 'exact', head: true });

    if (countError) throw countError;

    // Get all licenses for detailed stats
    const { data: licenses, error: dataError } = await supabase
      .from('licenses')
      .select('status, expires_at, is_banned');

    if (dataError) throw dataError;

    // Calculate stats from the data
    const total = totalCount || 0;
    const active = licenses ? licenses.filter(license =>
      license.status === 'active' &&
      (!license.expires_at || new Date(license.expires_at) > new Date())
    ).length : 0;
    const expired = licenses ? licenses.filter(license =>
      license.status === 'expired' ||
      (license.expires_at && new Date(license.expires_at) <= new Date())
    ).length : 0;
    const banned = licenses ? licenses.filter(license =>
      license.status === 'banned' || license.is_banned
    ).length : 0;

    res.json({
      total,
      active,
      expired,
      banned
    });
  } catch (error) {
    console.error('Stats error:', error);
    res.status(500).json({ error: error.message });
  }
}
