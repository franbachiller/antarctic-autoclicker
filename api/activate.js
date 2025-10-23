import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';
import { checkRateLimit } from './middleware/rate-limit.js';

export default async function handler(req, res) {
  // CORS - Allow desktop app and admin panel
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

  // Rate limit by IP
  const clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
  const rateCheck = checkRateLimit(clientIp, 10, 60000);

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
    const { licenseKey, hwid } = req.body;

    if (!licenseKey || !hwid) {
      return res.status(400).json({ error: 'License key and HWID required' });
    }

    // Validate license key format
    if (!/^[A-F0-9]{8}-[A-F0-9]{8}-[A-F0-9]{8}$/i.test(licenseKey)) {
      return res.status(400).json({ error: 'Invalid license key format' });
    }

    // Validate HWID format
    if (!/^[a-f0-9]{64}$/i.test(hwid)) {
      return res.status(400).json({ error: 'Invalid HWID format' });
    }

    // Find the license
    const { data: license, error: fetchError } = await supabase
      .from('licenses')
      .select('*')
      .eq('license_key', licenseKey)
      .single();

    if (fetchError || !license) {
      return res.status(404).json({ error: 'Invalid license key' });
    }

    // Check if license is banned
    if (license.is_banned || license.status === 'banned') {
      return res.status(403).json({ error: 'License has been banned' });
    }

    // Check if license is expired
    if (license.expires_at) {
      const expiresAt = new Date(license.expires_at);
      if (expiresAt < new Date()) {
        // Update status to expired
        await supabase
          .from('licenses')
          .update({ status: 'expired' })
          .eq('license_key', licenseKey);
        
        return res.status(403).json({ error: 'License has expired' });
      }
    }

    // Check if license is already bound to different HWID
    if (license.hwid && license.hwid !== hwid) {
      return res.status(403).json({
        error: 'License already activated on another device',
        code: 'HWID_MISMATCH'
      });
    }

    // Generate session token
    const sessionToken = crypto.randomBytes(32).toString('hex');
    const sessionExpires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days

    // Update license with HWID and session info
    const { error: updateError } = await supabase
      .from('licenses')
      .update({
        hwid: license.hwid || hwid,
        last_used: new Date().toISOString(),
        usage_count: (license.usage_count || 0) + 1,
        status: 'active',
        session_token: sessionToken,
        session_expires: sessionExpires.toISOString()
      })
      .eq('license_key', licenseKey);

    if (updateError) throw updateError;

    // Return success with session token
    res.json({
      success: true,
      sessionToken: sessionToken,
      licenseType: license.license_type,
      expiresAt: license.expires_at,
      message: 'License activated successfully'
    });

  } catch (error) {
    console.error('Activation error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

