# Script PowerShell para crear el ejecutable
# build.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 Creando Ejecutable de Descargador de Videos" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Limpiar builds anteriores
Write-Host "🧹 Limpiando builds anteriores..." -ForegroundColor Yellow
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "   ✅ Carpeta 'dist' eliminada" -ForegroundColor Green
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "   ✅ Carpeta 'build' eliminada" -ForegroundColor Green
}
Write-Host ""

# 2. Convertir logo
Write-Host "🎨 Convirtiendo logo..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe convert_logo.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al convertir logo" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 3. Crear ejecutable con PyInstaller
Write-Host "📦 Creando ejecutable con PyInstaller..." -ForegroundColor Yellow
.\.venv\Scripts\pyinstaller.exe --clean --noconfirm DescargadorVideos.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al crear ejecutable" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 4. Crear README para distribución
Write-Host "📝 Creando README para distribución..." -ForegroundColor Yellow
$readmeContent = @"
# Descargador Universal de Videos
## Versión: 1.0.0

### 🎥 Características:
- Descarga videos de múltiples plataformas (YouTube, TikTok, Facebook, Instagram, OK.ru, etc.)
- Descarga solo audio en formato MP3
- Selección de calidad de video (mejor, 1080p, 720p, 480p)
- Reconversión automática a formato compatible con WhatsApp (H.264 + AAC)
- Historial de descargas
- Organización automática de archivos por plataforma

### 📋 Requisitos:
- Windows 10/11 (64-bit)
- **FFmpeg** (IMPORTANTE): Debes instalar FFmpeg para funcionalidad completa
  - Descarga: https://www.gyan.dev/ffmpeg/builds/
  - O instala con winget: ``winget install Gyan.FFmpeg``

### 🚀 Uso:
1. Ejecuta ``DescargadorVideos.exe``
2. Pega la URL del video
3. Selecciona calidad o solo audio
4. Elige carpeta de destino
5. Haz clic en "Descargar"

### ⚙️ Configuración de FFmpeg:
El programa detectará automáticamente FFmpeg si está instalado.
Sin FFmpeg, solo podrás descargar videos (sin audio MP3).

### 📁 Estructura de Carpetas:
downloads/
  ├── RedesSociales/
  │   ├── Facebook/
  │   ├── TikTok/
  │   └── Instagram/
  ├── Peliculas-EN/
  ├── Peliculas-ES/
  └── Songs/

### 🆘 Soporte:
Si encuentras problemas, revisa:
- FFmpeg está instalado correctamente
- Tienes permisos de escritura en la carpeta de descargas
- La URL es válida y pública

### 📜 Licencia:
Este software es de uso libre para fines personales.

---
Desarrollado con ❤️ usando Python, yt-dlp y Tkinter
"@

Set-Content -Path "dist\README.txt" -Value $readmeContent -Encoding UTF8
Write-Host "   ✅ README.txt creado" -ForegroundColor Green
Write-Host ""

# 5. Resumen final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ EJECUTABLE CREADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 Ubicación: .\dist\DescargadorVideos.exe" -ForegroundColor White
Write-Host ""
Write-Host "📦 Para distribuir:" -ForegroundColor Yellow
Write-Host "   1. Comprime la carpeta 'dist' completa" -ForegroundColor White
Write-Host "   2. Incluye el README.txt con instrucciones" -ForegroundColor White
Write-Host "   3. Recuerda que los usuarios necesitan FFmpeg instalado" -ForegroundColor White
Write-Host ""
Write-Host "🎉 ¡Listo para usar!" -ForegroundColor Green
