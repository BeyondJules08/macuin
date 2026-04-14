#!/bin/bash
echo "Esperando que PostgreSQL esté listo..."
for i in $(seq 1 30); do
    python -c "
import psycopg2, os, sys
try:
    url = os.getenv('DATABASE_URL','postgresql://admin:admin123@postgres:5432/macuin_db')
    parts = url.replace('postgresql://','').split('@')
    user_pass = parts[0].split(':')
    host_db = parts[1].split('/')
    host = host_db[0]
    db = host_db[1]
    conn = psycopg2.connect(host=host, user=user_pass[0], password=user_pass[1], dbname=db)
    conn.close()
    sys.exit(0)
except: sys.exit(1)
" && break
    echo "Intento $i/30 - esperando 2s..."
    sleep 2
done
echo "Inicializando base de datos..."
python init_db.py
echo "Iniciando API..."
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
