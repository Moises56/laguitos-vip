"""
Interfaz gráfica de usuario (GUI) usando Tkinter
"""
import os
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Optional

import sys
sys.path.append(str(Path(__file__).parent.parent))

from downloader.core import VideoDownloader
from downloader.config import GUI_CONFIG, DOWNLOADS_FOLDER
from downloader.utils import extraer_info_plataforma

logger = logging.getLogger(__name__)


class VideoDownloaderApp:
    """
    Aplicación GUI para descargar videos.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Inicializa la aplicación GUI.
        
        Args:
            root: Ventana principal de Tkinter
        """
        self.root = root
        self.downloader = VideoDownloader()
        self.carpeta_destino = DOWNLOADS_FOLDER
        self.descarga_en_proceso = False
        
        # Variables de control para la barra de progreso
        self.progreso_var = tk.DoubleVar(value=0.0)
        self.estado_var = tk.StringVar(value="")
        
        # Control de throttling para la barra de progreso
        self.ultimo_update_progreso = 0
        self.min_intervalo_update = 0.1  # Actualizar máximo cada 100ms
        
        # Verificar FFmpeg al inicio
        from downloader.utils import verificar_ffmpeg
        self.ffmpeg_disponible, _ = verificar_ffmpeg()
        
        # Configurar ventana
        self._configurar_ventana()
        
        # Crear widgets
        self._crear_widgets()
        
        # Mostrar aviso de FFmpeg si no está disponible
        if not self.ffmpeg_disponible:
            self._mostrar_aviso_ffmpeg()
        
    def _configurar_ventana(self):
        """Configura la ventana principal."""
        self.root.title(GUI_CONFIG['window_title'])
        self.root.geometry(GUI_CONFIG['window_size'])
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _crear_widgets(self):
        """Crea todos los widgets de la interfaz."""
        
        # ===== TÍTULO =====
        titulo = tk.Label(
            self.root,
            text="Descargador de Videos Universal",
            font=(GUI_CONFIG['font_family'], 16, "bold")
        )
        titulo.pack(pady=15)
        
        # ===== FRAME URL =====
        frame_url = tk.Frame(self.root)
        frame_url.pack(pady=10, padx=20, fill='x')
        
        tk.Label(
            frame_url,
            text="🔗 URL del video:",
            font=(GUI_CONFIG['font_family'], 11)
        ).pack(anchor='w')
        
        self.url_entry = tk.Entry(frame_url, width=60, font=(GUI_CONFIG['font_family'], 10))
        self.url_entry.pack(fill='x', pady=5)
        self.url_entry.bind('<KeyRelease>', self._on_url_change)
        
        # Label para mostrar plataforma detectada
        self.platform_label = tk.Label(
            frame_url,
            text="",
            font=(GUI_CONFIG['font_family'], 9),
            fg="gray"
        )
        self.platform_label.pack(anchor='w')
        
        # ===== OPCIONES =====
        frame_opciones = tk.Frame(self.root)
        frame_opciones.pack(pady=10, padx=20, fill='x')
        
        # Opción de solo audio
        self.solo_audio_var = tk.BooleanVar()
        audio_text = "🎧 Descargar solo audio (MP3)"
        if not self.ffmpeg_disponible:
            audio_text += " (Requiere FFmpeg)"
        
        self.check_audio = tk.Checkbutton(
            frame_opciones,
            text=audio_text,
            variable=self.solo_audio_var,
            font=(GUI_CONFIG['font_family'], 10),
            command=self._toggle_calidad,
            state='disabled' if not self.ffmpeg_disponible else 'normal'
        )
        self.check_audio.pack(anchor='w', pady=5)
        
        # Selector de calidad (solo para video)
        calidad_frame = tk.Frame(frame_opciones)
        calidad_frame.pack(anchor='w', pady=5)
        
        tk.Label(
            calidad_frame,
            text="📺 Calidad:",
            font=(GUI_CONFIG['font_family'], 10)
        ).pack(side='left', padx=(0, 10))
        
        self.calidad_var = tk.StringVar(value='mejor')
        self.calidad_combo = ttk.Combobox(
            calidad_frame,
            textvariable=self.calidad_var,
            values=['mejor', '1080p', '720p', '480p'],
            state='readonly',
            width=15,
            font=(GUI_CONFIG['font_family'], 9)
        )
        self.calidad_combo.pack(side='left')
        
        # ===== CARPETA DESTINO =====
        frame_carpeta = tk.Frame(self.root)
        frame_carpeta.pack(pady=10, padx=20, fill='x')
        
        tk.Label(
            frame_carpeta,
            text="📁 Guardar en:",
            font=(GUI_CONFIG['font_family'], 10)
        ).pack(side='left', padx=(0, 10))
        
        # Botón "Cambiar" primero para que siempre sea visible
        btn_cambiar_carpeta = tk.Button(
            frame_carpeta,
            text="📂 Cambiar",
            command=self._seleccionar_carpeta,
            font=(GUI_CONFIG['font_family'], 9),
            bg="#FF9800",
            fg="white",
            padx=10,
            cursor="hand2"
        )
        btn_cambiar_carpeta.pack(side='right', padx=(10, 0))
        
        self.carpeta_label = tk.Label(
            frame_carpeta,
            text=str(self.carpeta_destino),
            font=(GUI_CONFIG['font_family'], 9),
            fg="blue",
            cursor="hand2",
            anchor='w'
        )
        self.carpeta_label.pack(side='left', fill='x', expand=True)
        self.carpeta_label.bind('<Button-1>', lambda e: self._abrir_carpeta())
        
        # ===== FRAME DE BOTONES PRINCIPALES =====
        frame_botones = tk.Frame(self.root)
        frame_botones.pack(pady=10)
        
        # Botón Descargar
        self.btn_descargar = tk.Button(
            frame_botones,
            text="⬇️ Descargar",
            font=(GUI_CONFIG['font_family'], 12, "bold"),
            bg=GUI_CONFIG['theme_color'],
            fg="white",
            width=18,
            height=2,
            command=self._iniciar_descarga,
            cursor="hand2"
        )
        self.btn_descargar.pack(side='left', padx=5)
        
        # Botón Historial
        self.btn_historial = tk.Button(
            frame_botones,
            text="📋 Historial",
            font=(GUI_CONFIG['font_family'], 12, "bold"),
            bg="#2196F3",
            fg="white",
            width=18,
            height=2,
            command=self._mostrar_historial,
            cursor="hand2"
        )
        self.btn_historial.pack(side='left', padx=5)
        
        # ===== FRAME DE BOTONES DE CONTROL =====
        frame_control = tk.Frame(self.root)
        frame_control.pack(pady=8)
        
        # Botón Pausar/Reanudar
        self.btn_pausar = tk.Button(
            frame_control,
            text="⏸️ Pausar",
            font=(GUI_CONFIG['font_family'], 10, "bold"),
            bg="#FF9800",
            fg="white",
            width=15,
            height=1,
            command=self._pausar_reanudar,
            cursor="hand2",
            state='disabled'
        )
        self.btn_pausar.pack(side='left', padx=5)
        
        # Botón Cancelar
        self.btn_cancelar = tk.Button(
            frame_control,
            text="🚫 Cancelar",
            font=(GUI_CONFIG['font_family'], 10, "bold"),
            bg="#F44336",
            fg="white",
            width=15,
            height=1,
            command=self._cancelar_descarga,
            cursor="hand2",
            state='disabled'
        )
        self.btn_cancelar.pack(side='left', padx=5)
        
        # ===== BARRA DE PROGRESO =====
        self.progress_bar = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=500,
            mode="determinate",
            maximum=100,
            variable=self.progreso_var  # Usar variable de control
        )
        self.progress_bar.pack(pady=12)
        
        # ===== LABEL DE PORCENTAJE (Grande y visible) =====
        self.porcentaje_label = tk.Label(
            self.root,
            text="",
            font=(GUI_CONFIG['font_family'], 16, "bold"),
            fg=GUI_CONFIG['theme_color']
        )
        self.porcentaje_label.pack(pady=3)
        
        # ===== LABEL DE ESTADO (velocidad y ETA) =====
        self.status_label = tk.Label(
            self.root,
            textvariable=self.estado_var,  # Usar variable de control
            font=(GUI_CONFIG['font_family'], 10),
            fg="gray"
        )
        self.status_label.pack(pady=3)
        
        # ===== FOOTER =====
        footer_text = "Compatible con YouTube, TikTok, Instagram, Facebook, OK.ru y más"
        if not self.ffmpeg_disponible:
            footer_text += "\n⚠️ FFmpeg no detectado - Descargas de audio deshabilitadas"
        
        footer = tk.Label(
            self.root,
            text=footer_text,
            font=(GUI_CONFIG['font_family'], 8),
            fg="gray"
        )
        footer.pack(side="bottom", pady=10)
    
    def _on_url_change(self, event):
        """Detecta la plataforma cuando se escribe una URL."""
        url = self.url_entry.get().strip()
        if url:
            plataforma = extraer_info_plataforma(url)
            if plataforma:
                self.platform_label.config(text=f"📱 Plataforma detectada: {plataforma}")
            else:
                self.platform_label.config(text="")
        else:
            self.platform_label.config(text="")
    
    def _toggle_calidad(self):
        """Habilita/deshabilita el selector de calidad según audio."""
        if self.solo_audio_var.get():
            self.calidad_combo.config(state='disabled')
        else:
            self.calidad_combo.config(state='readonly')
    
    def _seleccionar_carpeta(self):
        """Permite al usuario seleccionar una carpeta de destino."""
        carpeta = filedialog.askdirectory(
            title="Seleccionar carpeta de descargas",
            initialdir=str(self.carpeta_destino)
        )
        if carpeta:
            self.carpeta_destino = Path(carpeta)
            self.downloader = VideoDownloader(self.carpeta_destino)
            self.carpeta_label.config(text=str(self.carpeta_destino))
    
    def _abrir_carpeta(self):
        """Abre la carpeta de descargas en el explorador."""
        os.startfile(str(self.carpeta_destino))
    
    def _actualizar_progreso(self, d):
        """
        Callback para actualizar la barra de progreso.
        Thread-safe: usa root.after() para actualizar desde el hilo principal.
        Actualización más frecuente para mejor feedback visual.
        
        Args:
            d: Diccionario con información de progreso
        """
        if d['status'] == 'downloading':
            import time
            
            # Throttling reducido para mejor feedback (50ms en lugar de 100ms)
            tiempo_actual = time.time()
            if tiempo_actual - self.ultimo_update_progreso < 0.05:
                return  # Skip este update
            
            self.ultimo_update_progreso = tiempo_actual
            
            porcentaje = d.get('_percent_str', '0%').strip()
            velocidad = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            
            try:
                # Extraer el número del porcentaje
                progreso_num = float(porcentaje.replace('%', '').strip())
            except:
                progreso_num = 0
            
            # Actualizar variables de control (thread-safe)
            self.progreso_var.set(progreso_num)
            
            # Actualizar porcentaje grande y visible
            self.root.after(0, lambda: self.porcentaje_label.config(text=f"{porcentaje}"))
            
            # Actualizar estado con velocidad y ETA
            self.estado_var.set(f"⏬ Descargando: {velocidad} | Tiempo restante: {eta}")
                
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.porcentaje_label.config(text="100%"))
            self.estado_var.set("🔄 Procesando archivo...")
        
        elif d['status'] == 'processing':
            # Nuevo estado: Procesamiento con FFmpeg
            mensaje = d.get('message', 'Procesando...')
            self.root.after(0, lambda: self.porcentaje_label.config(text="100%"))
            self.estado_var.set(f"🔄 {mensaje}")
            logger.info(f"Processing: {mensaje}")
    
    def _pausar_reanudar(self):
        """Pausa o reanuda la descarga actual."""
        if self.downloader.pausar_descarga:
            # Reanudar
            self.downloader.reanudar()
            self.btn_pausar.config(text="⏸️ Pausar", bg="#FF9800")
            self.estado_var.set("▶️ Reanudando descarga...")
        else:
            # Pausar
            self.downloader.pausar()
            self.btn_pausar.config(text="▶️ Reanudar", bg="#4CAF50")
            self.estado_var.set("⏸️ Descarga en pausa")
    
    def _cancelar_descarga(self):
        """Cancela la descarga actual."""
        respuesta = messagebox.askyesno(
            "Cancelar descarga",
            "¿Estás seguro de que deseas cancelar la descarga?"
        )
        if respuesta:
            self.downloader.cancelar()
            self.estado_var.set("🚫 Cancelando...")
    
    def _iniciar_descarga(self):
        """Inicia el proceso de descarga en un hilo separado."""
        if self.descarga_en_proceso:
            messagebox.showwarning(
                "Descarga en proceso",
                "Ya hay una descarga en proceso. Por favor espera."
            )
            return
        
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning(
                "URL vacía",
                "Por favor, ingresa una URL válida."
            )
            return
        
        # Configurar estado
        self.descarga_en_proceso = True
        self.btn_descargar.config(state='disabled', bg='gray')
        self.btn_pausar.config(state='normal')
        self.btn_cancelar.config(state='normal')
        self.progreso_var.set(0.0)
        self.porcentaje_label.config(text="0%")  # Mostrar 0% al inicio
        self.estado_var.set("🎬 Iniciando descarga...")
        
        # Resetear throttling para nueva descarga
        self.ultimo_update_progreso = 0
        
        # Configurar callback de progreso
        self.downloader.set_progreso_callback(self._actualizar_progreso)
        
        # Obtener opciones
        solo_audio = self.solo_audio_var.get()
        calidad = self.calidad_var.get()
        
        # Iniciar descarga en hilo separado
        hilo = threading.Thread(
            target=self._ejecutar_descarga,
            args=(url, solo_audio, calidad),
            daemon=True
        )
        hilo.start()
    
    def _ejecutar_descarga(self, url: str, solo_audio: bool, calidad: str):
        """
        Ejecuta la descarga en un hilo separado.
        
        Args:
            url: URL del video
            solo_audio: Si es True, solo descarga audio
            calidad: Calidad del video
        """
        try:
            resultado = self.downloader.descargar(url, solo_audio, calidad)
            
            # Actualizar UI en el hilo principal
            self.root.after(0, self._descarga_completada, resultado)
            
        except Exception as e:
            self.root.after(0, self._descarga_error, str(e))
    
    def _descarga_completada(self, resultado):
        """
        Maneja la finalización de la descarga.
        
        Args:
            resultado: Diccionario con resultado de la descarga
        """
        self.descarga_en_proceso = False
        self.btn_descargar.config(state='normal', bg='#4CAF50')
        self.btn_pausar.config(state='disabled', text="⏸️ Pausar", bg="#FF9800")
        self.btn_cancelar.config(state='disabled')
        self.progreso_var.set(0.0)
        self.porcentaje_label.config(text="")  # Limpiar porcentaje
        
        if resultado['success']:
            self.estado_var.set("✅ Descarga completada")
            
            # Limpiar URL
            self.url_entry.delete(0, tk.END)
            self.platform_label.config(text="")
            
            # Mostrar mensaje de éxito
            messagebox.showinfo(
                "Descarga exitosa",
                f"{resultado['message']}\n\nArchivo: {Path(resultado['file_path']).name}"
            )
        else:
            self.estado_var.set("❌ Error en la descarga")
            messagebox.showerror(
                "Error",
                resultado['message']
            )
    
    def _descarga_error(self, error_msg: str):
        """
        Maneja errores durante la descarga.
        
        Args:
            error_msg: Mensaje de error
        """
        self.descarga_en_proceso = False
        self.btn_descargar.config(state='normal', bg=GUI_CONFIG['theme_color'])
        self.btn_pausar.config(state='disabled', text="⏸️ Pausar", bg="#FF9800")
        self.btn_cancelar.config(state='disabled')
        self.progreso_var.set(0.0)
        self.porcentaje_label.config(text="")  # Limpiar porcentaje
        
        # Si fue cancelación por el usuario, mostrar mensaje diferente
        if "cancelada por el usuario" in error_msg.lower():
            self.estado_var.set("🚫 Descarga cancelada")
            messagebox.showinfo("Cancelado", "La descarga fue cancelada.")
        else:
            self.estado_var.set("❌ Error")
            messagebox.showerror("Error", f"Ocurrió un error:\n{error_msg}")
    
    def _mostrar_aviso_ffmpeg(self):
        """Muestra un aviso si FFmpeg no está instalado."""
        mensaje = (
            "⚠️ FFmpeg no está instalado\n\n"
            "Sin FFmpeg:\n"
            "• ✅ Videos: Funcionará (calidad limitada)\n"
            "• ❌ Audio: No disponible\n\n"
            "Para descargar audio y videos en mejor calidad,\n"
            "instala FFmpeg siguiendo la guía:\n"
            "INSTALAR_FFMPEG.md"
        )
        messagebox.showwarning("FFmpeg no detectado", mensaje)
    
    def _mostrar_historial(self):
        """Muestra una ventana con el historial de descargas."""
        from downloader.historial import HistorialDescargas
        
        # Crear ventana de historial
        ventana_historial = tk.Toplevel(self.root)
        ventana_historial.title("📋 Historial de Descargas")
        ventana_historial.geometry("800x500")
        ventana_historial.resizable(True, True)
        
        # Título
        titulo = tk.Label(
            ventana_historial,
            text="Historial de Descargas",
            font=(GUI_CONFIG['font_family'], 14, "bold")
        )
        titulo.pack(pady=10)
        
        # Frame con scrollbar
        frame_container = tk.Frame(ventana_historial)
        frame_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(frame_container)
        scrollbar.pack(side='right', fill='y')
        
        # Lista de descargas
        lista = tk.Listbox(
            frame_container,
            yscrollcommand=scrollbar.set,
            font=(GUI_CONFIG['font_family'], 9),
            selectmode=tk.SINGLE
        )
        lista.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=lista.yview)
        
        # Cargar historial
        historial_obj = HistorialDescargas()
        descargas = historial_obj.obtener_historial()
        
        if not descargas:
            lista.insert(0, "📭 No hay descargas en el historial")
        else:
            for descarga in descargas:
                # Compatibilidad con historial antiguo sin campo 'type'
                tipo_emoji = "🎵" if descarga.get('type') == 'audio' else "🎬"
                texto = (
                    f"{tipo_emoji} {descarga['fecha']} | "
                    f"{descarga['plataforma']} | "
                    f"{descarga['titulo'][:50]}..."
                )
                lista.insert(tk.END, texto)
        
        # Frame de botones
        frame_botones = tk.Frame(ventana_historial)
        frame_botones.pack(pady=10)
        
        def abrir_ubicacion():
            """Abre la ubicación del archivo seleccionado."""
            seleccion = lista.curselection()
            if seleccion and descargas:
                indice = seleccion[0]
                archivo = descargas[indice]['archivo']
                if Path(archivo).exists():
                    # Abrir carpeta contenedora
                    os.startfile(str(Path(archivo).parent))
                else:
                    messagebox.showwarning(
                        "Archivo no encontrado",
                        f"El archivo ya no existe:\n{archivo}"
                    )
        
        def copiar_ruta():
            """Copia la ruta del archivo al portapapeles."""
            seleccion = lista.curselection()
            if seleccion and descargas:
                indice = seleccion[0]
                archivo = descargas[indice]['archivo']
                self.root.clipboard_clear()
                self.root.clipboard_append(archivo)
                messagebox.showinfo("Copiado", "Ruta copiada al portapapeles")
        
        def limpiar_historial():
            """Limpia todo el historial."""
            respuesta = messagebox.askyesno(
                "Confirmar",
                "¿Estás seguro de que deseas limpiar todo el historial?"
            )
            if respuesta:
                historial_obj.limpiar()
                ventana_historial.destroy()
                messagebox.showinfo("Limpiado", "Historial limpiado correctamente")
        
        # Botones
        tk.Button(
            frame_botones,
            text="📂 Abrir Ubicación",
            command=abrir_ubicacion,
            font=(GUI_CONFIG['font_family'], 10)
        ).pack(side='left', padx=5)
        
        tk.Button(
            frame_botones,
            text="📋 Copiar Ruta",
            command=copiar_ruta,
            font=(GUI_CONFIG['font_family'], 10)
        ).pack(side='left', padx=5)
        
        tk.Button(
            frame_botones,
            text="🗑️ Limpiar Todo",
            command=limpiar_historial,
            font=(GUI_CONFIG['font_family'], 10),
            bg="#f44336",
            fg="white"
        ).pack(side='left', padx=5)
        
        tk.Button(
            frame_botones,
            text="Cerrar",
            command=ventana_historial.destroy,
            font=(GUI_CONFIG['font_family'], 10)
        ).pack(side='left', padx=5)
    
    def run(self):
        """Inicia el loop principal de la aplicación."""
        self.root.mainloop()


def iniciar_app():
    """Función para iniciar la aplicación."""
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    app.run()


if __name__ == "__main__":
    iniciar_app()
