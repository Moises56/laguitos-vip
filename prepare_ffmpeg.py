"""
Script para preparar FFmpeg para incluirlo en el ejecutable.
Copia FFmpeg a la carpeta del proyecto para que PyInstaller lo incluya.
"""
import shutil
import subprocess
from pathlib import Path

def find_ffmpeg():
    """Encuentra FFmpeg en el sistema"""
    # Buscar en WinGet
    winget_path = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    if winget_path.exists():
        for ffmpeg_exe in winget_path.rglob("ffmpeg.exe"):
            return ffmpeg_exe.parent
    
    # Buscar en PATH
    try:
        result = subprocess.run(
            ["where", "ffmpeg"],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0:
            ffmpeg_path = Path(result.stdout.strip().split('\n')[0])
            return ffmpeg_path.parent
    except:
        pass
    
    return None

print("🔍 Buscando FFmpeg en el sistema...")
ffmpeg_dir = find_ffmpeg()

if not ffmpeg_dir:
    print("❌ Error: FFmpeg no encontrado en el sistema")
    print("   Instala FFmpeg primero:")
    print("   winget install Gyan.FFmpeg")
    exit(1)

print(f"✅ FFmpeg encontrado: {ffmpeg_dir}")

# Crear carpeta para FFmpeg en el proyecto
ffmpeg_bundle_dir = Path("ffmpeg_bundle")
ffmpeg_bundle_dir.mkdir(exist_ok=True)

# Archivos necesarios de FFmpeg
required_files = ["ffmpeg.exe", "ffprobe.exe"]

print("\n📦 Copiando archivos de FFmpeg...")
for filename in required_files:
    src = ffmpeg_dir / filename
    dst = ffmpeg_bundle_dir / filename
    
    if src.exists():
        shutil.copy2(src, dst)
        size_mb = dst.stat().st_size / (1024 * 1024)
        print(f"   ✅ {filename} ({size_mb:.1f} MB)")
    else:
        print(f"   ⚠️  {filename} no encontrado")

print("\n✅ FFmpeg preparado para incluir en el ejecutable")
print(f"📁 Ubicación: {ffmpeg_bundle_dir.absolute()}")
