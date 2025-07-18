from flask import Blueprint, render_template
from extensions import mysql

main_bp = Blueprint('main', __name__)

# Ruta principal
@main_bp.route('/')
def index():
    return render_template('index.html')

# Rutas para productos
@main_bp.route('/products')
def products():
    return render_template('products.html')

# Ruta para ofertas
@main_bp.route('/ofertas')
def ofertas():
    return render_template('ofertas.html')

# Ruta para novedades
@main_bp.route('/novedades')
def novedades():
    return render_template('novedades.html')

# Ruta para carrito
@main_bp.route('/carrito')
def carrito():
    return render_template('carrito.html')

# Ruta para obtener las categorías de productos
@main_bp.route('/category/<name>')
def category(name):
    return render_template('category.html', category=name)

# Manejador de errores
@main_bp.errorhandler(404)
def not_found(error):
    flash("Página no encontrada.", "error")
    return redirect(url_for('main.index'))

@main_bp.errorhandler(500)
def internal_error(error):
    flash("Error interno del servidor. Por favor intenta nuevamente.", "error")
    return redirect(url_for('main.index'))