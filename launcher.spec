# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for FishRouter WebView2 Launcher"""

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_all

block_cipher = None

# Collect all submodules for problematic packages
requests_submodules = collect_submodules('requests')
urllib3_submodules = collect_submodules('urllib3')
chardet_submodules = collect_submodules('chardet')
certifi_submodules = collect_submodules('certifi')
idna_submodules = collect_submodules('idna')
pywebview_submodules = collect_submodules('webview')
pythonnet_submodules = collect_submodules('pythonnet')
clr_loader_submodules = collect_submodules('clr_loader')

# Collect all data files
requests_datas = collect_data_files('requests')
urllib3_datas = collect_data_files('urllib3')
chardet_datas = collect_data_files('chardet')
certifi_datas = collect_data_files('certifi')
idna_datas = collect_data_files('idna')
pywebview_datas = collect_data_files('webview')

hiddenimports = [
    'webview',
    'webview.platforms.winforms',
    'webview.platforms.cefbrowser',
    'webview.platforms.mshtml',
    'pythonnet',
    'clr_loader',
    'clr_loader.clr',
    'proxy_tools',
] + requests_submodules + urllib3_submodules + chardet_submodules + certifi_submodules + idna_submodules + pywebview_submodules + pythonnet_submodules + clr_loader_submodules

datas = [
    ('config.example.json', '.'),
    ('static', 'static'),
] + requests_datas + urllib3_datas + chardet_datas + certifi_datas + idna_datas + pywebview_datas

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
