# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['memory_mate.py'],
    pathex=[],
    binaries=[],
    datas=[('processing.gif', '.'),
           ('settings.png', '.'),
           ('rotate_left.png', '.'),
           ('rotate_right.png', '.'),
           ('memory_mate.ico', '.'),
           ('yellow_star.png', '.'),
           ('grey_star.png', '.'),
           ('reset_icon.png', '.'),
           ('pause.png', '.'),
           ('play.png', '.'),
           ('open_padlock.png', '.'),
           ('closed_padlock.png', '.'),
           ('exiftool_memory_mate.exe', '.'),
           ('exiftool_memory_mate.cfg', '.'),
           ('Memory Mate Sample Photo.jpg', '.')
          ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='Memory Mate',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['memory_mate.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Memory Mate',
)
