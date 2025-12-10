# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ftcli/ftcli.py'],
    pathex=[],
    binaries=[],
    datas=[('.env', '.')],
    hiddenimports=[
        'ftcli.commands.stats',
        'ftcli.commands.approve',
        'ftcli.commands.create',
        'ftcli.commands.join',
        'ftcli.commands.pending',
        'ftcli.commands.init',
        'ftcli.commands.auth',
        'ftcli.database',
        'ftcli.tui',
        'ftcli.utils.config',
        'ftcli.utils.ftc_scout',
        'asyncpg',
        'textual',
        'typer',
        'aiohttp',
        'bcrypt',
    ],
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
    name='ftcli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# For macOS .app bundle (optional)
app = BUNDLE(
    exe,
    name='FTC-CLI.app',
    icon=None,
    bundle_identifier='com.ftc.ftcli',
)