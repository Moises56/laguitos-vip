"""
Configuración y constantes del descargador de videos
"""
import os
from pathlib import Path

# -----------------------------------------------------
# Rutas del proyecto
# -----------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
DOWNLOADS_FOLDER = PROJECT_ROOT / "downloads"
LOGS_FOLDER = PROJECT_ROOT / "logs"
# Cookies.txt opcional: si existe, se usa con prioridad sobre las cookies del navegador.
# Necesario en Chrome/Edge v127+ por el problema de App-Bound Encryption (DPAPI).
# Exportar con la extensión "Get cookies.txt LOCALLY" estando logueado en YouTube.
COOKIES_FILE = PROJECT_ROOT / "cookies.txt"

# Crear carpetas si no existen
DOWNLOADS_FOLDER.mkdir(exist_ok=True)
LOGS_FOLDER.mkdir(exist_ok=True)

# -----------------------------------------------------
# Configuración de logging
# -----------------------------------------------------
LOG_FILE = LOGS_FOLDER / "downloader.log"
LOG_FORMAT = '%(asctime)s - [%(levelname)s] - %(message)s'
LOG_LEVEL = 'INFO'

# -----------------------------------------------------
# Configuración de yt-dlp
# -----------------------------------------------------
# Formatos de video soportados
VIDEO_FORMATS = {
    'mejor': 'bestvideo+bestaudio/best',
    '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
    '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
    '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]'
}

# Configuración de audio
AUDIO_CONFIG = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

# Opciones base de yt-dlp
BASE_YTDLP_OPTIONS = {
    'noplaylist': True,
    'quiet': False,  # False para permitir progress_hooks
    'no_warnings': False,  # Mostrar advertencias
    'extract_flat': False,
    'noprogress': False,  # Habilitar reportes de progreso para la GUI
    'verbose': False,  # No mostrar demasiada información
    # --- Anti-403 / robustez de red ---
    'retries': 5,
    'fragment_retries': 3,  # Bajo: si los fragmentos dan 403, fallar rápido en vez de colgarse
    'retry_sleep_functions': {'http': lambda n: min(4 * (n + 1), 30), 'fragment': lambda n: min(2 * (n + 1), 10)},
    'geo_bypass': True,
    'nocheckcertificate': True,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept': '*/*',
    },
    # JS runtime para resolver el "n challenge" y la firma de YouTube (yt-dlp 2026+).
    # Requiere Node.js instalado en PATH. Sin esto, solo se obtienen storyboards (imágenes).
    # Ver: https://github.com/yt-dlp/yt-dlp/wiki/EJS
    'js_runtimes': {'node': {}},
    # Dejamos el set de player_client por defecto de yt-dlp — con node + cookies elige bien.
    # Las cookies se inyectan dinámicamente en core.py:
    #   - Si existe COOKIES_FILE → 'cookiefile'
    #   - Si no → fallback en cascada con 'cookiesfrombrowser' (chrome/edge/firefox)
}

# -----------------------------------------------------
# Plataformas soportadas (regex patterns)
# -----------------------------------------------------
SUPPORTED_PLATFORMS = [
    'youtube.com',
    'youtu.be',
    'tiktok.com',
    'instagram.com',
    'facebook.com',
    'fb.watch',
    'ok.ru',
    'twitter.com',
    'x.com',
    'vimeo.com',
    'dailymotion.com',
    'twitch.tv'
]

# -----------------------------------------------------
# Mensajes de la aplicación
# -----------------------------------------------------
MESSAGES = {
    'download_started': '🎬 Iniciando descarga...',
    'download_complete': '✅ Descarga completada correctamente',
    'download_error': '❌ Error durante la descarga',
    'invalid_url': '⚠️ URL no válida o no soportada',
    'ffmpeg_not_found': '⚠️ FFmpeg no encontrado. Necesario para convertir audio.',
    'processing': '🔄 Procesando archivo...',
}

# -----------------------------------------------------
# Configuración de la GUI
# -----------------------------------------------------
GUI_CONFIG = {
    'window_title': '🎥 Descargador Universal de Videos',
    'window_size': '600x550',  # Aumentado para incluir botones de control
    'resizable': False,
    'theme_color': '#4CAF50',
    'font_family': 'Arial',
}

# -----------------------------------------------------
# Configuración de Procesamiento
# -----------------------------------------------------
PROCESSING_CONFIG = {
    'auto_convert': True,  # Reconvertir solo si es necesario (verifica codecs)
    'force_convert': False,  # Forzar reconversión siempre (para máxima compatibilidad)
}
