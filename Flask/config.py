import os
from datetime import timedelta

class Config:
    """Configuración base de la aplicación Flask
    
    NOTA: Flask ya NO accede directamente a la base de datos.
    Toda la comunicación con PostgreSQL se realiza a través de la API FastAPI.
    Esta configuración se mantiene solo para compatibilidad con extensiones
    que requieran SQLALCHEMY_DATABASE_URI.
    """

    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Configuración de base de datos — PostgreSQL (heredado, no se usa directamente)
    # La app Flask se comunica con la DB únicamente vía FastAPI (api_client.py)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://admin:admin123@postgres:5432/macuin_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuración de Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # Paginación
    ITEMS_PER_PAGE = 20
    
    # Configuración de la aplicación
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
