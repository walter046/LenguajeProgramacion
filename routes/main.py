from flask import Blueprint, render_template, redirect, url_for, session, flash, request, jsonify
from extensions import mysql

main_bp = Blueprint('main', __name__)

# Ruta principal
@main_bp.route('/')
def index():
    cursor = mysql.connection.cursor()
    
    genero = request.args.get('genero')
    tipo = request.args.get('tipo')
    precio = request.args.get('precio', type=float)
    colaboracion = request.args.get('colaboracion')
    tallas = request.args.getlist('tallas')

    query = "SELECT id, nombre, descripcion, precio, imagen_url FROM zapatillas WHERE 1=1"
    params = [] 

    if genero:
        query += " AND genero = %s"
        params.append(genero)
    if tipo:
        query += " AND tipo = %s"
        params.append(tipo)
    if precio:
        query += " AND precio <= %s"
        params.append(precio)
    if colaboracion:
        query += " AND colaboracion LIKE %s"
        params.append(f"%{colaboracion}%")
    if tallas:
        query += " AND talla IN ({})".format(','.join(['%s'] * len(tallas)))
        params.extend(tallas)
        
    # obtener 3 productos aleatorios
    if not any([genero, tipo, precio, colaboracion, tallas]):
        query += " ORDER BY RAND() LIMIT 3"
    else:
        cursor.execute(query, tuple(params))

    cursor.execute(query, tuple(params))
    productos = cursor.fetchall()
    cursor.close()

    lista_productos = [{
        'id': p['id'],
        'nombre': p['nombre'],
        'descripcion': p['descripcion'],
        'precio': float(p['precio']),
        'imagen': p['imagen_url']
    } for p in productos]
    
    return render_template('index.html', productos=lista_productos)

# Ruta para marcas
@main_bp.route('/marcas')
def marcas():
    return render_template('marcas.html')

# Ruta para locales
@main_bp.route('/locales')
def locales():
    return render_template('locales.html')

# Ruta para carrito
@main_bp.route('/carrito')
def carrito():
    return render_template('carrito.html')

# Manejador de errores
@main_bp.errorhandler(404)
def not_found(error):
    flash("Página no encontrada.", "error")
    return redirect(url_for('main.index'))

@main_bp.errorhandler(500)
def internal_error(error):
    flash("Error interno del servidor. Por favor intenta nuevamente.", "error")
    return redirect(url_for('main.index'))