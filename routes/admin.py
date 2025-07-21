from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from functools import wraps
from extensions import mysql

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("DEBUG - Session data:", session)  # Verifica los datos de sesión
        print("DEBUG - Rol:", session.get('usuario_rol'))
        # Verifica tanto la sesión como el rol
        if not session.get('usuario_id'):
            flash("Debes iniciar sesión para acceder a esta área", "error")
            return redirect(url_for('auth.login'))
        
        if session.get('usuario_rol') != 'ADMIN':
            flash("Acceso denegado. Se requieren privilegios de administrador", "error")
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def obtener_totales_admin():
    cursor = mysql.connection.cursor()
    
    cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
    total_usuarios = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) AS total FROM pedidos")
    total_pedidos = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) AS total FROM zapatillas")
    total_zapatillas = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) AS total FROM carrito")
    total_carritos = cursor.fetchone()['total']
    
    return {
        'total_usuarios': total_usuarios,
        'total_pedidos': total_pedidos,
        'total_zapatillas': total_zapatillas,
        'total_carritos': total_carritos
    }

# Dashboard Admin
@admin_bp.route('/dashboardadm')
@admin_required
def dashboard_admin():
    totales = obtener_totales_admin()

    return render_template(
        'admin/dashboardadm.html', **totales
    )

# CRUD CARRITO
@admin_bp.route('/carritoadm')
@admin_required
def ver_carrito():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT c.id, c.usuario_id, u.nombre AS nombre_usuario,
               z.id AS zapatilla_id, z.nombre AS nombre_zapatilla,
               c.cantidad, c.agregado_en
        FROM carrito c
        JOIN usuarios u ON c.usuario_id = u.id
        JOIN zapatillas z ON c.zapatilla_id = z.id
    """)
    carrito = cursor.fetchall()
    
    totales = obtener_totales_admin()
    
    return render_template('admin/carritoadm.html', carrito=carrito, **totales)

@admin_bp.route('/carritoadm/agregar', methods=['POST'])
@admin_required
def agregar_carrito():
    usuario_id = request.form['usuario_id']
    zapatilla_id = request.form['zapatilla_id']
    cantidad = request.form['cantidad']
    agregado_en = datetime.now()

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO carrito (usuario_id, zapatilla_id, cantidad, agregado_en)
        VALUES (%s, %s, %s, %s)
    """, (usuario_id, zapatilla_id, cantidad, agregado_en))
    mysql.connection.commit()

    flash('Producto agregado al carrito')
    return redirect(url_for('admin.ver_carrito'))

@admin_bp.route('/carritoadm/editar/<int:id>', methods=['POST'])
@admin_required
def editar_carrito(id):
    usuario_id = request.form['usuario_id']
    zapatilla_id = request.form['zapatilla_id']
    cantidad = request.form['cantidad']

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE carrito
        SET usuario_id = %s, zapatilla_id = %s, cantidad = %s
        WHERE id = %s
    """, (usuario_id, zapatilla_id, cantidad, id))
    mysql.connection.commit()

    flash('Producto actualizado en el carrito')
    return redirect(url_for('admin.ver_carrito'))

@admin_bp.route('/carritoadm/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_carrito(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM carrito WHERE id = %s", (id,))
    mysql.connection.commit()
    flash('Producto eliminado del carrito')
    return redirect(url_for('admin.ver_carrito'))

# CRUD USUARIOS
# Mostrar todos los usuarios
@admin_bp.route('/usuariosadm')
@admin_required
def usuarios():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios")
    
    usuarios = cursor.fetchall()
    
    totales = obtener_totales_admin()
    
    return render_template('admin/usuariosadm.html', usuarios=usuarios, **totales)

# Agregar un nuevo usuario
@admin_bp.route('/usuariosadm/agregar', methods=['POST'])
@admin_required
def agregar_usuario():
    nombre = request.form['nombre']
    username = request.form['username']
    password = request.form['password']
    direccion = request.form['direccion']
    telefono = request.form['telefono']
    rol = request.form['rol']

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO usuarios (nombre, username, password, direccion, telefono, rol, fecha_registro)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """, (nombre, username, password, direccion, telefono, rol))
    mysql.connection.commit()
    flash('Usuario agregado correctamente')
    return redirect(url_for('admin.usuarios'))

# Editar un usuario existente
@admin_bp.route('/usuariosadm/editar/<int:id>', methods=['POST'])
@admin_required
def editar_usuario(id):
    nombre = request.form['nombre']
    username = request.form['username']
    direccion = request.form['direccion']
    telefono = request.form['telefono']
    rol = request.form['rol']

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE usuarios
        SET nombre=%s, username=%s, direccion=%s, telefono=%s, rol=%s
        WHERE id=%s
    """, (nombre, username, direccion, telefono, rol, id))
    mysql.connection.commit()
    flash('Usuario actualizado correctamente')
    return redirect(url_for('admin.usuarios'))

# Eliminar un usuario
@admin_bp.route('/usuariosadm/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_usuario(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    mysql.connection.commit()
    flash('Usuario eliminado correctamente')
    return redirect(url_for('admin.usuarios'))

# CRUD ZAPATILLAS
@admin_bp.route('/zapatillasadm')
@admin_required
def listar_zapatillas():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM zapatillas")
    
    zapatillas = cursor.fetchall()
    
    totales = obtener_totales_admin()
    
    return render_template('admin/zapatillasadm.html', zapatillas=zapatillas, **totales)

@admin_bp.route('/zapatillasadm/agregar', methods=['POST'])
@admin_required
def agregar_zapatilla():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    imagen_url = request.form['imagen_url']

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO zapatillas (nombre, descripcion, precio, imagen_url) VALUES (%s, %s, %s, %s)",
                   (nombre, descripcion, precio, imagen_url))
    mysql.connection.commit()
    flash('Zapatilla agregada correctamente', 'success')
    return redirect(url_for('admin.listar_zapatillas'))

@admin_bp.route('/zapatillasadm/editar/<int:id>', methods=['POST'])
@admin_required
def editar_zapatilla(id):
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    imagen_url = request.form['imagen_url']

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE zapatillas 
        SET nombre=%s, descripcion=%s, precio=%s, imagen_url=%s 
        WHERE id=%s
    """, (nombre, descripcion, precio, imagen_url, id))
    mysql.connection.commit()
    flash('Zapatilla actualizada correctamente', 'success')
    return redirect(url_for('admin.listar_zapatillas'))

@admin_bp.route('/zapatillasadm/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_zapatilla(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM zapatillas WHERE id = %s", (id,))
    mysql.connection.commit()
    flash('Zapatilla eliminada correctamente', 'success')
    return redirect(url_for('admin.listar_zapatillas'))

# CRUD PEDIDOS
@admin_bp.route('/pedidosadm')
@admin_required
def listar_pedidos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM pedidos")
    
    pedidos = cursor.fetchall()
    
    totales = obtener_totales_admin()
    
    return render_template('admin/pedidosadm.html', pedidos=pedidos, **totales)

@admin_bp.route('/pedidosadm/eliminar/<int:id>')
@admin_required
def eliminar_pedido(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM pedidos WHERE id = %s", (id,))
    mysql.connection.commit()
    return redirect(url_for('admin.listar_pedidos'))

@admin_bp.route('/pedidosadm/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_pedido(id):
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        total = request.form['total']
        estado = request.form['estado']
        direccion = request.form['direccion']
        fecha_pedido = request.form['fecha_pedido']
        cursor.execute("""
            UPDATE pedidos
            SET usuario_id=%s, total=%s, estado=%s, direccion=%s, fecha_pedido=%s
            WHERE id=%s
        """, (usuario_id, total, estado, direccion, fecha_pedido, id))
        mysql.connection.commit()
        return redirect(url_for('admin.listar_pedidos'))
    
    cursor.execute("SELECT * FROM pedidos WHERE id = %s", (id,))
    pedido = cursor.fetchone()
    return render_template('admin/editar_pedidoadm.html', pedido=pedido)

@admin_bp.route('/pedidosadm/agregar', methods=['GET', 'POST'])
@admin_required
def agregar_pedido():
    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        total = request.form['total']
        estado = request.form['estado']
        direccion = request.form['direccion']
        fecha_pedido = request.form['fecha_pedido']
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO pedidos (usuario_id, total, estado, direccion, fecha_pedido)
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario_id, total, estado, direccion, fecha_pedido))
        mysql.connection.commit()
        return redirect(url_for('admin.listar_pedidos'))
    
    return render_template('admin/agregar_pedidoadm.html')
