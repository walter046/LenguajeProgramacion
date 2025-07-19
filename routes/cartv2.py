from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from extensions import mysql
from datetime import datetime

cartv2_bp = Blueprint('cartv2', __name__)

# Configuración de PayPal
PAYPAL_CLIENT_ID = 'Abg4b8sFLI31Qe5J_MHBrVya9Itvj6Mte0d7wzRpBrTD_hPZfRWmivQxNObfZJhjPf_6VP10NdNt4Za6'
PAYPAL_SECRET = 'EKf3gi0lstTZeK-E564vzECoERV5gFwYj-RpwtbxJgpPfWPzgB5HH1GCS8pXwfNx_9Amnb3c2Psa4DMU'  # Coloca aquí tu client secret real
PAYPAL_BASE_URL = 'https://sandbox.paypal.com'  # Sandbox

def get_paypal_token():
    response = requests.post(
        f"{PAYPAL_BASE_URL}/v1/oauth2/token",
        headers={"Accept": "application/json"},
        data={"grant_type": "client_credentials"},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
    )
    return response.json().get("access_token")

# Ruta para agregar al carrito
@cartv2_bp.route('/add_to_cart/<int:producto_id>', methods=['POST'])
def add_to_cart(producto_id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(producto_id)

    try:
        cursor = mysql.connection.cursor()

        usuario_id = session.get('usuario_id')  # Será None si no hay sesión
        cantidad = 1
        agregado_en = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = """
            INSERT INTO carrito (usuario_id, zapatilla_id, cantidad, agregado_en)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (usuario_id, producto_id, cantidad, agregado_en))
        mysql.connection.commit()

        flash('Producto agregado al carrito', 'success')

    except Exception as e:
        flash(f'Error al agregar producto a la base de datos: {e}', 'danger')

    return redirect(url_for('products.products'))

# Ruta para ver el carrito
@cartv2_bp.route('/cart')
def view_cart():
    cart = session.get('cart', [])

    productos = []
    if cart:
        cursor = mysql.connection.cursor()
        format_strings = ','.join(['%s'] * len(cart))
        query = f"""
            SELECT id, nombre, descripcion, precio, imagen_url 
            FROM zapatillas 
            WHERE id IN ({format_strings})
        """
        cursor.execute(query, tuple(cart))
        productos = cursor.fetchall()

    return render_template('carritov2.html', productos=productos)

# Ruta para eliminar producto del carrito
@cartv2_bp.route('/remove_from_cart/<int:producto_id>')
def remove_from_cart(producto_id):
    if 'cart' in session:
        session['cart'] = [pid for pid in session['cart'] if pid != producto_id]

        # Eliminar también de la tabla 'carrito'
        try:
            cursor = mysql.connection.cursor()
            if 'usuario_id' in session:
                # Elimina solo para ese usuario si está logueado
                cursor.execute("""
                    DELETE FROM carrito 
                    WHERE usuario_id = %s AND zapatilla_id = %s 
                    LIMIT 1
                """, (session['usuario_id'], producto_id))
            else:
                # Elimina si usuario_id es NULL
                cursor.execute("""
                    DELETE FROM carrito 
                    WHERE usuario_id IS NULL AND zapatilla_id = %s 
                    LIMIT 1
                """, (producto_id,))
            mysql.connection.commit()
        except Exception as e:
            flash(f'Error al eliminar de la base de datos: {e}', 'danger')

        flash('Producto eliminado del carrito', 'info')

    return redirect(url_for('cartv2.view_cart'))

# Ruta para vaciar el carrito
@cartv2_bp.route('/clear_cart')
def clear_cart():
    if 'cart' in session:
        session.pop('cart', None)

        try:
            cursor = mysql.connection.cursor()
            if 'usuario_id' in session:
                cursor.execute("DELETE FROM carrito WHERE usuario_id = %s", (session['usuario_id'],))
            else:
                cursor.execute("DELETE FROM carrito WHERE usuario_id IS NULL")
            mysql.connection.commit()
        except Exception as e:
            flash(f'Error al vaciar carrito en base de datos: {e}', 'danger')

        flash('Carrito vaciado', 'warning')

    return redirect(url_for('cartv2.view_cart'))

@cartv2_bp.route('/checkout')
def checkout():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT c.id, p.nombre, p.precio, p.stock, p.imagen_url, c.cantidad
        FROM carrito c
        JOIN zapatillas p ON c.zapatilla_id = p.id
    """)
    productos = cursor.fetchall()

    total = sum(p['precio'] * p['cantidad'] for p in productos)
    return render_template('checkout.html', productos=productos, total=total)

from flask import request, jsonify

@cartv2_bp.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    data = request.get_json()
    order_id = data.get('orderID')

    cursor = mysql.connection.cursor()

    # Obtener productos del carrito
    if 'usuario_id' in session:
        cursor.execute("SELECT zapatilla_id, cantidad FROM carrito WHERE usuario_id = %s", (session['usuario_id'],))
    else:
        cursor.execute("SELECT zapatilla_id, cantidad FROM carrito WHERE usuario_id IS NULL")

    carrito = cursor.fetchall()

    # Descontar stock desde 'zapatillas'
    for item in carrito:
        cursor.execute("""
            UPDATE zapatillas
            SET stock = stock - %s
            WHERE id = %s
        """, (item['cantidad'], item['zapatilla_id']))

    # Vaciar carrito (base de datos)
    if 'usuario_id' in session:
        cursor.execute("DELETE FROM carrito WHERE usuario_id = %s", (session['usuario_id'],))
    else:
        cursor.execute("DELETE FROM carrito WHERE usuario_id IS NULL")

    mysql.connection.commit()

    # Vaciar carrito de la sesión
    session.pop('cart', None)

    return jsonify({"message": "Pago confirmado y stock actualizado"})
