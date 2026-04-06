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

# Collect all data files
requests_datas = collect_data_files('requests')
urllib3_datas = collect_data_files('urllib3')
chardet_datas = collect_data_files('chardet')
certifi_datas = collect_data_files('certifi')
idna_datas = collect_data_files('idna')

hiddenimports = [
    'webview',
    'webview.platforms.winforms',
    'webview.platforms.cefbrowser',
    'json',
    'threading',
    'subprocess',
    'time',
    'glob',
    'logging',
    'collections',
    'functools',
    'base64',
    'hashlib',
    'hmac',
    'secrets',
    'queue',
    'socket',
    'ssl',
    'datetime',
    'email',
    'http',
    'xml',
    'html',
    'urllib.parse',
    'urllib.request',
    'urllib.error',
    'urllib.response',
    'http.client',
    'http.cookies',
    'email.utils',
    'dateutil',
    'dateutil.parser',
    'dateutil.tz',
    'pkg_resources',
    'pkg_resources.extern',
    'importlib',
    'importlib.resources',
    'importlib_metadata',
    'zipp',
    'distutils',
    'distutils.version',
    'setuptools',
    'setuptools._vendor',
    'setuptools._vendor.jaraco',
    'setuptools._vendor.jaraco.text',
    'setuptools._vendor.jaraco.functools',
    'setuptools._vendor.jaraco.context',
    'setuptools.extern',
    'autocommand',
    'inflection',
    'markdown_it',
    'rich',
    'rich.console',
    'rich.theme',
    'rich.style',
    'rich.color',
    'rich.text',
    'rich.table',
    'rich.progress',
    'rich.logging',
    'rich._loop',
    'rich._windows',
    'rich._livesync',
    'rich._file',
    'rich._timing',
    'rich._stack',
    'rich._pick',
    'rich._ratio',
    'rich._spinner',
    'rich._timer',
    'rich._wrap',
    'rich._emoji_codes',
    'rich._emoji',
    'rich.markdown',
    'rich.jupyter',
    'pygments',
    'pygments.lexer',
    'pygments.token',
    'pygments.formatters',
    'pygments.styles',
    'markupsafe',
    'jinja2',
    'jinja2.runtime',
    'jinja2.defaults',
    'jinja2.filters',
    'jinja2.utils',
    'jinja2.loaders',
    'markupsafe._speedups',
] + requests_submodules + urllib3_submodules + chardet_submodules + certifi_submodules + idna_submodules

datas = [
    ('config.example.json', '.'),
    ('static', 'static'),
] + requests_datas + urllib3_datas + chardet_datas + certifi_datas + idna_datas

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
