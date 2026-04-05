# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for FishRouter GUI"""

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Collect all hidden imports from app modules and PySide6
hiddenimports = collect_submodules('app') + [
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtNetwork',
    'PySide6.QtSvg',
    'PySide6.QtPrintSupport',
]

# Add Qt plugins
datas = []
try:
    import PySide6
    plugins_dir = os.path.join(os.path.dirname(PySide6.__file__), 'plugins')
    if os.path.exists(plugins_dir):
        datas.append((plugins_dir, 'PySide6/plugins'))
except Exception:
    pass

a = Analysis(
    ['app/gui.py'],
    pathex=[],
    binaries=[],
    datas=datas + [
        ('static', 'static'),
        ('config.example.json', '.'),
    ],
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
