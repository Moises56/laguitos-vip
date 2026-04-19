"""
🎥 Descargador Universal de Videos
Punto de entrada principal de la aplicación

Autor: Video Downloader Team
Versión: 1.0.0
"""
import sys
import logging
from pathlib import Path

# Agregar la carpeta del proyecto al path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from gui.app import iniciar_app
from downloader.config import LOG_FILE, LOG_FORMAT

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Función principal."""
    try:
        logger.info("=" * 50)
        logger.info("🎥 Iniciando Descargador Universal de Videos")
        logger.info("=" * 50)
        
        # Iniciar aplicación GUI
        iniciar_app()
        
        logger.info("Aplicación cerrada correctamente")
        
    except Exception as e:
        logger.error(f"Error fatal en la aplicación: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
