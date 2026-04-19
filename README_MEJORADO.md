# 🎥 Descargador Universal de Videos

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Status](https://img.shields.io/badge/Status-Stable-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

Aplicación de escritorio **profesional** y **fácil de usar** para descargar videos y audio desde más de **1000+ plataformas**.

---

## ✨ Captura de Pantalla

_(Aplicación en funcionamiento - interfaz limpia y moderna)_

---

## 🚀 Inicio Rápido (3 pasos)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar aplicación
python main.py

# 3. ¡Pega una URL y descarga!
```

**Windows**: También puedes hacer doble clic en `iniciar.bat`

---

## ✨ Características

### 🎬 Descarga Inteligente

- ✅ **1000+ plataformas**: YouTube, TikTok, Instagram, Facebook y más
- ✅ **Múltiples calidades**: Mejor, 1080p, 720p, 480p
- ✅ **Audio MP3**: Convierte videos a audio de alta calidad
- ✅ **Detección automática**: Reconoce la plataforma al instante

### 🎨 Interfaz Amigable

- ✅ **Fácil de usar**: Solo pega la URL y descarga
- ✅ **Progreso en vivo**: Barra de progreso y estadísticas
- ✅ **Selector de carpeta**: Elige dónde guardar
- ✅ **Un clic**: Abre la carpeta de descargas directamente

### ⚡ Rendimiento

- ✅ **Descarga rápida**: Velocidad máxima de tu conexión
- ✅ **No congela**: Threading para interfaz fluida
- ✅ **Logs detallados**: Registro completo de operaciones
- ✅ **Manejo de errores**: Mensajes claros y útiles

---

## 🌐 Plataformas Soportadas

| Categoría     | Plataformas                                                                    |
| ------------- | ------------------------------------------------------------------------------ |
| **Video**     | YouTube, Vimeo, Dailymotion                                                    |
| **Social**    | TikTok, Instagram, Facebook, Twitter/X                                         |
| **Streaming** | Twitch, OK.ru                                                                  |
| **Más**       | [1000+ sitios](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) |

---

## 📦 Instalación

### Requisitos

- Python 3.8+
- pip
- FFmpeg (solo para audio) → [Guía de instalación](INSTALAR_FFMPEG.md)

### Pasos

```bash
# Clonar repositorio
git clone <url>
cd pyProyectVideos

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

---

## 📖 Documentación

| Documento                                  | Descripción                 |
| ------------------------------------------ | --------------------------- |
| [GUIA_USO.md](GUIA_USO.md)                 | Guía completa de usuario    |
| [INSTALAR_FFMPEG.md](INSTALAR_FFMPEG.md)   | Instalar FFmpeg paso a paso |
| [RESUMEN_PROYECTO.md](RESUMEN_PROYECTO.md) | Documentación técnica       |
| [CHANGELOG.md](CHANGELOG.md)               | Historial de versiones      |

---

## 🎯 Uso

1. **Ejecuta**: `python main.py`
2. **Pega** la URL del video
3. **Selecciona** video o audio
4. **Descarga** y listo! 🎉

---

## 🛠️ Stack Tecnológico

- **Python 3.8+** - Lenguaje base
- **Tkinter** - Interfaz gráfica
- **yt-dlp** - Motor de descarga
- **FFmpeg** - Conversión de audio

---

## 🧪 Testing

```bash
python test_proyecto.py
```

Verifica:

- ✅ Estructura del proyecto
- ✅ Importaciones
- ✅ Validación de URLs
- ✅ FFmpeg

---

## 🗺️ Roadmap

- [x] **v1.0**: Versión base funcional ✅
- [ ] **v1.1**: Cola de descargas, tema oscuro
- [ ] **v1.2**: Historial, más formatos
- [ ] **v2.0**: Versión web con API REST

Ver completo: [CHANGELOG.md](CHANGELOG.md)

---

## 🐛 Problemas Comunes

| Problema             | Solución                                 |
| -------------------- | ---------------------------------------- |
| FFmpeg no encontrado | [Ver guía](INSTALAR_FFMPEG.md)           |
| URL no válida        | Verifica que sea de plataforma soportada |
| Error de descarga    | Revisa logs en `logs/`                   |

---

## ⚠️ Uso Responsable

Esta herramienta es para uso personal y educativo. Respeta los derechos de autor y términos de servicio de las plataformas.

---

## 📄 Licencia

MIT License - Libre para usar y modificar

---

<div align="center">

**¿Te gusta el proyecto? ¡Dale una ⭐!**

Versión 1.0.0 | 2025-10-30

</div>
