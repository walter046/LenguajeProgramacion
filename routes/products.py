from flask import Blueprint, render_template, redirect, url_for, session, flash, request, jsonify
from extensions import mysql

products_bp = Blueprint('products', __name__)

@products_bp.route('/products')
def products():
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

    cursor.execute(query, tuple(params))
    productos = cursor.fetchall()
    cursor.close()

    lista_productos = [{
        'id': p['0'],
        'nombre': p['1'],
        'descripcion': p['2'],
        'precio': float(p['3']),
        'imagen': p['4']
    } for p in productos]

    return render_template('products.html', productos=lista_productos)

@products_bp.route('/products/<int:producto_id>')
def detalle_products(producto_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nombre, descripcion, precio, imagen_url FROM zapatillas WHERE id = %s", (producto_id,))
    producto = cursor.fetchone()
    cursor.close()

    if producto:
        producto_dict = {
            'id': producto['0'],
            'nombre': producto['1'],
            'descripcion': producto['2'],
            'precio': float(producto['3']),
            'imagen': producto['4']
        }
        return render_template('detalle_products.html', producto=producto_dict)
    else:
        return "Producto no encontrado", 404
