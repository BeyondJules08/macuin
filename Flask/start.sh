#!/bin/bash

echo "🚀 MACUIN Flask - Modo Standalone (Sin Docker)"
echo "=================================================="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

echo "✅ Python detectado: $(python3 --version)"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Inicializar base de datos si no existe
if [ ! -f "macuin.db" ]; then
    echo "🗄️  Inicializando base de datos SQLite..."
    python3 init_db.py
else
    echo "✅ Base de datos existente encontrada"
fi

echo ""
echo "=================================================="
echo "✅ ¡Todo listo!"
echo "=================================================="
echo ""
echo "🌐 Iniciando servidor Flask en http://localhost:5000"
echo ""
echo "Para detener el servidor: Ctrl+C"
echo ""
echo "=================================================="
echo ""

# Iniciar Flask
export FLASK_APP=app.py
export FLASK_ENV=development
python3 app.py
