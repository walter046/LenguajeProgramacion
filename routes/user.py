from flask import Blueprint, render_template, redirect, url_for, session, flash, request, jsonify
from extensions import mysql

user_bp = Blueprint('user', __name__)

# Ruta del dashboard
@user_bp.route('/dashboard')
def dashboard():
    # Verificar si el usuario está autenticado
    if 'usuario_id' in session:
        usuario_id = session['usuario_id']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, nombre, username, direccion, telefono FROM usuarios WHERE id=%s", (usuario_id,))
        usuario = cursor.fetchone()
        cursor.close()
        
        if usuario:
            # Convertir la tupla a un diccionario para facilitar el acceso en la plantilla
            usuario_dict = {
                'id': usuario['id'],
                'nombre': usuario['nombre'],
                'username': usuario['username'],
                'direccion': usuario['direccion'],
                'telefono': usuario['telefono']
       
            }
            return render_template('dashboard.html', usuario=usuario_dict)
        else:
            flash("Usuario no encontrado.", "error")
            # Si el usuario no existe, redirigir al login
            return redirect(url_for('login'))
            
    flash("Por favor inicia sesión para acceder.", "warning")
    # Si no está autenticado, redirigir al login
    return redirect(url_for('login'))

# Ruta para actualizar los datos del usuario
@user_bp.route('/update_user', methods=['POST'])
def update_user():
    if 'usuario_id' not in session:
        flash("No tienes autorización para realizar esta acción.", "error")
        return redirect(url_for('login'))
    
    try:
        # Obtener datos del formulario
        usuario_id = session['usuario_id']
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        direccion = request.form.get('direccion', '').strip()
        telefono = request.form.get('telefono', '').strip()
        
        # Validaciones para los campos vacíos
        if not all([nombre, email, direccion, telefono]):
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('dashboard'))
        
        # Verificar si el email ya existe para otro usuario
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE username=%s AND id != %s", (email, usuario_id))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash("El email ya está en uso por otro usuario.", "error")
            cursor.close()
            # Redirigir al dashboard si ya esta en uso
            return redirect(url_for('dashboard'))
        
        # Actualizar datos
        cursor.execute("""
            UPDATE usuarios SET nombre=%s, username=%s, direccion=%s, telefono=%s WHERE id=%s
        """, (nombre, email, direccion, telefono, usuario_id))
        mysql.connection.commit()
        cursor.close()
        
        # Actualizar el nombre en la sesión si ha cambiado
        session['usuario_nombre'] = nombre
        
        flash("✅ Tus datos han sido actualizados correctamente.", "success")
        
    except Exception as e:
        # Manejo de errores
        flash("Error al actualizar los datos. Por favor intenta nuevamente.", "error")
        print(f"Error updating user: {e}")
    
    # Redirigir al dashboard después de la actualización
    return redirect(url_for('dashboard'))

# Ruta para eliminar el usuario
@user_bp.route('/delete_user')
def delete_user():
    # Verificar si el usuario está autenticado
    if 'usuario_id' not in session:
        flash("No tienes autorización para realizar esta acción.", "error")
        return redirect(url_for('login'))
    
    try:
        # Obtener el ID del usuario de la sesión
        usuario_id = session['usuario_id']
        
        # Obtener nombre del usuario antes de eliminar
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT nombre FROM usuarios WHERE id=%s", (usuario_id,))
        user_data = cursor.fetchone()
        username = user_data[0] if user_data else "Usuario"
        
        # Eliminar usuario
        cursor.execute("DELETE FROM usuarios WHERE id=%s", (usuario_id,))
        mysql.connection.commit()
        cursor.close()
        
        # Cerrar sesión
        session.pop('usuario_id', None)
        session.pop('usuario_nombre', None) # Eliminar también el nombre
        flash(f"Cuenta de {username} eliminada correctamente. Lamentamos verte partir.", "info")
        
    except Exception as e:
        # Manejo de errores
        flash("Error al eliminar la cuenta. Por favor intenta nuevamente.", "error")
        print(f"Error deleting user: {e}")
    
    # Redirigir al inicio después de eliminar la cuenta
    return redirect(url_for('index'))

# Ruta para obtener información del usuario (API)
@user_bp.route('/api/user_info')
def get_user_info():
    # Verificar si el usuario está autenticado
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    # Obtener el ID del usuario de la sesión
    usuario_id = session['usuario_id']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nombre, username, direccion, telefono FROM usuarios WHERE id=%s", (usuario_id,))
    usuario = cursor.fetchone()
    cursor.close()
    
    if usuario:
        return jsonify({
            'id': usuario[0],
            'nombre': usuario[1],
            'email': usuario[2],
            'direccion': usuario[3],
            'telefono': usuario[4]
        })
    
    return jsonify({'error': 'Usuario no encontrado'}), 404