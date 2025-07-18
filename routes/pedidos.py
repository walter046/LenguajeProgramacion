from flask import Blueprint, render_template, redirect, url_for, session, flash, request, jsonify
from extensions import mysql

pedidos_bp = Blueprint('pedidos', __name__)

# Ruta para ver los pedidos del usuario
@pedidos_bp.route('/mis_pedidos')
def mis_pedidos():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para ver tus pedidos", "error")
        return redirect(url_for('auth.login'))
    
    try:
        usuario_id = session['usuario_id']
        cursor = mysql.connection.cursor()
        
        # Obtener pedidos del usuario
        cursor.execute("""
            SELECT p.*, COUNT(d.id_detalle) as num_items
            FROM pedidos p
            LEFT JOIN detalles_pedido d ON p.id_pedido = d.pedido_id
            WHERE p.usuario_id = %s
            GROUP BY p.id_pedido
            ORDER BY p.fecha_pedido DESC
        """, (usuario_id,))
        
        pedidos = cursor.fetchall()
        
        # Obtenemos historial de carritos guardados
        cursor.execute("""
            SELECT * FROM historial_carrito 
            WHERE usuario_id = %s 
            ORDER BY fecha_creacion DESC
        """, (usuario_id,))
        
        historial_carritos = cursor.fetchall()
        cursor.close()
        
        return render_template('mis_pedidos.html', pedidos=pedidos, historial_carritos=historial_carritos)
        
    except Exception as e:
        # Manejo de errores
        print(f"Error al obtener pedidos: {e}")
        flash("Error al cargar los pedidos", "error")
        return redirect(url_for('user.dashboard'))

# Ruta para crear un pedido
@pedidos_bp.route('/crear_pedido', methods=['POST'])
def crear_pedido():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para crear un pedido'}), 401
    
    try:
        data = request.get_json()
        direccion = data.get('direccion', '')
        telefono = data.get('telefono', '')
        
        carrito = session.get('cart', {})
        if not carrito:
            return jsonify({'success': False, 'message': 'El carrito está vacío'}), 400
        
        usuario_id = session['usuario_id']
        total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
        
        cursor = mysql.connection.cursor()
        
        # Crear el pedido
        cursor.execute("""
            INSERT INTO pedidos (usuario_id, total, direccion_envio, telefono)
            VALUES (%s, %s, %s, %s)
        """, (usuario_id, total, direccion, telefono))
        
        pedido_id = cursor.lastrowid
        
        # Crear los detalles del pedido
        for product_id, item in carrito.items():
            subtotal = item['precio'] * item['cantidad']
            cursor.execute("""
                INSERT INTO detalles_pedido (pedido_id, zapatilla_id, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (pedido_id, product_id, item['cantidad'], item['precio'], subtotal))
        
        mysql.connection.commit()
        cursor.close()
        
        # Limpiar el carrito después de crear el pedido
        session.pop('cart', None)
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': f'Pedido creado correctamente. Número de pedido: {pedido_id}',
            'pedido_id': pedido_id
        })
        
    except Exception as e:
        print(f"Error al crear pedido: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Ruta para cancelar un pedido
@pedidos_bp.route('/cancelar_pedido/<int:pedido_id>', methods=['POST'])
def cancelar_pedido(pedido_id):
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión'}), 401
    
    try:
        usuario_id = session['usuario_id']
        cursor = mysql.connection.cursor()
        
        # Verificar que el pedido pertenece al usuario
        cursor.execute("""
            SELECT estado FROM pedidos 
            WHERE id_pedido = %s AND usuario_id = %s
        """, (pedido_id, usuario_id))
        
        pedido = cursor.fetchone()
        if not pedido:
            return jsonify({'success': False, 'message': 'Pedido no encontrado'}), 404
        
        if pedido['estado'] in ['enviado', 'entregado']:
            return jsonify({'success': False, 'message': 'No se puede cancelar un pedido ya enviado'}), 400
        
        # Cancelar el pedido
        cursor.execute("""
            UPDATE pedidos SET estado = 'cancelado' 
            WHERE id_pedido = %s
        """, (pedido_id,))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Pedido cancelado correctamente'
        })
        
    except Exception as e:
        print(f"Error al cancelar pedido: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
