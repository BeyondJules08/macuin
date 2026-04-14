FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DATABASE_URL=postgresql://admin:admin123@postgres:5432/macuin_db

CMD ["python", "app.py"]
