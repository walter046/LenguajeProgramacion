from flask import Flask

app = Flask(__name__)

# Configuración de la aplicación
from config import Config
app.config.from_object(Config)

# Inicializar extensiones
from extensions import mysql, limiter
mysql.init_app(app)
limiter.init_app(app)

# Rutas de autenticación
from routes.auth import auth_bp
app.register_blueprint(auth_bp)

# Rutas para usuarios
from routes.user import user_bp
app.register_blueprint(user_bp)

# Rutas principales
from routes.main import main_bp
app.register_blueprint(main_bp)

# Rutas de carrito
from routes.cart import cart_bp
app.register_blueprint(cart_bp)

# Rutas de pedidos
from routes.pedidos import pedidos_bp
app.register_blueprint(pedidos_bp)

if __name__ == '__main__':
    app.run(debug=True)