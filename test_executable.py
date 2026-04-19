"""
Script para probar el ejecutable y verificar FFmpeg
"""
import sys
from pathlib import Path
from downloader.utils import verificar_ffmpeg

print("=" * 60)
print("🔍 TEST DE EJECUTABLE - VERIFICACIÓN DE FFMPEG")
print("=" * 60)

# Información del entorno
print("\n📌 Información del entorno:")
print(f"   • sys.frozen: {getattr(sys, 'frozen', False)}")
if getattr(sys, 'frozen', False):
    print(f"   • sys._MEIPASS: {sys._MEIPASS}")
else:
    print(f"   • Directorio actual: {Path.cwd()}")
    print(f"   • Directorio script: {Path(__file__).parent}")

# Verificar FFmpeg
print("\n🔍 Verificando FFmpeg...")
encontrado, ruta = verificar_ffmpeg()

print(f"\n📊 Resultado:")
print(f"   • FFmpeg encontrado: {'✅ SÍ' if encontrado else '❌ NO'}")
print(f"   • Ruta/Mensaje: {ruta}")

if encontrado:
    ffmpeg_path = Path(ruta)
    if ffmpeg_path.exists():
        size_mb = ffmpeg_path.stat().st_size / (1024 * 1024)
        print(f"   • Tamaño: {size_mb:.2f} MB")
        print(f"   • Ubicación tipo: {'BUNDLED (Portable)' if 'ffmpeg_bundle' in str(ffmpeg_path) else 'SISTEMA'}")

print("\n" + "=" * 60)
