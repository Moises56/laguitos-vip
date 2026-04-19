@echo off
title Descargador Universal de Videos
color 0A

echo.
echo ========================================
echo   Descargador Universal de Videos
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo [OK] Entorno virtual activado
) else (
    echo [AVISO] No se encontro entorno virtual
    echo Usando Python del sistema...
)

echo.
echo Iniciando aplicacion...
echo.

REM Ejecutar aplicación
python main.py

echo.
echo Aplicacion cerrada.
pause
