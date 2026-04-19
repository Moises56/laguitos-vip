# 📦 Guía de Distribución - Descargador de Videos PORTABLE

## ✅ Cómo compartir este programa

### Opción 1: Compresión ZIP (Recomendado)

```powershell
# En PowerShell (carpeta pyProyectVideos):
Compress-Archive -Path "dist\DescargadorVideos\*" -DestinationPath "DescargadorVideos_Portable_v1.0.zip"
```

**Resultado**: Un archivo ZIP de ~250-300 MB (comprimido desde 403 MB)

**Instrucciones para el usuario final**:

1. Descargar el archivo ZIP
2. **Extraer todo** en una carpeta (click derecho → "Extraer todo")
3. Ejecutar `DescargadorVideos.exe`

---

### Opción 2: Carpeta compartida

Compartir la carpeta completa `dist\DescargadorVideos` (403 MB) por:

- USB / Disco externo
- Red local compartida
- OneDrive / Google Drive / Dropbox
- WeTransfer (archivos grandes)

---

## 📊 Información de la distribución

| Componente      | Tamaño     | Descripción                |
| --------------- | ---------- | -------------------------- |
| FFmpeg          | 370 MB     | Conversión de video/audio  |
| Python + yt-dlp | 25 MB      | Descargador y dependencias |
| Ejecutable      | 1.2 MB     | Programa principal         |
| Otros           | 7.5 MB     | Librerías adicionales      |
| **TOTAL**       | **403 MB** | Distribución completa      |

---

## 🚀 Ventajas de esta versión

✅ **Totalmente portable**: No requiere instalación  
✅ **Sin dependencias**: Usuario no necesita instalar Python, FFmpeg, etc.  
✅ **Plug & Play**: Descomprimir y ejecutar  
✅ **Sin permisos de administrador**: No modifica el sistema  
✅ **Multi-usuario**: Funciona en cualquier cuenta de Windows

---

## ⚙️ Requisitos del sistema (usuario final)

- **Sistema operativo**: Windows 10/11 (64 bits)
- **RAM**: Mínimo 2 GB (recomendado 4 GB)
- **Espacio en disco**: 500 MB libres (403 MB programa + descargas)
- **Internet**: Conexión activa para descargar videos

---

## 🔐 Consideraciones de seguridad

### Windows Defender / Antivirus

⚠️ **Posibles advertencias**:

- Ejecutables generados con PyInstaller pueden ser marcados como "sospechosos"
- Esto es un **falso positivo común**
- No es un virus, es el método de empaquetado

**Solución para el usuario**:

1. Click derecho en `DescargadorVideos.exe`
2. "Propiedades" → "Desbloquear" → "Aplicar"
3. O agregar excepción en el antivirus

### Firma digital (Opcional - Avanzado)

Para evitar advertencias de Windows SmartScreen:

- Obtener certificado de firma de código ($100-300/año)
- Firmar el ejecutable con `signtool.exe`
- Esto evita advertencias pero no es necesario

---

## 📝 Checklist de distribución

Antes de compartir, verificar:

- [ ] El programa inicia correctamente
- [ ] FFmpeg está incluido (verificar carpeta `_internal/ffmpeg_bundle/`)
- [ ] Funciona en una computadora **sin** Python instalado
- [ ] Funciona en una computadora **sin** FFmpeg instalado
- [ ] Incluir archivo `README.md` con instrucciones
- [ ] Probar en Windows 10 y Windows 11 si es posible

---

## 🧪 Prueba en computadora limpia

**Para verificar que es verdaderamente portable**:

1. Copiar carpeta `DescargadorVideos` a otra PC
2. PC debe estar **sin Python** instalado
3. PC debe estar **sin FFmpeg** instalado
4. Ejecutar `DescargadorVideos.exe`
5. Intentar descargar un video de prueba
6. ✅ Si funciona: Todo OK, listo para distribuir

---

## 📦 Plataformas de distribución sugeridas

### Archivos grandes (403 MB / 250 MB comprimido):

- **WeTransfer**: Gratis hasta 2 GB, válido 7 días
- **Google Drive**: Compartir carpeta con link
- **Dropbox**: Link público de descarga
- **OneDrive**: Compartir con link
- **MEGA**: 20 GB gratis

### Distribución profesional:

- **GitHub Releases**: Gratis, ilimitado, con versionado
- **SourceForge**: Para proyectos open source
- **Sitio web propio**: Si tienes hosting

---

## 🔄 Actualizaciones futuras

Para distribuir actualizaciones:

1. Modificar código fuente
2. Reconstruir ejecutable: `.\.venv\Scripts\pyinstaller.exe DescargadorVideos.spec --clean`
3. Probar nueva versión
4. Comprimir nueva carpeta `dist\DescargadorVideos`
5. Distribuir con nuevo número de versión (v1.1, v1.2, etc.)

**Archivo de cambios sugerido**: `CHANGELOG.md`

---

## 💾 Respaldo del código fuente

**IMPORTANTE**: Guardar el código fuente en:

- Repositorio Git (GitHub/GitLab)
- Backup en la nube
- Disco externo

La carpeta `dist` se puede regenerar, pero el código fuente es irreemplazable.

---

## 📄 Estructura recomendada para entrega

```
DescargadorVideos_Portable_v1.0.zip
└── Extraer en carpeta:
    ├── DescargadorVideos.exe        ← Ejecutar
    ├── README.md                    ← Instrucciones
    ├── _internal/                   ← No modificar
    │   ├── ffmpeg_bundle/
    │   │   ├── ffmpeg.exe
    │   │   └── ffprobe.exe
    │   └── [otras dependencias]
    └── (descargas/ se creará automáticamente)
```

---

## ✅ Conclusión

**Tu programa ahora es:**

- ✅ Completamente portable
- ✅ No requiere instalaciones
- ✅ Incluye FFmpeg (370 MB)
- ✅ Listo para compartir
- ✅ Usuario final: solo descomprimir y ejecutar

**Tamaño final**: 403 MB (sin comprimir) / ~250-300 MB (ZIP)

---

**Desarrollado con**: Python 3.12.2 + yt-dlp + FFmpeg 8.0 + PyInstaller 6.16.0  
**Fecha**: 2025
