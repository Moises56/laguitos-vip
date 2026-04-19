"""
Sistema de historial de descargas
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class HistorialDescargas:
    """Maneja el historial de descargas."""
    
    def __init__(self, archivo_historial: Path = None):
        """
        Inicializa el historial.
        
        Args:
            archivo_historial: Ruta del archivo JSON del historial
        """
        if archivo_historial is None:
            from .config import PROJECT_ROOT
            archivo_historial = PROJECT_ROOT / "historial.json"
        
        self.archivo_historial = archivo_historial
        self._crear_archivo_si_no_existe()
    
    def _crear_archivo_si_no_existe(self):
        """Crea el archivo de historial si no existe."""
        if not self.archivo_historial.exists():
            self._guardar([])
    
    def _cargar(self) -> List[Dict[str, Any]]:
        """Carga el historial desde el archivo."""
        try:
            with open(self.archivo_historial, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _guardar(self, historial: List[Dict[str, Any]]):
        """Guarda el historial en el archivo."""
        try:
            with open(self.archivo_historial, 'w', encoding='utf-8') as f:
                json.dump(historial, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar historial: {e}")
    
    def agregar(self, url: str, titulo: str, ruta_archivo: str, 
                plataforma: str, tipo: str):
        """
        Agrega una descarga al historial.
        
        Args:
            url: URL del video
            titulo: Título del video
            ruta_archivo: Ruta donde se guardó
            plataforma: Plataforma de origen
            tipo: 'video' o 'audio'
        """
        historial = self._cargar()
        
        entrada = {
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'url': url,
            'titulo': titulo,
            'archivo': ruta_archivo,
            'plataforma': plataforma,
            'tipo': tipo
        }
        
        historial.insert(0, entrada)  # Agregar al inicio
        
        # Mantener solo las últimas 100 descargas
        if len(historial) > 100:
            historial = historial[:100]
        
        self._guardar(historial)
    
    def obtener_historial(self, limite: int = None) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de descargas.
        
        Args:
            limite: Número máximo de entradas a retornar
            
        Returns:
            Lista de descargas
        """
        historial = self._cargar()
        if limite:
            return historial[:limite]
        return historial
    
    def limpiar(self):
        """Limpia todo el historial."""
        self._guardar([])
    
    def eliminar_entrada(self, indice: int):
        """
        Elimina una entrada del historial.
        
        Args:
            indice: Índice de la entrada a eliminar
        """
        historial = self._cargar()
        if 0 <= indice < len(historial):
            historial.pop(indice)
            self._guardar(historial)
