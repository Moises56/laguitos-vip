# 🎥 Descargador Universal de Videos

Aplicación de escritorio para descargar videos y audio de múltiples plataformas.

## 🌟 Características

- ✅ Descarga videos de YouTube, TikTok, Instagram, Facebook, OK.ru y más
- 🎧 Opción para descargar solo audio (MP3)
- 📊 Barra de progreso en tiempo real
- 🎨 Interfaz gráfica amigable con Tkinter
- 🔒 Manejo robusto de errores

## 📦 Instalación

1. Clona este repositorio
2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:

```bash
python main.py
```

## ⚠️ Requisitos

- Python 3.8 o superior
- FFmpeg (opcional, pero recomendado)
  - **Sin FFmpeg**: Videos funcionan (calidad limitada)
  - **Con FFmpeg**: Videos en mejor calidad + Audio MP3
  - [Guía rápida de instalación](FFMPEG_RAPIDO.md)

## 📝 Uso

1. Pega la URL del video
2. Selecciona si quieres video o solo audio
3. Haz clic en Descargar
4. Los archivos se guardarán en la carpeta `downloads/`

## 🛠️ Tecnologías

- Python
- Tkinter (GUI)
- yt-dlp (descarga)
- FFmpeg (conversión)

## 📄 Licencia

MIT License
