# syntax=docker/dockerfile:1.7
# ═══════════════════════════════════════════════════════════════
#  Laguitos Web — Dockerfile multi-stage
# ═══════════════════════════════════════════════════════════════
#  Stage 1 (builder):  instala dependencias Python en un venv
#  Stage 2 (runtime):  imagen minimal con ffmpeg + venv + app
#
#  Objetivo: imagen final < 500 MB, usuario no-root, healthcheck,
#  manejo correcto de señales con tini.
#
#  Build context: raíz del repo (context=. en docker-compose.yml).
# ═══════════════════════════════════════════════════════════════


# ─────────────────────────────────────────────────────────────
#  STAGE 1 · BUILDER
#  Instala deps en /opt/venv. Se descarta tras la segunda stage.
# ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Evita prompts de apt y reduce capa con --no-install-recommends
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

# build-essential sólo para compilar wheels si pip no encuentra
# binarios manylinux (bcrypt/cryptography/asyncpg suelen tenerlos
# pero dejamos esta red de seguridad).
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Venv aislado en /opt/venv (se copia limpio al runtime)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalación de deps
WORKDIR /build
COPY web/backend/requirements-docker.txt ./requirements-docker.txt

RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements-docker.txt


# ─────────────────────────────────────────────────────────────
#  STAGE 2 · RUNTIME
#  Imagen final: slim + ffmpeg + venv + código de la app.
# ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Variables de entorno que NO cambian entre dev/prod
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    DATA_DIR=/app/data

# Paquetes de sistema mínimos para runtime:
#   - ffmpeg: merge video+audio, extracción MP3, reconversión
#   - ca-certificates: HTTPS de yt-dlp
#   - curl: HEALTHCHECK
#   - tini: PID 1 correcto (manejo de SIGTERM para uvicorn)
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        ca-certificates \
        curl \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Symlinks para el bug .exe hardcoded en downloader/core.py
# (líneas 152, 216). Sin tocar código Python, hacemos que los
# paths /usr/local/bin/ffmpeg.exe y ffprobe.exe existan.
RUN ln -s /usr/bin/ffmpeg  /usr/local/bin/ffmpeg.exe \
    && ln -s /usr/bin/ffprobe /usr/local/bin/ffprobe.exe

# Venv limpio desde el builder
COPY --from=builder /opt/venv /opt/venv

# Usuario no-root con UID 1000 (alineado con el UID típico de
# Docker Desktop en Windows/WSL2; facilita permisos en bind mounts)
RUN useradd --create-home --uid 1000 --shell /bin/bash laguitos

WORKDIR /app

# Código de la aplicación (sólo lo necesario)
COPY --chown=laguitos:laguitos downloader   /app/downloader
COPY --chown=laguitos:laguitos web/backend  /app/web/backend
COPY --chown=laguitos:laguitos web/frontend /app/web/frontend
COPY --chown=laguitos:laguitos web/__init__.py /app/web/__init__.py

# Directorios runtime (se sobreescriben con volúmenes en compose,
# pero necesitamos que existan y sean escribibles por `laguitos`)
RUN mkdir -p /app/data /app/data/downloads /app/logs /app/downloads \
    && chown -R laguitos:laguitos /app/data /app/logs /app/downloads

USER laguitos

EXPOSE 8000

# Healthcheck con el endpoint verificado /api/health
# (main.py:117, sin deps de DB/auth → rápido y estable)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=30s \
    CMD curl -fsS http://localhost:8000/api/health || exit 1

# tini como PID 1: maneja SIGTERM/SIGINT correctamente para uvicorn
ENTRYPOINT ["/usr/bin/tini", "--"]

# --app-dir web/backend hace que los imports `from app.X` resuelvan
# sin necesidad de cambiar WORKDIR (que queda en /app para que el
# import `from downloader.core import ...` siga funcionando).
CMD ["uvicorn", "app.main:app", \
     "--app-dir", "web/backend", \
     "--host", "0.0.0.0", \
     "--port", "8000"]
