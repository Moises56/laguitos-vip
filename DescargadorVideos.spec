# -*- mode: python ; coding: utf-8 -*-

# MODO ONEDIR para incluir FFmpeg (370 MB)
# Genera una carpeta con el ejecutable y todos los archivos necesarios

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('logo/logoDownloader.ico', 'logo'),
        ('logo/logoDownloader.png', 'logo'),
        ('ffmpeg_bundle/ffmpeg.exe', 'ffmpeg_bundle'),
        ('ffmpeg_bundle/ffprobe.exe', 'ffmpeg_bundle'),
    ],
    hiddenimports=['tkinter', 'yt_dlp'],
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
    exclude_binaries=True,  # ONEDIR: No incluir en el EXE
    name='DescargadorVideos',
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
    icon=['logo\\logoDownloader.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DescargadorVideos',
)
