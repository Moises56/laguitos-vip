# 📖 Guía de Uso - Descargador Universal de Videos

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt
```

### 2. Ejecutar la aplicación

```bash
python main.py
```

## 🎯 Cómo usar

### Descargar un video

1. **Copia la URL** del video que quieres descargar (YouTube, TikTok, Instagram, etc.)
2. **Pégala** en el campo "URL del video"
3. La aplicación detectará automáticamente la plataforma
4. **Selecciona las opciones**:
   - 🎧 Marca "Descargar solo audio (MP3)" si solo quieres el audio
   - 📺 Selecciona la calidad de video (mejor, 1080p, 720p, 480p)
5. **Haz clic en "⬇️ Descargar"**
6. Espera a que termine (verás el progreso en la barra)
7. El archivo se guardará en la carpeta `downloads/`

### Cambiar carpeta de destino

1. Haz clic en el botón **"Cambiar"** junto a "📁 Guardar en:"
2. Selecciona la carpeta donde quieres guardar tus descargas
3. A partir de ahí, todos los archivos se guardarán en esa carpeta

### Abrir carpeta de descargas

- Haz clic en la **ruta azul** de la carpeta (donde dice la ubicación)
- Se abrirá el explorador de archivos en esa ubicación

## 🌐 Plataformas Soportadas

✅ **YouTube** (youtube.com, youtu.be)  
✅ **TikTok** (tiktok.com)  
✅ **Instagram** (instagram.com)  
✅ **Facebook** (facebook.com, fb.watch)  
✅ **OK.ru** (ok.ru)  
✅ **Twitter/X** (twitter.com, x.com)  
✅ **Vimeo** (vimeo.com)  
✅ **Dailymotion** (dailymotion.com)  
✅ **Twitch** (twitch.tv)  
✅ Y muchas más...

## 🎬 Opciones de Descarga

### Video

- **Mejor**: Descarga la mejor calidad disponible
- **1080p**: Full HD (si está disponible)
- **720p**: HD
- **480p**: Calidad estándar

### Audio

- **Formato**: MP3
- **Calidad**: 192 kbps (alta calidad)

## ⚠️ Requisitos Importantes

### FFmpeg (para audio)

Si quieres descargar audio (MP3), necesitas tener **FFmpeg** instalado:

#### Windows:

1. Descarga FFmpeg desde: https://ffmpeg.org/download.html
2. Extrae el archivo ZIP
3. Agrega la carpeta `bin` al PATH del sistema

#### Verificar instalación:

```bash
ffmpeg -version
```

Si ves la versión de FFmpeg, está correctamente instalado.

## 🐛 Solución de Problemas

### Error: "FFmpeg no encontrado"

- Instala FFmpeg siguiendo las instrucciones de arriba
- Reinicia la aplicación después de instalar

### Error: "URL no válida"

- Verifica que la URL esté completa
- Asegúrate de que sea de una plataforma soportada
- Intenta copiar la URL directamente desde la barra del navegador

### Error durante la descarga

- Verifica tu conexión a internet
- Algunos videos pueden tener restricciones de región o privacidad
- Videos privados o eliminados no se pueden descargar

### La descarga es muy lenta

- Depende de tu conexión a internet
- Videos en alta calidad (1080p+) son archivos grandes
- La velocidad también depende del servidor de la plataforma

## 📝 Notas Adicionales

- Los videos descargados se guardan con el título original del video
- Si descargas audio de un video, solo se guardará el archivo .mp3
- La aplicación crea una carpeta `logs/` con información de las descargas
- Puedes descargar múltiples videos, pero uno a la vez

## 🔒 Uso Responsable

⚠️ **Importante**:

- Respeta los derechos de autor
- Solo descarga contenido que tengas permiso de descargar
- No redistribuyas contenido sin autorización
- Algunos términos de servicio de plataformas prohíben la descarga

## 📊 Estructura del Proyecto

```
pyProyectVideos/
│
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias
├── README.md              # Documentación
│
├── downloader/            # Módulo de descarga
│   ├── __init__.py
│   ├── config.py         # Configuración
│   ├── core.py           # Lógica principal
│   └── utils.py          # Utilidades
│
├── gui/                   # Interfaz gráfica
│   ├── __init__.py
│   └── app.py            # Aplicación Tkinter
│
├── downloads/            # Descargas (creada automáticamente)
└── logs/                 # Logs (creada automáticamente)
```

## 🆘 Soporte

Si encuentras algún problema o tienes sugerencias:

1. Revisa esta guía primero
2. Verifica los logs en la carpeta `logs/`
3. Asegúrate de tener la última versión de yt-dlp: `pip install --upgrade yt-dlp`

---

¡Disfruta descargando tus videos favoritos! 🎉
