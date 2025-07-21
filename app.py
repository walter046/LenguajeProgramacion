from flask import Flask

app = Flask(__name__)

# Configuración de la aplicación
from config import Config
app.config.from_object(Config)

# Inicializar extensiones
from extensions import mysql
mysql.init_app(app)

# Rutas de autenticación
from routes.auth import auth_bp
app.register_blueprint(auth_bp)

# Rutas para usuarios
from routes.user import user_bp
app.register_blueprint(user_bp)

# Rutas principales
from routes.main import main_bp
app.register_blueprint(main_bp)


# Rutas de pedidos
from routes.pedidos import pedidos_bp
app.register_blueprint(pedidos_bp)

# Rutas de administración
from routes.admin import admin_bp
app.register_blueprint(admin_bp)

# Rutas de productos
from routes.products import products_bp
app.register_blueprint(products_bp)


from routes.cart import cart_bp
app.register_blueprint(cart_bp)

from routes.dashboardadm import admin_dashboard_bp
app.register_blueprint(admin_dashboard_bp)

from routes.usuariosadm import usuariosadm_bp
app.register_blueprint(usuariosadm_bp)

from routes.zapatillasadm import zapatillas_adm_bp
app.register_blueprint(zapatillas_adm_bp)

from routes.pedidosadm import pedidosadm_bp
app.register_blueprint(pedidosadm_bp)

from routes.carritoadm import carrito_bp
app.register_blueprint(carrito_bp)

if __name__ == '__main__':
    app.run(debug=True)

