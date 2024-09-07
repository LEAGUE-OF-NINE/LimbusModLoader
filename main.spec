# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import get_package_paths

_unity_py = os.path.join(get_package_paths('UnityPy')[1], 'resources/uncompressed.tpk')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[(_unity_py, 'UnityPy/resources')],
    hiddenimports=['pkg_resources.extern'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=True,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon.png",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
