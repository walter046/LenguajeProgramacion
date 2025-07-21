from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from extensions import mysql
from datetime import datetime

cart_bp = Blueprint('cart', __name__)

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
@cart_bp.route('/add_to_cart/<int:producto_id>', methods=['POST'])
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
@cart_bp.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    productos = []
    direccion = None

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

    # Obtener dirección del usuario si está logeado
    if 'usuario_id' in session:
        usuario_id = session['usuario_id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT direccion FROM usuarios WHERE id = %s", (usuario_id,))
        result = cursor.fetchone()
        if result:
            direccion = result['direccion']
    else:
        # Si el usuario no está logeado, usar la dirección manual de la sesión (si existe)
        direccion = session.get('direccion_manual')

    return render_template('carrito.html', productos=productos, direccion=direccion)


# Ruta para eliminar producto del carrito
@cart_bp.route('/remove_from_cart/<int:producto_id>')
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

    return redirect(url_for('cart.view_cart'))

# Ruta para vaciar el carrito
@cart_bp.route('/clear_cart')
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

    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout')
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

@cart_bp.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    data = request.get_json()
    order_id = data.get('orderID')
    cursor = mysql.connection.cursor()

    # Obtener dirección
    if 'usuario_id' in session:
        usuario_id = session['usuario_id']
        cursor.execute("SELECT direccion FROM usuarios WHERE id = %s", (usuario_id,))
        result = cursor.fetchone()
        direccion = result['direccion'] if result else None
    else:
        usuario_id = None
        direccion = session.get('direccion_manual')

    # Obtener productos del carrito
    if usuario_id:
        cursor.execute("""
            SELECT c.zapatilla_id, c.cantidad, z.precio
            FROM carrito c
            JOIN zapatillas z ON c.zapatilla_id = z.id
            WHERE c.usuario_id = %s
        """, (usuario_id,))
    else:
        cursor.execute("""
            SELECT c.zapatilla_id, c.cantidad, z.precio
            FROM carrito c
            JOIN zapatillas z ON c.zapatilla_id = z.id
            WHERE c.usuario_id IS NULL
        """)

    carrito = cursor.fetchall()

    if not carrito:
        return jsonify({"error": "El carrito está vacío"}), 400

    total = sum(item['precio'] * item['cantidad'] for item in carrito)

    # 1. Insertar pedido en tabla pedidos
    fecha_pedido = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        INSERT INTO pedidos (usuario_id, total, estado, direccion, fecha_pedido)
        VALUES (%s, %s, %s, %s, %s)
    """, (usuario_id, total, 'pagado', direccion, fecha_pedido))
    pedido_id = cursor.lastrowid

    # 2. Insertar detalles del pedido
    for item in carrito:
        cursor.execute("""
            INSERT INTO detalles_pedido (pedido_id, zapatilla_id, cantidad, precio_unitario)
            VALUES (%s, %s, %s, %s)
        """, (pedido_id, item['zapatilla_id'], item['cantidad'], item['precio']))

        # 3. Actualizar stock
        cursor.execute("""
            UPDATE zapatillas
            SET stock = stock - %s
            WHERE id = %s
        """, (item['cantidad'], item['zapatilla_id']))

    # 4. Limpiar carrito en la base de datos
    if usuario_id:
        cursor.execute("DELETE FROM carrito WHERE usuario_id = %s", (usuario_id,))
    else:
        cursor.execute("DELETE FROM carrito WHERE usuario_id IS NULL")

    mysql.connection.commit()

    # Limpiar carrito en la sesión
    session.pop('cart', None)

    return jsonify({"message": "Pago confirmado, pedido registrado, stock actualizado"})


@cart_bp.route('/set_direccion', methods=['POST'])
def set_direccion():
    direccion = request.form.get('direccion')
    session['direccion_manual'] = direccion
    flash('Dirección guardada correctamente.', 'success')
    return redirect(url_for('cart.view_cart'))