# Laguitos Docker — Setup

Guía de arranque con Docker Desktop en Windows (dev local).
Para el despliegue en Azure Ubuntu VPS (prod) ver Fase 4.

## Arquitectura (dev)

Un único container `laguitos-backend` que:
- Sirve la API FastAPI en `/api/*` y el WebSocket en `/ws/*`
- Sirve el frontend estático en `/` (via `StaticFiles` cuando `DEBUG=true`)
- Usa SQLite (`./data/laguitos.db`) persistido en volumen bind
- Usa FFmpeg del sistema (instalado en la imagen) para merge y reconversión

## Primera vez

1. Asegurate que Docker Desktop esté corriendo:
   ```powershell
   docker --version
   docker compose version
   docker ps
   ```

2. Ejecutá el script de inicialización:
   ```powershell
   .\scripts\docker\init.ps1
   ```
   Esto crea `cookies.txt` (placeholder vacío si no tenés uno real),
   `.env` (desde `docker/.env.example`) y los directorios `data/`, `logs/`.

3. Editá `.env` con valores reales:
   - `SECRET_KEY`: generar con
     ```powershell
     python -c "import secrets; print(secrets.token_urlsafe(64))"
     ```
   - `SEED_USER_1_PASSWORD` y `SEED_USER_2_PASSWORD`: passwords reales
     para los dos usuarios seed (Moisés y Estefany).

4. Primer build + up:
   ```powershell
   docker compose up -d --build
   ```

5. Verificá que está corriendo:
   ```powershell
   docker compose logs -f backend
   curl http://localhost:8000/api/health
   ```
   Respuesta esperada:
   ```json
   {"status":"ok","app":"Laguitos Web","debug":true}
   ```

6. Abrí el frontend en el navegador:
   <http://localhost:8000/>

## Día a día

| Acción | Comando |
|---|---|
| Levantar | `docker compose up -d` |
| Ver logs | `docker compose logs -f backend` |
| Bajar | `docker compose down` |
| Rebuild tras cambios de deps | `docker compose up -d --build` |
| Entrar al shell | `docker compose exec backend bash` |
| Reiniciar solo el backend | `docker compose restart backend` |
| Inspeccionar BD SQLite | abrir `./data/laguitos.db` con DB Browser |

## Estructura de archivos Docker

```
.
├── docker-compose.yml            # dev, 1 service
├── .dockerignore                 # excluye .env, cookies.txt, build/, etc.
├── web/backend/
│   ├── Dockerfile                # multi-stage (builder + runtime)
│   └── requirements-docker.txt   # superset + yt-dlp, sin deps desktop
├── docker/
│   ├── .env.example              # template de variables de entorno
│   └── README.md                 # este archivo
└── scripts/docker/
    └── init.ps1                  # setup automático para Windows
```

## Cookies de YouTube (opcional)

Por defecto `init.ps1` crea un `cookies.txt` placeholder vacío. Con eso:
- TikTok, Instagram pública, Twitter/X y otros → funcionan sin cookies
- YouTube con videos que requieren login → puede fallar con "Sign in to confirm"

Para usar cookies reales:
1. Instalá la extensión "Get cookies.txt LOCALLY" en Chrome/Firefox
2. Logueate en youtube.com
3. Exportá cookies y guardalas como `cookies.txt` en la raíz del repo
4. Reiniciá el container: `docker compose restart backend`

El archivo se monta read-only en `/app/cookies.txt` y `downloader/core.py`
lo detecta automáticamente (prioridad sobre cookies de browser).

## Troubleshooting

**"bind source path does not exist: cookies.txt"**
→ Correr `.\scripts\docker\init.ps1` primero.

**HEALTHCHECK en `starting` por mucho tiempo**
→ Ver logs: `docker compose logs backend`. El `start_period` es 30s;
si el healthcheck falla tras eso, probablemente falta una env var en `.env`.

**Import errors al arrancar uvicorn**
→ Verificar que `PYTHONPATH=/app` y que `web/backend/app/main.py`
  se accede vía `--app-dir web/backend`. Ya configurado en el Dockerfile.

**Permisos de archivos en `./data` o `./logs`**
→ En Windows Docker Desktop no debería pasar, pero si sucede, un
  `docker compose down && docker compose up -d --build` suele arreglarlo.

**Videos no se reconvierten a H.264+AAC en el container**
→ Comportamiento conocido: los symlinks `ffmpeg.exe → ffmpeg` permiten
  que la reconversión funcione. Si no se ejecuta, es porque los codecs
  originales ya son compatibles (esperado).

## Imagen y tamaño

Build target: **< 500 MB** (python:3.12-slim + ffmpeg + venv + app).
Verificar tras build:
```powershell
docker images laguitos-backend
```
