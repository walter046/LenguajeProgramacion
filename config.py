from datetime import timedelta

class Config:
    # Configuración de MySQL
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'tienda_zapatillas'
    MYSQL_CURSORCLASS = 'DictCursor'  # Para resultados como diccionarios

    # Clave secreta para sesiones y CSRF
    SECRET_KEY = '48dfa2e08c42b1fa67f5f6ffbcba98b73febe6972123259da3759a84c304b1f5'

    # Configuración de sesiones
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)