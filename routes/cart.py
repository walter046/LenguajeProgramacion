from flask import Blueprint, render_template, redirect, url_for, session, flash, request, jsonify
from extensions import mysql

cart_bp = Blueprint('cart', __name__)

# Ruta para agregar productos al carrito
@cart_bp.route('/agregarCarrito', methods=['POST'])
def add_to_cart():
    try:
        print("=== AGREGAR AL CARRITO ===")
        data = request.get_json()
        print("Datos recibidos:", data)
        
        product_id = str(data.get('id'))
        product_name = data.get('nombre')
        product_price = float(data.get('precio'))
        
        print(f"ID: {product_id}, Nombre: {product_name}, Precio: {product_price}")

        # Inicializar el carrito si no existe 
        if 'cart' not in session:
            session['cart'] = {}
            print("Carrito inicializado")

        # Actualizamoss el carrito
        if product_id in session['cart']:
            session['cart'][product_id]['cantidad'] += 1
            print(f"Producto existente, cantidad aumentada")
        else:
            session['cart'][product_id] = {
                'nombre': product_name,
                'precio': product_price,
                'cantidad': 1
            }
            print(f"Nuevo producto añadido al carrito")
        
        session.modified = True
        
        # Calcular cantidad total de items totales
        total_items = sum(item['cantidad'] for item in session['cart'].values())
        print(f"Total de items en carrito: {total_items}")
        print("Carrito actual:", session['cart'])

        return jsonify({
            'success': True,
            'message': f'{product_name} añadido al carrito.',
            'cart_count': total_items,
            'cart': session['cart']
        })
    except Exception as e:
        print(f"Error en add_to_cart: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

# Ruta para actualizar el carrito
@cart_bp.route('/actualizarCarrito', methods=['POST'])
def update_cart():
    try:
        data = request.get_json()
        product_id = str(data.get('id'))
        action = data.get('action')

        if 'cart' not in session or product_id not in session['cart']:
            return jsonify({'success': False, 'message': 'Producto no encontrado en el carrito'})

        if action == 'remove':
            del session['cart'][product_id]
        elif action == 'decrease':
            if session['cart'][product_id]['cantidad'] > 1:
                session['cart'][product_id]['cantidad'] -= 1
            else:
                del session['cart'][product_id]
        elif action == 'increase':
            session['cart'][product_id]['cantidad'] += 1
        
        session.modified = True
        total_items = sum(item['cantidad'] for item in session['cart'].values())

        return jsonify({
            'success': True,
            'cart_count': total_items,
            'cart': session['cart']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

# Ruta para obtener el carrito actual
@cart_bp.route('/get_cart')
def get_cart():
    print("=== GET CART ===")
    print("Session actual:", dict(session))
    print("Carrito actual:", session.get('cart', {}))
    return jsonify({'cart': session.get('cart', {})})

# Ruta para depurar el carrito
@cart_bp.route('/debug_cart')
def debug_cart():
    print("=== DEBUG CART ===")
    print("Session completa:", dict(session))
    print("Carrito:", session.get('cart', {}))
    return jsonify({
        'session': dict(session),
        'cart': session.get('cart', {}),
        'cart_keys': list(session.get('cart', {}).keys())
    })

# Ruta para guardar el carrito en historial
@cart_bp.route('/guardar_carrito', methods=['POST'])
def guardar_carrito():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para guardar el carrito'}), 401
    
    try:
        usuario_id = session['usuario_id']
        carrito_data = session.get('cart', {})
        
        if not carrito_data:
            return jsonify({'success': False, 'message': 'El carrito está vacío'}), 400
        
        cursor = mysql.connection.cursor()
        
        # Guardar en historial de carrito
        import json
        carrito_json = json.dumps(carrito_data)
        
        cursor.execute("""
            INSERT INTO historial_carrito (usuario_id, carrito_data) 
            VALUES (%s, %s)
        """, (usuario_id, carrito_json))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Carrito guardado correctamente'
        })
    except Exception as e:
        # Manejo de errores
        print(f"Error al guardar carrito: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Ruta para cargar el carrito actual desde el historial
@cart_bp.route('/guardar_carrito_actual', methods=['POST'])
def guardar_carrito_actual():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión'}), 401
    
    try:
        data = request.get_json()
        carrito_data = data.get('carrito', {})
        
        if not carrito_data:
            return jsonify({'success': False, 'message': 'No hay datos del carrito'}), 400
        
        # Guardar en la sesión actual
        session['cart'] = carrito_data
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Carrito cargado correctamente'
        })
        
    except Exception as e:
        print(f"Error al cargar carrito: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Ruta para vaciar el carrito
@cart_bp.route('/clear_cart', methods=['POST'])
def clear_cart():
    try:
        session.pop('cart', None)
        session.modified = True
        return jsonify({
            'success': True,
            'message': 'Carrito vaciado correctamente'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

# Ruta para actualizar la cantidad de un item en el carrito
@cart_bp.route('/update_cart_item', methods=['POST'])
def update_cart_item():
    try:
        data = request.get_json()
        product_id = str(data.get('id'))
        change = int(data.get('change', 0))

        if 'cart' not in session:
            session['cart'] = {}

        if product_id in session['cart']:
            current_quantity = session['cart'][product_id]['cantidad']
            new_quantity = current_quantity + change
            
            if new_quantity <= 0:
                # Eliminar el item si la cantidad llega a 0 o menos
                del session['cart'][product_id]
                message = f"Producto eliminado del carrito"
            else:
                # Actualizar la cantidad
                session['cart'][product_id]['cantidad'] = new_quantity
                message = f"Cantidad actualizada"
        else:
            return jsonify({
                'success': False,
                'message': 'Producto no encontrado en el carrito'
            }), 404

        session.modified = True
        total_items = sum(item['cantidad'] for item in session['cart'].values())

        return jsonify({
            'success': True,
            'message': message,
            'cart_count': total_items,
            'cart': session['cart']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

