"""
Módulo principal de descarga de videos usando yt-dlp
"""
import os
import logging
import subprocess
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from yt_dlp import YoutubeDL

from .config import (
    DOWNLOADS_FOLDER,
    VIDEO_FORMATS,
    AUDIO_CONFIG,
    BASE_YTDLP_OPTIONS,
    COOKIES_FILE,
    MESSAGES,
    LOG_FILE,
    LOG_FORMAT
)
from .utils import validar_url, verificar_ffmpeg, extraer_info_plataforma

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def sanitizar_nombre_archivo(nombre: str, max_length: int = 150) -> str:
    """
    Sanitiza el nombre de archivo para evitar problemas en Windows.
    
    Args:
        nombre: Nombre original del archivo
        max_length: Longitud máxima del nombre (sin extensión)
    
    Returns:
        Nombre sanitizado y truncado si es necesario
    """
    # Caracteres no permitidos en Windows
    caracteres_invalidos = '<>:"/\\|?*'
    
    # Reemplazar caracteres inválidos
    for char in caracteres_invalidos:
        nombre = nombre.replace(char, '')
    
    # Remover emojis y caracteres especiales problemáticos
    nombre = ''.join(char for char in nombre if ord(char) < 127 or char.isalnum() or char in ' .-_')
    
    # Limpiar espacios múltiples
    nombre = ' '.join(nombre.split())
    
    # Truncar si es muy largo
    if len(nombre) > max_length:
        nombre = nombre[:max_length].rstrip()
    
    return nombre


class VideoDownloader:
    """
    Clase para manejar la descarga de videos y audio desde múltiples plataformas.
    """
    
    def __init__(self, carpeta_destino: Optional[Path] = None):
        """
        Inicializa el descargador.
        
        Args:
            carpeta_destino: Carpeta donde guardar descargas (opcional)
        """
        self.carpeta_destino = carpeta_destino or DOWNLOADS_FOLDER
        # Crear la carpeta y todas las subcarpetas necesarias
        self.carpeta_destino.mkdir(parents=True, exist_ok=True)
        self.progreso_callback = None
        self.cancelar_descarga = False
        self.pausar_descarga = False
        
    def set_progreso_callback(self, callback: Callable):
        """
        Establece una función callback para reportar progreso.
        
        Args:
            callback: Función que recibe el diccionario de progreso
        """
        self.progreso_callback = callback
    
    def cancelar(self):
        """Cancela la descarga actual."""
        self.cancelar_descarga = True
        logger.info("🚫 Cancelando descarga...")
    
    def pausar(self):
        """Pausa la descarga actual."""
        self.pausar_descarga = True
        logger.info("⏸️ Pausando descarga...")
    
    def reanudar(self):
        """Reanuda la descarga pausada."""
        self.pausar_descarga = False
        logger.info("▶️ Reanudando descarga...")
    
    def _hook_progreso(self, d: Dict[str, Any]):
        """
        Hook interno para capturar el progreso de descarga.
        
        Args:
            d: Diccionario con información de progreso de yt-dlp
        """
        # Verificar si se debe cancelar
        if self.cancelar_descarga:
            raise Exception("Descarga cancelada por el usuario")
        
        # Manejar pausa
        import time
        while self.pausar_descarga:
            time.sleep(0.1)
            if self.cancelar_descarga:
                raise Exception("Descarga cancelada por el usuario")
        
        if self.progreso_callback:
            self.progreso_callback(d)
        
        # Log del progreso
        if d['status'] == 'downloading':
            porcentaje = d.get('_percent_str', '0%')
            velocidad = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            logger.info(f"⏬ Descargando: {porcentaje} | {velocidad} | ETA: {eta}")
        elif d['status'] == 'finished':
            logger.info("Descarga finalizada. Procesando archivo...")
    
    def _verificar_codecs(self, filename: str, ffmpeg_path: str) -> tuple:
        """
        Verifica los codecs de video y audio del archivo.
        
        Args:
            filename: Ruta del archivo a verificar
            ffmpeg_path: Ruta al ejecutable de FFmpeg
            
        Returns:
            Tupla (video_codec, audio_codec)
        """
        try:
            ffmpeg_dir = str(Path(ffmpeg_path).parent)
            ffprobe_exe = str(Path(ffmpeg_dir) / 'ffprobe.exe')
            
            # Comando para obtener información de codecs
            cmd = [
                ffprobe_exe,
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_name',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                filename
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            video_codec = result.stdout.strip() if result.returncode == 0 else None
            
            # Obtener codec de audio
            cmd[3] = 'a:0'  # Cambiar a stream de audio
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            audio_codec = result.stdout.strip() if result.returncode == 0 else None
            
            return (video_codec, audio_codec)
        except Exception as e:
            logger.warning(f"No se pudieron verificar codecs: {e}")
            return (None, None)
    
    def _reconvertir_para_compatibilidad(self, filename: str, ffmpeg_path: str) -> str:
        """
        Reconvierte el video a formato compatible con WhatsApp y redes sociales.
        Solo reconvierte si los codecs no son H.264 + AAC.
        
        Args:
            filename: Ruta del archivo a reconvertir
            ffmpeg_path: Ruta al ejecutable de FFmpeg
            
        Returns:
            Ruta del archivo reconvertido (o el original si no es necesario)
        """
        try:
            # Verificar codecs actuales
            video_codec, audio_codec = self._verificar_codecs(filename, ffmpeg_path)
            
            logger.info(f"📹 Codecs detectados - Video: {video_codec}, Audio: {audio_codec}")
            
            # Si ya tiene H.264 y AAC, no reconvertir
            if video_codec == 'h264' and audio_codec == 'aac':
                logger.info("✅ Video ya está en formato compatible (H.264 + AAC) - No se requiere reconversión")
                return filename
            
            # Si necesita reconversión, informar y proceder
            logger.info(f"🔄 Reconversión necesaria: {video_codec}/{audio_codec} → H.264/AAC")
            # Crear nombre temporal
            temp_filename = filename.rsplit('.', 1)[0] + '_temp.mp4'
            
            logger.info("🔄 Reconvirtiendo video para máxima compatibilidad...")
            
            # Notificar progreso: Iniciando procesamiento
            if self.progreso_callback:
                self.progreso_callback({
                    'status': 'processing',
                    'message': 'Convirtiendo a formato compatible...'
                })
            
            # Comando FFmpeg para reconvertir con codecs universales
            ffmpeg_dir = str(Path(ffmpeg_path).parent)
            ffmpeg_exe = str(Path(ffmpeg_dir) / 'ffmpeg.exe')
            
            # Obtener tamaño del archivo para estimar tiempo
            file_size_mb = os.path.getsize(filename) / (1024 * 1024)
            estimated_time = int(file_size_mb * 0.5)  # Aproximadamente 0.5 seg por MB con veryfast
            
            logger.info(f"📦 Tamaño: {file_size_mb:.1f}MB | Tiempo estimado: ~{estimated_time}s")
            
            cmd = [
                ffmpeg_exe,
                '-i', filename,              # Archivo de entrada
                '-c:v', 'libx264',          # Codec video H.264
                '-preset', 'veryfast',      # Más rápido (ultrafast, superfast, veryfast, faster, fast, medium)
                '-crf', '23',               # Calidad constante (18-28 bueno)
                '-c:a', 'aac',              # Codec audio AAC
                '-b:a', '128k',             # Bitrate audio
                '-movflags', '+faststart',  # Optimización web
                '-y',                       # Sobrescribir sin preguntar
                temp_filename
            ]
            
            # Ejecutar FFmpeg (subprocess ya está importado arriba)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            if result.returncode == 0:
                # Reemplazar archivo original con el reconvertido (os ya está importado)
                os.replace(temp_filename, filename)
                logger.info("✅ Video reconvertido exitosamente (H.264 + AAC)")
                return filename
            else:
                logger.warning(f"⚠️ No se pudo reconvertir: {result.stderr[:200]}")
                # Limpiar archivo temporal si existe
                if Path(temp_filename).exists():
                    Path(temp_filename).unlink()
                return filename
                
        except Exception as e:
            logger.warning(f"⚠️ Error al reconvertir: {e}")
            return filename
    
    def descargar(
        self,
        url: str,
        solo_audio: bool = False,
        calidad: str = 'mejor'
    ) -> Dict[str, Any]:
        """
        Descarga un video o audio desde una URL.
        
        Args:
            url: URL del video a descargar
            solo_audio: Si es True, solo descarga audio (MP3)
            calidad: Calidad del video ('mejor', '1080p', '720p', '480p')
            
        Returns:
            Diccionario con resultado de la descarga:
            {
                'success': bool,
                'message': str,
                'file_path': str (si success=True),
                'platform': str
            }
        """
        # Resetear flags de control
        self.cancelar_descarga = False
        self.pausar_descarga = False
        
        # Validar URL
        es_valida, mensaje = validar_url(url)
        if not es_valida:
            logger.error(f"URL inválida: {mensaje}")
            return {
                'success': False,
                'message': mensaje,
                'file_path': None,
                'platform': None
            }
        
        # Extraer plataforma
        plataforma = extraer_info_plataforma(url)
        logger.info(f"Descargando desde: {plataforma}")
        
        # Verificar FFmpeg
        ffmpeg_ok, ffmpeg_path = verificar_ffmpeg()
        
        # Configurar opciones de yt-dlp
        opciones = BASE_YTDLP_OPTIONS.copy()
        
        # Template de salida limitando el nombre a 80 caracteres para evitar rutas muy largas
        opciones['outtmpl'] = str(self.carpeta_destino / '%(title).80s.%(ext)s')
        opciones['progress_hooks'] = [self._hook_progreso]
        
        # Restricciones para nombres de archivo seguros y compatibles
        opciones['windowsfilenames'] = True  # Nombres compatibles con Windows
        opciones['restrictfilenames'] = True  # Eliminar caracteres especiales y emojis (solo ASCII seguro)
        
        # Si FFmpeg está disponible, indicarle a yt-dlp dónde está
        if ffmpeg_ok and ffmpeg_path:
            # Extraer el directorio que contiene ffmpeg.exe
            if ffmpeg_path.endswith('.exe'):
                ffmpeg_dir = str(Path(ffmpeg_path).parent)
                opciones['ffmpeg_location'] = ffmpeg_dir
                logger.debug(f"Usando FFmpeg desde: {ffmpeg_dir}")
        
        # Configurar formato según elección y disponibilidad de FFmpeg
        if solo_audio:
            if not ffmpeg_ok:
                logger.warning(ffmpeg_path)
                return {
                    'success': False,
                    'message': 'FFmpeg no está instalado. Es necesario para descargar audio.\nConsulta INSTALAR_FFMPEG.md para instrucciones.',
                    'file_path': None,
                    'platform': plataforma
                }
            opciones.update(AUDIO_CONFIG)
        else:
            # Si FFmpeg NO está disponible, usar formato pre-fusionado (no requiere merge)
            if not ffmpeg_ok:
                logger.warning(f"{ffmpeg_path} - Usando formato sin fusión")
                # Usar formato que ya incluye video+audio (sin necesidad de merge)
                opciones['format'] = 'best'
            else:
                # Con FFmpeg disponible, podemos fusionar video y audio separados
                # Optimizar para velocidad: preferir formatos ya fusionados cuando sea posible
                formato = VIDEO_FORMATS.get(calidad, VIDEO_FORMATS['mejor'])
                opciones['format'] = formato
                opciones['merge_output_format'] = 'mp4'
                
                # Opciones de optimización para velocidad
                opciones['concurrent_fragment_downloads'] = 5  # Descargas paralelas de fragmentos
                opciones['http_chunk_size'] = 10485760  # 10MB chunks para mejor velocidad
        
        # Realizar descarga
        try:
            logger.info(MESSAGES['download_started'])
            logger.info(f"URL: {url}")
            logger.info(f"Modo: {'Audio (MP3)' if solo_audio else f'Video ({calidad})'}")

            # Estrategia de cookies en orden de preferencia:
            #   1) cookies.txt en la raíz del proyecto (la más fiable; evita DPAPI)
            #   2) cookies del navegador (chrome → edge → firefox)
            #   3) sin cookies (sirve para TikTok, Instagram pública, etc.)
            cookie_attempts = []
            if COOKIES_FILE.exists():
                cookie_attempts.append(('file', str(COOKIES_FILE)))
            cookie_attempts.extend([('browser', ('chrome',)),
                                    ('browser', ('edge',)),
                                    ('browser', ('firefox',)),
                                    ('none', None)])

            # Triggers que indican fallo de cookies → reintentar con la siguiente fuente
            cookie_error_triggers = (
                'cookie', 'sign in to confirm', 'could not copy',
                'database is locked', 'permission', 'dpapi', 'decrypt',
                'unsupported browser',
            )

            info = None
            ydl = None
            last_error = None
            for kind, value in cookie_attempts:
                intento_opts = opciones.copy()
                intento_opts.pop('cookiesfrombrowser', None)
                intento_opts.pop('cookiefile', None)
                if kind == 'file':
                    intento_opts['cookiefile'] = value
                    logger.info(f"🍪 Usando cookies.txt: {value}")
                elif kind == 'browser':
                    intento_opts['cookiesfrombrowser'] = value
                    logger.info(f"🍪 Usando cookies del navegador: {value[0]}")
                else:
                    logger.info("🍪 Reintentando sin cookies...")
                try:
                    ydl = YoutubeDL(intento_opts)
                    info = ydl.extract_info(url, download=True)
                    break  # éxito
                except Exception as e:
                    err_str = str(e).lower()
                    if any(t in err_str for t in cookie_error_triggers):
                        last_error = e
                        logger.warning(f"⚠️ Falló con {kind}={value}: {str(e)[:180]}")
                        continue
                    raise  # otro tipo de error → salir
            if info is None or ydl is None:
                hint = (
                    "\n\n💡 SOLUCIÓN: YouTube exige cookies de sesión.\n"
                    "   1) Instala la extensión 'Get cookies.txt LOCALLY' en Chrome.\n"
                    "   2) Entra a youtube.com (logueado) y exporta cookies.\n"
                    f"   3) Guarda el archivo como: {COOKIES_FILE}"
                )
                raise Exception(f"{last_error}{hint}" if last_error else f"No se pudo extraer información del video.{hint}")

            # Obtener ruta del archivo descargado
            if solo_audio:
                filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
            else:
                filename = ydl.prepare_filename(info)

            logger.info(MESSAGES['download_complete'])
            logger.info(f"Archivo guardado: {filename}")

            # Si es video y FFmpeg está disponible, reconvertir para compatibilidad
            if not solo_audio and ffmpeg_ok and ffmpeg_path:
                filename = self._reconvertir_para_compatibilidad(filename, ffmpeg_path)

            # Guardar en historial
            try:
                from .historial import HistorialDescargas
                historial = HistorialDescargas()
                historial.agregar(
                    url=url,
                    titulo=info.get('title', 'Sin título'),
                    ruta_archivo=filename,
                    plataforma=plataforma or 'Desconocida',
                    tipo='audio' if solo_audio else 'video'
                )
            except Exception as e:
                logger.warning(f"Error al guardar en historial: {e}")

            return {
                'success': True,
                'message': MESSAGES['download_complete'],
                'file_path': filename,
                'platform': plataforma,
                'title': info.get('title', 'Sin título'),
                'type': 'audio' if solo_audio else 'video'
            }

        except Exception as e:
            error_msg = f"{MESSAGES['download_error']}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'message': error_msg,
                'file_path': None,
                'platform': plataforma
            }


# Función de conveniencia para uso simple
def descargar_video(
    url: str,
    solo_audio: bool = False,
    calidad: str = 'mejor',
    carpeta_destino: Optional[Path] = None,
    progreso_callback: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Función simple para descargar un video.
    
    Args:
        url: URL del video
        solo_audio: Si es True, solo descarga audio
        calidad: Calidad del video
        carpeta_destino: Carpeta de destino (opcional)
        progreso_callback: Función callback para progreso (opcional)
        
    Returns:
        Diccionario con resultado de la descarga
    """
    downloader = VideoDownloader(carpeta_destino)
    if progreso_callback:
        downloader.set_progreso_callback(progreso_callback)
    return downloader.descargar(url, solo_audio, calidad)
