"""
Script de prueba para el descargador
Prueba las funcionalidades básicas sin GUI
"""
import sys
from pathlib import Path

# Agregar el proyecto al path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from downloader.core import VideoDownloader
from downloader.utils import validar_url, verificar_ffmpeg, extraer_info_plataforma


def test_validacion_urls():
    """Prueba la validación de URLs."""
    print("=" * 60)
    print("🧪 Test: Validación de URLs")
    print("=" * 60)
    
    urls_test = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.tiktok.com/@user/video/123456",
        "https://www.instagram.com/p/ABC123/",
        "https://invalid-url",
        "",
        "https://www.google.com"
    ]
    
    for url in urls_test:
        es_valida, mensaje = validar_url(url)
        plataforma = extraer_info_plataforma(url) if es_valida else None
        
        status = "✅" if es_valida else "❌"
        print(f"\n{status} URL: {url[:50]}...")
        print(f"   Válida: {es_valida}")
        print(f"   Plataforma: {plataforma}")
        if not es_valida:
            print(f"   Mensaje: {mensaje}")


def test_ffmpeg():
    """Verifica si FFmpeg está instalado."""
    print("\n" + "=" * 60)
    print("🧪 Test: Verificación de FFmpeg")
    print("=" * 60)
    
    ffmpeg_ok, resultado = verificar_ffmpeg()
    
    if ffmpeg_ok:
        print(f"✅ FFmpeg encontrado: {resultado}")
    else:
        print(f"❌ FFmpeg no encontrado")
        print(f"   {resultado}")
        print("\n⚠️  Necesitas FFmpeg para descargar audio (MP3)")


def test_estructura_proyecto():
    """Verifica la estructura del proyecto."""
    print("\n" + "=" * 60)
    print("🧪 Test: Estructura del proyecto")
    print("=" * 60)
    
    carpetas_requeridas = [
        "downloader",
        "gui",
        "downloads",
        "logs"
    ]
    
    archivos_requeridos = [
        "main.py",
        "requirements.txt",
        "README.md",
        "downloader/__init__.py",
        "downloader/config.py",
        "downloader/core.py",
        "downloader/utils.py",
        "gui/__init__.py",
        "gui/app.py"
    ]
    
    print("\n📁 Verificando carpetas:")
    for carpeta in carpetas_requeridas:
        ruta = PROJECT_ROOT / carpeta
        existe = ruta.exists() and ruta.is_dir()
        status = "✅" if existe else "❌"
        print(f"   {status} {carpeta}/")
    
    print("\n📄 Verificando archivos:")
    for archivo in archivos_requeridos:
        ruta = PROJECT_ROOT / archivo
        existe = ruta.exists() and ruta.is_file()
        status = "✅" if existe else "❌"
        print(f"   {status} {archivo}")


def test_importaciones():
    """Verifica que todas las importaciones funcionan."""
    print("\n" + "=" * 60)
    print("🧪 Test: Importaciones de módulos")
    print("=" * 60)
    
    modulos = [
        ("yt_dlp", "YoutubeDL"),
        ("downloader.config", "GUI_CONFIG"),
        ("downloader.core", "VideoDownloader"),
        ("downloader.utils", "validar_url"),
        ("gui.app", "VideoDownloaderApp")
    ]
    
    errores = 0
    for modulo, objeto in modulos:
        try:
            exec(f"from {modulo} import {objeto}")
            print(f"   ✅ {modulo}.{objeto}")
        except Exception as e:
            print(f"   ❌ {modulo}.{objeto} - Error: {e}")
            errores += 1
    
    if errores == 0:
        print("\n✅ Todas las importaciones exitosas")
    else:
        print(f"\n❌ {errores} error(es) de importación")


def main():
    """Ejecuta todas las pruebas."""
    print("\n")
    print("🎥" * 30)
    print("DESCARGADOR UNIVERSAL DE VIDEOS - SUITE DE PRUEBAS")
    print("🎥" * 30)
    
    try:
        test_estructura_proyecto()
        test_importaciones()
        test_validacion_urls()
        test_ffmpeg()
        
        print("\n" + "=" * 60)
        print("✅ PRUEBAS COMPLETADAS")
        print("=" * 60)
        print("\n💡 Sugerencias:")
        print("   - Si FFmpeg no está instalado, no podrás descargar audio")
        print("   - Para ejecutar la aplicación: python main.py")
        print("   - Para más información: ver GUIA_USO.md")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
