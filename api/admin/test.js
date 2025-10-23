export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Key');

  if (req.method === 'OPTIONS') return res.status(200).end();

  // Log EVERYTHING
  console.log('=== TEST ENDPOINT DEBUG ===');
  console.log('Headers:', req.headers);
  console.log('Method:', req.method);
  
  // Get admin key from header
  const adminKey = req.headers['x-admin-key'];
  const expectedKey = process.env.ADMIN_KEY;
  
  console.log('Admin key received:', adminKey);
  console.log('Expected key:', expectedKey);
  console.log('Match:', adminKey === expectedKey);
  
  // Return debug info
  res.json({
    success: true,
    receivedKey: adminKey ? `${adminKey.substring(0, 3)}...` : 'null',
    expectedKey: expectedKey ? `${expectedKey.substring(0, 3)}...` : 'null',
    match: adminKey === expectedKey,
    allEnvVars: Object.keys(process.env).filter(k => k.includes('ADMIN'))
  });
}

