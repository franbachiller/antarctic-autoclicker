import { createClient } from '@supabase/supabase-js';

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
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
    return res.json({
      total: 0,
      active: 0,
      expired: 0,
      banned: 0
    });
  }

  try {
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { data: licenses, error } = await supabase
      .from('licenses')
      .select('status, expires_at, is_banned');

    if (error) throw error;

    const now = new Date();
    const total = licenses?.length || 0;
    const active = licenses?.filter(l => 
      l.status === 'active' && 
      !l.is_banned && 
      (!l.expires_at || new Date(l.expires_at) > now)
    ).length || 0;
    const expired = licenses?.filter(l => 
      l.expires_at && new Date(l.expires_at) <= now
    ).length || 0;
    const banned = licenses?.filter(l => l.is_banned).length || 0;

    res.json({ total, active, expired, banned });
  } catch (error) {
    console.error('Stats error:', error);
    res.status(500).json({ error: error.message });
  }
}

