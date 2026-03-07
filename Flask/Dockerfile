# Usa una imagen base de Python ligera
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación
COPY . .

# Expone el puerto en el que corre Flask
EXPOSE 5000

# Variables de entorno por defecto
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV INIT_MOCK_DATA=true
ENV DATABASE_URL=sqlite:///:memory:

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
