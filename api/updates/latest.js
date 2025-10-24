/**
 * ANTARCTIC UPDATE API
 * ====================
 * Endpoint para obtener la última versión disponible del autoclicker
 * 
 * GET /api/updates/latest
 * 
 * Response:
 * {
 *   "version": "1.0.2",
 *   "download_url": "https://...",
 *   "release_notes": "...",
 *   "released_at": "2025-01-15T10:00:00Z"
 * }
 */

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Información de la última versión
    // IMPORTANTE: Actualiza estos valores manualmente cuando hagas una nueva release
    const latestVersion = {
      version: '1.0.2',
      download_url: process.env.LATEST_EXE_URL || 'https://your-storage-url.com/Antarctic-1.0.2.exe',
      release_notes: `
- Fix: click type multiplier now correctly doubles/triples speed
- Optimize performance: higher thread priority, reduced GUI updates
- Fix license validation: remove incorrect buffer logic
- Add 1 day license option
- Restore small delay between batches to prevent excessive speed
      `.trim(),
      released_at: '2025-01-15T10:00:00Z'
    };

    res.json(latestVersion);

  } catch (error) {
    console.error('Error in updates/latest:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

