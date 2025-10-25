/**
 * ANTARCTIC UPDATE DOWNLOAD
 * ==========================
 * Endpoint para descargar la última versión del ejecutable
 * 
 * GET /api/updates/download?version=1.0.2
 * 
 * Redirige a la URL de descarga del ejecutable
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
    const { version } = req.query;

    // Mapeo de versiones a URLs de descarga
    // IMPORTANTE: Actualiza esto cuando subas una nueva versión
    const downloadUrls = {
      '1.0.2': process.env.LATEST_EXE_URL || 'https://drive.google.com/uc?export=download&id=17Ij1zl6Q0UVs4Jhkod3kjfydvO90wsxP',
    };

    // Si no se especifica versión, usar la última
    const targetVersion = version || '1.0.2';
    const downloadUrl = downloadUrls[targetVersion];

    if (!downloadUrl) {
      return res.status(404).json({ 
        error: 'Version not found',
        available_versions: Object.keys(downloadUrls)
      });
    }

    // Redirigir a la URL de descarga
    res.redirect(302, downloadUrl);

  } catch (error) {
    console.error('Error in updates/download:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

