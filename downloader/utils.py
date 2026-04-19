"""
Utilidades y funciones auxiliares para el descargador
"""
import os
import re
import shutil
import logging
from urllib.parse import urlparse
from typing import Tuple, Optional
from .config import SUPPORTED_PLATFORMS, MESSAGES

# Configurar logger
logger = logging.getLogger(__name__)


def validar_url(url: str) -> Tuple[bool, str]:
    """
    Valida si una URL es válida y está soportada.
    
    Args:
        url: URL a validar
        
    Returns:
        Tuple (es_valida, mensaje)
    """
    if not url or not url.strip():
        return False, "La URL está vacía"
    
    url = url.strip()
    
    # Verificar formato básico de URL
    try:
        resultado = urlparse(url)
        if not all([resultado.scheme, resultado.netloc]):
            return False, "Formato de URL inválido"
    except Exception as e:
        return False, f"Error al analizar URL: {str(e)}"
    
    # Verificar si la plataforma está soportada
    dominio = resultado.netloc.lower()
    
    # Remover 'www.' si existe
    if dominio.startswith('www.'):
        dominio = dominio[4:]
    
    plataforma_soportada = any(
        platform in dominio for platform in SUPPORTED_PLATFORMS
    )
    
    if not plataforma_soportada:
        return False, MESSAGES['invalid_url']
    
    return True, "URL válida"


def verificar_ffmpeg() -> Tuple[bool, str]:
    """
    Verifica si FFmpeg está instalado en el sistema.
    Primero busca el FFmpeg incluido en el ejecutable (modo portable).
    Prueba múltiples métodos y ubicaciones comunes.
    
    Returns:
        Tuple (está_instalado, ruta_o_mensaje)
    """
    import subprocess
    import sys
    from pathlib import Path
    
    # Método 0: FFmpeg incluido en el ejecutable (PORTABLE - SIN INSTALACIÓN)
    if getattr(sys, 'frozen', False):
        # Estamos ejecutando como EXE
        exe_dir = Path(sys._MEIPASS)  # Carpeta temporal de PyInstaller
        bundled_ffmpeg = exe_dir / 'ffmpeg_bundle' / 'ffmpeg.exe'
        
        if bundled_ffmpeg.exists():
            logger.info(f"✅ Usando FFmpeg incluido (portable): {bundled_ffmpeg}")
            return True, str(bundled_ffmpeg)
    else:
        # Modo desarrollo: buscar en ffmpeg_bundle del proyecto
        project_dir = Path(__file__).parent.parent
        bundled_ffmpeg = project_dir / 'ffmpeg_bundle' / 'ffmpeg.exe'
        
        if bundled_ffmpeg.exists():
            logger.info(f"✅ Usando FFmpeg del proyecto: {bundled_ffmpeg}")
            return True, str(bundled_ffmpeg)
    
    # Método 1: Buscar con shutil.which
    ffmpeg_path = shutil.which('ffmpeg')
    
    if ffmpeg_path:
        logger.info(f"FFmpeg encontrado en PATH: {ffmpeg_path}")
        return True, ffmpeg_path
    
    # Método 2: Buscar en ubicaciones comunes de Windows
    ubicaciones_comunes = [
        # WinGet
        Path(os.environ.get('LOCALAPPDATA', '')) / 'Microsoft' / 'WinGet' / 'Packages',
        # Instalación manual común
        Path('C:/ffmpeg/bin'),
        Path('C:/Program Files/ffmpeg/bin'),
        Path('C:/Program Files (x86)/ffmpeg/bin'),
    ]
    
    for ubicacion in ubicaciones_comunes:
        if ubicacion.exists():
            # Buscar ffmpeg.exe recursivamente
            for ffmpeg_exe in ubicacion.rglob('ffmpeg.exe'):
                try:
                    # Verificar que funciona
                    resultado = subprocess.run(
                        [str(ffmpeg_exe), '-version'],
                        capture_output=True,
                        timeout=5,
                        text=True
                    )
                    if resultado.returncode == 0:
                        logger.info(f"FFmpeg encontrado en: {ffmpeg_exe}")
                        return True, str(ffmpeg_exe)
                except Exception:
                    continue
    
    # Método 3: Intentar ejecutar ffmpeg directamente (alias de shell)
    try:
        resultado = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            timeout=5,
            text=True,
            shell=True  # Usar shell para detectar alias
        )
        if resultado.returncode == 0 and 'ffmpeg version' in resultado.stdout:
            logger.info("FFmpeg detectado (alias/comando de shell)")
            return True, "ffmpeg (disponible via shell)"
    except Exception:
        pass
    
    # No encontrado
    logger.warning("FFmpeg no encontrado en el sistema")
    return False, MESSAGES['ffmpeg_not_found']


def sanitizar_nombre_archivo(nombre: str) -> str:
    """
    Limpia un nombre de archivo de caracteres no permitidos.
    
    Args:
        nombre: Nombre de archivo a limpiar
        
    Returns:
        Nombre de archivo sanitizado
    """
    # Caracteres no permitidos en nombres de archivo
    caracteres_invalidos = r'[<>:"/\\|?*]'
    nombre_limpio = re.sub(caracteres_invalidos, '_', nombre)
    
    # Limitar longitud
    if len(nombre_limpio) > 200:
        nombre_limpio = nombre_limpio[:200]
    
    return nombre_limpio.strip()


def formatear_tamaño(bytes: int) -> str:
    """
    Convierte bytes a formato legible (KB, MB, GB).
    
    Args:
        bytes: Tamaño en bytes
        
    Returns:
        String con tamaño formateado
    """
    for unidad in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unidad}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"


def extraer_info_plataforma(url: str) -> Optional[str]:
    """
    Extrae el nombre de la plataforma desde una URL.
    
    Args:
        url: URL del video
        
    Returns:
        Nombre de la plataforma o None
    """
    try:
        resultado = urlparse(url)
        dominio = resultado.netloc.lower()
        
        if 'youtube.com' in dominio or 'youtu.be' in dominio:
            return 'YouTube'
        elif 'tiktok.com' in dominio:
            return 'TikTok'
        elif 'instagram.com' in dominio:
            return 'Instagram'
        elif 'facebook.com' in dominio or 'fb.watch' in dominio:
            return 'Facebook'
        elif 'ok.ru' in dominio:
            return 'OK.ru'
        elif 'twitter.com' in dominio or 'x.com' in dominio:
            return 'Twitter/X'
        elif 'vimeo.com' in dominio:
            return 'Vimeo'
        elif 'dailymotion.com' in dominio:
            return 'Dailymotion'
        elif 'twitch.tv' in dominio:
            return 'Twitch'
        else:
            return 'Desconocida'
    except Exception:
        return None
