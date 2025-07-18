from flask_mysqldb import MySQL
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Inicialización de Flask-MySQL
mysql = MySQL()

# Inicialización de Flask-Limiter
limiter = Limiter(
    key_func=get_remote_address, # Usa la IP remota para limitar
    storage_uri="memory://",     # Almacenamiento en memoria para desarrollo
)