# 🚀 Instalación Rápida de FFmpeg en Windows

## ⚡ Opción 1: Winget (Más Fácil - Windows 10/11)

Abre PowerShell y ejecuta:

```powershell
winget install FFmpeg
```

Luego reinicia la aplicación.

---

## 📦 Opción 2: Descarga Manual (5 minutos)

### Paso 1: Descargar

1. Ve a: https://github.com/BtbN/FFmpeg-Builds/releases
2. Busca el archivo: `ffmpeg-master-latest-win64-gpl.zip`
3. Descárgalo

### Paso 2: Extraer

1. Extrae el ZIP
2. Mueve la carpeta a `C:\ffmpeg`
3. Verifica que exista: `C:\ffmpeg\bin\ffmpeg.exe`

### Paso 3: Agregar al PATH

**Método Visual:**

1. Presiona `Win + X` → "Sistema"
2. Click en "Configuración avanzada del sistema"
3. Click en "Variables de entorno"
4. En "Variables del sistema", selecciona "Path"
5. Click "Editar" → "Nuevo"
6. Agrega: `C:\ffmpeg\bin`
7. Click "Aceptar" en todo

**Método PowerShell (como Admin):**

```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ffmpeg\bin", "Machine")
```

### Paso 4: Verificar

Abre una **nueva** PowerShell y ejecuta:

```powershell
ffmpeg -version
```

Si ves la versión, ¡funciona! ✅

---

## ✅ Después de Instalar

1. **Cierra completamente** la aplicación
2. **Abre nueva terminal**
3. Ejecuta de nuevo: `python main.py`
4. Ahora podrás descargar audio en MP3 🎵

---

## 🆘 Problemas

### No funciona después de instalar

**Solución**:

- Cierra TODO (terminales, VSCode, aplicación)
- En casos extremos, reinicia Windows
- Las variables PATH se cargan al inicio de las aplicaciones

### No tengo permisos para cambiar PATH

**Solución**:

- Haz clic derecho en PowerShell
- "Ejecutar como administrador"
- Intenta de nuevo

---

**Para más detalles**: Ver [INSTALAR_FFMPEG.md](INSTALAR_FFMPEG.md)
