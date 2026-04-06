# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for FishRouter WebView2 Launcher"""

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

hiddenimports = [
    'webview',
    'webview.platforms.winforms',
    'webview.platforms.cefbrowser',
    'requests',
    'requests.compat',
    'requests.models',
    'requests.api',
    'requests.sessions',
    'requests.utils',
    'urllib3',
    'urllib3.util',
    'urllib3.util.retry',
    'chardet',
    'certifi',
    'idna',
    'json',
    'threading',
    'subprocess',
    'time',
]

datas = [
    ('config.example.json', '.'),
    ('static', 'static'),  # include built React app
]

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FishRouter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # windowed
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
