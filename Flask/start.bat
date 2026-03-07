@echo off
echo ========================================
echo MACUIN Flask - Modo Standalone
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado
    pause
    exit /b 1
)

echo Python detectado
echo.

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo Instalando dependencias...
pip install -q --upgrade pip
pip install -q -r requirements.txt

REM Inicializar base de datos si no existe
if not exist "macuin.db" (
    echo Inicializando base de datos SQLite...
    python init_db.py
) else (
    echo Base de datos existente encontrada
)

echo.
echo ========================================
echo TODO LISTO!
echo ========================================
echo.
echo Servidor Flask en: http://localhost:5000
echo.
echo Para detener: Ctrl+C
echo.
echo ========================================
echo.

REM Iniciar Flask
set FLASK_APP=app.py
set FLASK_ENV=development
python app.py

pause
