import { createClient } from '@supabase/supabase-js';
import { checkRateLimit } from './middleware/rate-limit.js';

export default async function handler(req, res) {
  // CORS
  const ALLOWED_ORIGINS = [
    'https://antarctic-autoclicker.vercel.app',
    'http://localhost:3000'
  ];
  const origin = req.headers.origin;
  if (ALLOWED_ORIGINS.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  } else {
    res.setHeader('Access-Control-Allow-Origin', '*');
  }
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Rate limit
  const clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
  const rateCheck = checkRateLimit(clientIp, 20, 60000);

  if (!rateCheck.allowed) {
    return res.status(429).json({
      error: 'Too many requests',
      retryAfter: rateCheck.retryAfter
    });
  }

  // Check if Supabase is configured
  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_ANON_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return res.status(500).json({ error: 'Database not configured' });
  }

  try {
    const supabase = createClient(supabaseUrl, supabaseKey);
    const { sessionToken, hwid } = req.body;

    if (!sessionToken || !hwid) {
      return res.status(400).json({ error: 'Session token and HWID required' });
    }

    // Validate session token format
    if (!/^[a-f0-9]{64}$/i.test(sessionToken)) {
      return res.status(400).json({ error: 'Invalid session token format' });
    }

    // Validate HWID format
    if (!/^[a-f0-9]{64}$/i.test(hwid)) {
      return res.status(400).json({ error: 'Invalid HWID format' });
    }

    // Find the license by session token
    const { data: license, error: fetchError } = await supabase
      .from('licenses')
      .select('*')
      .eq('session_token', sessionToken)
      .single();

    if (fetchError || !license) {
      return res.status(401).json({ valid: false, error: 'Invalid session' });
    }

    // Check session expiration
    if (license.session_expires && new Date(license.session_expires) < new Date()) {
      return res.status(401).json({
        valid: false,
        error: 'Session expired. Please re-activate.'
      });
    }

    // Verify HWID matches
    if (license.hwid !== hwid) {
      return res.status(403).json({ valid: false, error: 'HWID mismatch' });
    }

    // Check if license is banned
    if (license.is_banned || license.status === 'banned') {
      return res.status(403).json({ valid: false, error: 'License has been banned' });
    }

    // Check if license is expired
    if (license.expires_at) {
      const expiresAt = new Date(license.expires_at);
      if (expiresAt < new Date()) {
        // Update status to expired
        await supabase
          .from('licenses')
          .update({ status: 'expired' })
          .eq('license_key', license.license_key);
        
        return res.status(403).json({ valid: false, error: 'License has expired' });
      }
    }

    // Update last used timestamp
    await supabase
      .from('licenses')
      .update({ last_used: new Date().toISOString() })
      .eq('license_key', license.license_key);

    // Return success
    res.json({
      valid: true,
      licenseType: license.license_type,
      expiresAt: license.expires_at,
      message: 'Session valid'
    });

  } catch (error) {
    console.error('Validation error:', error);
    res.status(500).json({ valid: false, error: 'Internal server error' });
  }
}

