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


# === CRUD ZAPATILLAS ===

@admin_bp.route('/zapatillas')
@admin_required
def lista_zapatillas():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM zapatillas")
    zapatillas = cursor.fetchall()
    cursor.close()
    return render_template('admin/zapatillas/index.html', zapatillas=zapatillas)

@admin_bp.route('/zapatillas/crear', methods=['GET', 'POST'])
@admin_required
def crear_zapatilla():
    if request.method == 'POST':
        datos = (
            request.form['nombre'], request.form['marca'], request.form['descripcion'],
            request.form['precio'], request.form['stock'], request.form['imagen_url'],
            request.form['talla'], request.form['genero'], request.form['tipo'], request.form['colaboracion']
        )
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO zapatillas (nombre, marca, descripcion, precio, stock, imagen_url, talla, genero, tipo, colaboracion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, datos)
        mysql.connection.commit()
        cursor.close()
        flash("Zapatilla creada exitosamente")
        return redirect(url_for('admin.lista_zapatillas'))
    return render_template('admin/zapatillas/crear.html')

@admin_bp.route('/zapatillas/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_zapatilla(id):
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        datos = (
            request.form['nombre'], request.form['marca'], request.form['descripcion'],
            request.form['precio'], request.form['stock'], request.form['imagen_url'],
            request.form['talla'], request.form['genero'], request.form['tipo'], request.form['colaboracion'], id
        )
        cursor.execute("""
            UPDATE zapatillas SET nombre=%s, marca=%s, descripcion=%s, precio=%s, stock=%s, imagen_url=%s,
            talla=%s, genero=%s, tipo=%s, colaboracion=%s WHERE id=%s
        """, datos)
        mysql.connection.commit()
        flash("Zapatilla actualizada")
        return redirect(url_for('admin.lista_zapatillas'))
    cursor.execute("SELECT * FROM zapatillas WHERE id=%s", (id,))
    zapatilla = cursor.fetchone()
    cursor.close()
    return render_template('admin/zapatillas/editar.html', zapatilla=zapatilla)

@admin_bp.route('/zapatillas/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_zapatilla(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM zapatillas WHERE id=%s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash("Zapatilla eliminada")
    return redirect(url_for('admin.lista_zapatillas'))

# === CRUD USUARIOS ===

@admin_bp.route('/usuarios')
@admin_required
def lista_usuarios():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nombre, username, direccion, telefono, rol FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    return render_template('admin/usuarios/index.html', usuarios=usuarios)

@admin_bp.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_usuario(id):
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        datos = (
            request.form['nombre'], request.form['username'], request.form['direccion'],
            request.form['telefono'], request.form['rol'], id
        )
        cursor.execute("""
            UPDATE usuarios SET nombre=%s, username=%s, direccion=%s, telefono=%s, rol=%s WHERE id=%s
        """, datos)
        mysql.connection.commit()
        flash("Usuario actualizado")
        return redirect(url_for('admin.lista_usuarios'))
    cursor.execute("SELECT id, nombre, username, direccion, telefono, rol FROM usuarios WHERE id=%s", (id,))
    usuario = cursor.fetchone()
    cursor.close()
    return render_template('admin/usuarios/editar.html', usuario=usuario)

@admin_bp.route('/usuarios/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_usuario(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=%s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash("Usuario eliminado")
    return redirect(url_for('admin.lista_usuarios'))

# === CRUD PEDIDOS ===

@admin_bp.route('/pedidos')
@admin_required
def lista_pedidos():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT p.id, u.nombre, p.total, p.estado, p.fecha_pedido
        FROM pedidos p
        JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.fecha_pedido DESC
    """)
    pedidos = cursor.fetchall()
    cursor.close()
    return render_template('admin/pedidos/index.html', pedidos=pedidos)

@admin_bp.route('/pedidos/<int:id>')
@admin_required
def ver_pedido(id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT p.id, u.nombre, p.total, p.estado, p.fecha_pedido
        FROM pedidos p
        JOIN usuarios u ON p.usuario_id = u.id
        WHERE p.id = %s
    """, (id,))
    pedido = cursor.fetchone()

    cursor.execute("""
        SELECT d.cantidad, d.precio_unitario, z.nombre
        FROM detalles_pedido d
        JOIN zapatillas z ON d.zapatilla_id = z.id
        WHERE d.pedido_id = %s
    """, (id,))
    detalles = cursor.fetchall()
    cursor.close()
    return render_template('admin/pedidos/ver.html', pedido=pedido, detalles=detalles)

@admin_bp.route('/pedidos/estado/<int:id>', methods=['POST'])
@admin_required
def cambiar_estado_pedido(id):
    nuevo_estado = request.form['estado']
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE pedidos SET estado=%s WHERE id=%s", (nuevo_estado, id))
    mysql.connection.commit()
    cursor.close()
    flash("Estado actualizado")
    return redirect(url_for('admin.ver_pedido', id=id))
