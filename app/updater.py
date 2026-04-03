"""FishRouter Auto-Update Module"""
import os
import sys
import json
import time
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger("fishrouter.updater")

GITHUB_API = "https://api.github.com/repos/Aobing-code/fishrouter"


class AutoUpdater:
    """Auto-update manager"""

    def __init__(self):
        self.current_version = self._get_current_version()
        self.latest_release: Optional[Dict] = None
        self.update_available = False
        self.download_url = None
        self.is_windows = sys.platform == "win32"

    def _get_current_version(self) -> str:
        """Get current version from git commit count"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__))
            )
            if result.returncode == 0:
                count = int(result.stdout.strip())
                return f"v0.{count}"
        except:
            pass
        return "v0.0"

    def check_for_updates(self) -> Dict:
        """Check for updates on GitHub"""
        try:
            import urllib.request
            import ssl

            # Create unverified SSL context for compatibility
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            req = urllib.request.Request(
                f"{GITHUB_API}/releases/latest",
                headers={"Accept": "application/vnd.github.v3+json"}
            )

            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                release = json.loads(response.read().decode())

            self.latest_release = release
            tag_name = release.get("tag_name", "")
            self.download_url = self._get_download_url(release)

            # Compare versions
            if self._is_newer(tag_name):
                self.update_available = True
                return {
                    "available": True,
                    "current": self.current_version,
                    "latest": tag_name,
                    "download_url": self.download_url,
                    "release_notes": release.get("body", ""),
                    "published_at": release.get("published_at", "")
                }

            return {"available": False, "current": self.current_version, "latest": tag_name}

        except Exception as e:
            logger.error(f"Update check failed: {e}")
            return {"available": False, "error": str(e)}

    def _get_download_url(self, release: Dict) -> Optional[str]:
        """Get download URL for current platform"""
        assets = release.get("assets", [])
        platform_suffix = ""

        if self.is_windows:
            # Prefer EXE installer, fallback to portable ZIP
            for asset in assets:
                if asset.get("name", "").endswith(".exe"):
                    return asset.get("browser_download_url")
            for asset in assets:
                if "Portable" in asset.get("name", "") and asset.get("name", "").endswith(".zip"):
                    return asset.get("browser_download_url")
        else:
            # Linux/macOS tarball
            for asset in assets:
                name = asset.get("name", "")
                if "linux" in name.lower() and name.endswith(".tar.gz"):
                    return asset.get("browser_download_url")

        return None

    def _is_newer(self, latest_tag: str) -> bool:
        """Check if latest version is newer than current"""
        try:
            # Extract version numbers
            current_num = int(self.current_version.replace("v0.", ""))
            latest_num = int(latest_tag.split("-")[0].replace("v0.", ""))
            return latest_num > current_num
        except:
            return False

    def download_update(self, progress_callback=None) -> Optional[str]:
        """Download the update"""
        if not self.download_url:
            return None

        try:
            import urllib.request
            import ssl

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            # Create temp directory
            temp_dir = tempfile.mkdtemp(prefix="fishrouter_update_")
            ext = ".exe" if self.download_url.endswith(".exe") else ".zip" if self.download_url.endswith(".zip") else ".tar.gz"
            download_path = os.path.join(temp_dir, f"update{ext}")

            # Download with progress
            def report_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(100, int(downloaded * 100 / total_size))
                    progress_callback(percent, downloaded, total_size)

            urllib.request.urlretrieve(self.download_url, download_path, report_progress)

            return download_path

        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

    def install_update(self, download_path: str) -> bool:
        """Install the downloaded update"""
        try:
            if download_path.endswith(".exe"):
                # Windows installer - run it
                if self.is_windows:
                    subprocess.Popen([download_path])
                    return True
            elif download_path.endswith(".zip"):
                # Portable ZIP - extract and replace
                import zipfile
                temp_extract = tempfile.mkdtemp(prefix="fishrouter_extract_")
                with zipfile.ZipFile(download_path, 'r') as zf:
                    zf.extractall(temp_extract)

                # Find the main executable
                for root, dirs, files in os.walk(temp_extract):
                    for f in files:
                        if f.lower() == "fishrouter.exe":
                            src = os.path.join(root, f)
                            dst = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), f)
                            shutil.copy2(src, dst)
                            return True

            return False

        except Exception as e:
            logger.error(f"Install failed: {e}")
            return False

    def restart_app(self):
        """Restart the application"""
        if self.is_windows:
            exe_path = os.path.abspath(sys.argv[0])
            subprocess.Popen([exe_path])
        os._exit(0)
