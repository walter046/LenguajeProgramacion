from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import mysql

usuariosadm_bp = Blueprint('usuariosadm', __name__)

# Mostrar todos los usuarios
@usuariosadm_bp.route('/usuariosadm')
def usuarios():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    return render_template('usuariosadm.html', usuarios=usuarios)

# Agregar un nuevo usuario
@usuariosadm_bp.route('/usuariosadm/agregar', methods=['POST'])
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
    return redirect(url_for('usuariosadm.usuarios'))

# Editar un usuario existente
@usuariosadm_bp.route('/usuariosadm/editar/<int:id>', methods=['POST'])
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
    return redirect(url_for('usuariosadm.usuarios'))

# Eliminar un usuario
@usuariosadm_bp.route('/usuariosadm/eliminar/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    mysql.connection.commit()
    flash('Usuario eliminado correctamente')
    return redirect(url_for('usuariosadm.usuarios'))
