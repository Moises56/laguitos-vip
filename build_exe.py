"""
Script simple para crear el ejecutable usando PyInstaller
"""
import os
import subprocess
import sys
from pathlib import Path

print("=" * 50)
print("🚀 Creando Ejecutable de Descargador de Videos")
print("=" * 50)
print()

# 1. Verificar que estamos en el directorio correcto
if not Path("main.py").exists():
    print("❌ Error: No se encuentra main.py")
    print("   Ejecuta este script desde el directorio del proyecto")
    sys.exit(1)

# 2. Crear logo si no existe
logo_ico = Path("logo/logoDownloader.ico")
if not logo_ico.exists():
    print("🎨 Creando logo...")
    result = subprocess.run([sys.executable, "convert_logo.py"])
    if result.returncode != 0:
        print("❌ Error al crear logo")
        sys.exit(1)
    print()

# 3. Crear ejecutable
print("📦 Creando ejecutable con PyInstaller...")
print("   (Esto puede tardar varios minutos...)")
print()

cmd = [
    sys.executable,
    "-m", "PyInstaller",
    "--name=DescargadorVideos",
    "--onefile",
    "--windowed",  # Sin consola
    f"--icon={logo_ico}",
    "--add-data=logo/logoDownloader.ico;logo",
    "--add-data=logo/logoDownloader.png;logo",
    "--hidden-import=tkinter",
    "--hidden-import=yt_dlp",
    "--clean",
    "--noconfirm",
    "main.py"
]

result = subprocess.run(cmd)

if result.returncode != 0:
    print()
    print("❌ Error al crear ejecutable")
    sys.exit(1)

print()
print("=" * 50)
print("✅ EJECUTABLE CREADO EXITOSAMENTE")
print("=" * 50)
print()
print(f"📁 Ubicación: {Path('dist/DescargadorVideos.exe').absolute()}")
print()
print("🎉 ¡Listo para usar!")
print()
print("📝 Notas importantes:")
print("   • Los usuarios necesitarán FFmpeg instalado")
print("   • El ejecutable incluye todas las dependencias de Python")
print("   • Tamaño aproximado: ~50-80 MB")
