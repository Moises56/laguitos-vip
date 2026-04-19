# 🎵 Guía de Instalación de FFmpeg

FFmpeg es necesario para poder descargar y convertir audio a formato MP3. Sin FFmpeg, solo podrás descargar videos.

---

## 🪟 Windows

### Método 1: Winget (Recomendado para Windows 10/11)

```bash
winget install FFmpeg
```

### Método 2: Descarga Manual

#### Paso 1: Descargar FFmpeg

1. Ve a: https://github.com/BtbN/FFmpeg-Builds/releases
2. Descarga el archivo: `ffmpeg-master-latest-win64-gpl.zip`

#### Paso 2: Extraer

1. Extrae el archivo ZIP en `C:\ffmpeg`
2. Deberías tener la carpeta: `C:\ffmpeg\bin\`

#### Paso 3: Agregar al PATH

1. Presiona `Win + X` y selecciona "Sistema"
2. Haz clic en "Configuración avanzada del sistema"
3. Haz clic en "Variables de entorno"
4. En "Variables del sistema", busca y selecciona "Path"
5. Haz clic en "Editar"
6. Haz clic en "Nuevo"
7. Agrega: `C:\ffmpeg\bin`
8. Haz clic en "Aceptar" en todas las ventanas

#### Paso 4: Verificar

Abre una nueva ventana de PowerShell o CMD y ejecuta:

```bash
ffmpeg -version
```

Si ves la información de la versión, ¡está instalado correctamente! ✅

---

## 🍎 macOS

### Usando Homebrew (Recomendado)

```bash
# Si no tienes Homebrew instalado:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar FFmpeg:
brew install ffmpeg
```

### Verificar:

```bash
ffmpeg -version
```

---

## 🐧 Linux

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

### Fedora

```bash
sudo dnf install ffmpeg
```

### Arch Linux

```bash
sudo pacman -S ffmpeg
```

### Verificar:

```bash
ffmpeg -version
```

---

## ✅ Verificación en la Aplicación

Una vez instalado FFmpeg:

1. **Cierra la aplicación** del descargador si está abierta
2. **Abre una nueva terminal** (para cargar las nuevas variables de entorno)
3. **Ejecuta la aplicación de nuevo**:
   ```bash
   python main.py
   ```
4. Intenta descargar un video en modo "solo audio"
5. Si funciona, FFmpeg está correctamente configurado ✅

---

## 🔧 Solución de Problemas

### Error: "FFmpeg no encontrado"

**Causa**: FFmpeg no está en el PATH del sistema.

**Solución**:

1. Verifica la instalación: `ffmpeg -version`
2. Si no funciona, revisa que agregaste correctamente la ruta al PATH
3. **Importante**: Cierra y abre nuevamente la terminal después de modificar el PATH
4. En Windows, a veces es necesario reiniciar el sistema

### Error: "El archivo no se puede convertir"

**Causa**: FFmpeg está instalado pero corrupto o incompleto.

**Solución**:

1. Desinstala FFmpeg
2. Descarga de nuevo desde el sitio oficial
3. Reinstala siguiendo los pasos de arriba

### Windows: No puedo modificar variables de entorno

**Solución**: Necesitas permisos de administrador.

1. Haz clic derecho en "Símbolo del sistema"
2. Selecciona "Ejecutar como administrador"
3. Intenta nuevamente

---

## 📝 Notas Importantes

- **Reiniciar aplicaciones**: Después de instalar FFmpeg, cierra todas las terminales y aplicaciones abiertas
- **Variables de entorno**: Los cambios en el PATH solo afectan a nuevas sesiones de terminal
- **Permisos**: En algunos sistemas puede requerir permisos de administrador

---

## 🆘 ¿Sigues teniendo problemas?

1. Verifica que el archivo `ffmpeg.exe` (Windows) o `ffmpeg` (Linux/Mac) existe
2. Asegúrate de que la ruta al binario esté en el PATH
3. Intenta ejecutar `where ffmpeg` (Windows) o `which ffmpeg` (Linux/Mac) para ver la ruta
4. Revisa los logs en la carpeta `logs/` de la aplicación

---

## 🔗 Enlaces Oficiales

- **FFmpeg Website**: https://ffmpeg.org/
- **FFmpeg Documentation**: https://ffmpeg.org/documentation.html
- **FFmpeg Windows Builds**: https://github.com/BtbN/FFmpeg-Builds/releases
- **Homebrew (macOS)**: https://brew.sh/

---

¡Una vez instalado FFmpeg, podrás disfrutar de todas las funcionalidades de la aplicación! 🎉
