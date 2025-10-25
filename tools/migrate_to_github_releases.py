"""
MIGRATE TO GITHUB RELEASES
===========================
Script to update the auto-updater to use GitHub releases instead of Google Drive

This script will:
1. Fetch the latest GitHub release
2. Update api/updates/latest.js to use GitHub release URL
3. Update api/updates/download.js to use GitHub release URL
"""

import requests
import sys
import os
from pathlib import Path

# Configuration
GITHUB_REPO = "Narfbach/antarctic-autoclicker"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')


def get_latest_github_release():
    """
    Fetch the latest GitHub release information

    Returns:
        dict: Release information or None if not found
    """
    try:
        print(f"[*] Fetching latest release from GitHub...")

        headers = {}
        if GITHUB_TOKEN:
            headers['Authorization'] = f'token {GITHUB_TOKEN}'

        response = requests.get(GITHUB_API_URL, headers=headers, timeout=10)
        
        if response.status_code == 404:
            print("[ERROR] No releases found on GitHub")
            print("\nYou need to create a release first:")
            print("  1. Run: release.bat")
            print("  2. Or manually create a release on GitHub")
            return None
        
        response.raise_for_status()
        release = response.json()
        
        # Find the .exe asset
        exe_asset = None
        for asset in release.get('assets', []):
            if asset['name'].endswith('.exe'):
                exe_asset = asset
                break
        
        if not exe_asset:
            print("[ERROR] No .exe file found in the latest release")
            return None
        
        version = release['tag_name'].lstrip('v')
        download_url = exe_asset['browser_download_url']
        release_notes = release.get('body', 'No release notes available')
        
        print(f"[OK] Found release: v{version}")
        print(f"     Download URL: {download_url}")
        print(f"     File size: {exe_asset['size'] / (1024*1024):.2f} MB")
        
        return {
            'version': version,
            'download_url': download_url,
            'release_notes': release_notes,
            'released_at': release['published_at']
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch GitHub release: {e}")
        return None


def update_latest_js(release_info):
    """Update api/updates/latest.js with GitHub release URL"""
    latest_js_path = Path("api/updates/latest.js")
    
    if not latest_js_path.exists():
        print(f"[ERROR] File not found: {latest_js_path}")
        return False
    
    try:
        content = latest_js_path.read_text(encoding='utf-8')
        
        # Replace version
        import re
        content = re.sub(
            r"version:\s*['\"][\d.]+['\"]",
            f"version: '{release_info['version']}'",
            content
        )
        
        # Replace download_url - keep env variable fallback but use GitHub as default
        content = re.sub(
            r"download_url:\s*process\.env\.LATEST_EXE_URL\s*\|\|\s*['\"].*?['\"]",
            f"download_url: process.env.LATEST_EXE_URL || '{release_info['download_url']}'",
            content
        )
        
        # Replace release_notes
        escaped_notes = release_info['release_notes'].replace('`', '\\`').replace('${', '\\${')
        content = re.sub(
            r"release_notes:\s*`[^`]*`",
            f"release_notes: `\n{escaped_notes}\n      `",
            content,
            flags=re.DOTALL
        )
        
        # Replace released_at
        content = re.sub(
            r"released_at:\s*['\"].*?['\"]",
            f"released_at: '{release_info['released_at']}'",
            content
        )
        
        latest_js_path.write_text(content, encoding='utf-8')
        print(f"[OK] Updated {latest_js_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to update latest.js: {e}")
        return False


def update_download_js(release_info):
    """Update api/updates/download.js with GitHub release URL"""
    download_js_path = Path("api/updates/download.js")
    
    if not download_js_path.exists():
        print(f"[ERROR] File not found: {download_js_path}")
        return False
    
    try:
        content = download_js_path.read_text(encoding='utf-8')
        
        import re
        
        # Update the version mapping
        version = release_info['version']
        download_url = release_info['download_url']
        
        # Replace the existing version entry or add new one
        content = re.sub(
            r"(const downloadUrls = \{[^}]*)'[\d.]+':\s*process\.env\.LATEST_EXE_URL\s*\|\|\s*['\"].*?['\"]",
            f"\\1'{version}': process.env.LATEST_EXE_URL || '{download_url}'",
            content
        )
        
        # Update the default version
        content = re.sub(
            r"const targetVersion = version \|\| ['\"][\d.]+['\"]",
            f"const targetVersion = version || '{version}'",
            content
        )
        
        download_js_path.write_text(content, encoding='utf-8')
        print(f"[OK] Updated {download_js_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to update download.js: {e}")
        return False


def main():
    print("=" * 60)
    print("MIGRATE AUTO-UPDATER TO GITHUB RELEASES")
    print("=" * 60)
    print()
    
    # Fetch latest GitHub release
    release_info = get_latest_github_release()
    
    if not release_info:
        print("\n[FAILED] Could not fetch GitHub release information")
        print("\nNext steps:")
        print("  1. Create a GitHub release using: release.bat")
        print("  2. Run this script again")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("UPDATING API FILES")
    print("=" * 60)
    print()
    
    # Update API files
    success1 = update_latest_js(release_info)
    success2 = update_download_js(release_info)
    
    if success1 and success2:
        print()
        print("=" * 60)
        print("[SUCCESS] MIGRATION COMPLETE")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Review changes in api/updates/")
        print("  2. Test the update endpoint:")
        print(f"     curl https://antarctic-autoclicker.vercel.app/api/updates/latest")
        print("  3. Commit and push:")
        print("     git add api/updates/")
        print("     git commit -m 'Migrate to GitHub releases for updates'")
        print("     git push")
        print("  4. Vercel will auto-deploy the changes")
        print()
        print("Your updater will now download from GitHub releases!")
    else:
        print("\n[FAILED] Migration incomplete")
        sys.exit(1)


if __name__ == "__main__":
    main()

