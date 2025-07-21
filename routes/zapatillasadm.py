from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import mysql

zapatillas_adm_bp = Blueprint('zapatillas_adm', __name__)

@zapatillas_adm_bp.route('/zapatillasadm')
def listar_zapatillas():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM zapatillas")
    zapatillas = cursor.fetchall()
    return render_template('zapatillasadm.html', zapatillas=zapatillas)

@zapatillas_adm_bp.route('/zapatillasadm/agregar', methods=['POST'])
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
    return redirect(url_for('zapatillas_adm.listar_zapatillas'))

@zapatillas_adm_bp.route('/zapatillasadm/editar/<int:id>', methods=['POST'])
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
    return redirect(url_for('zapatillas_adm.listar_zapatillas'))

@zapatillas_adm_bp.route('/zapatillasadm/eliminar/<int:id>', methods=['POST'])
def eliminar_zapatilla(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM zapatillas WHERE id = %s", (id,))
    mysql.connection.commit()
    flash('Zapatilla eliminada correctamente', 'success')
    return redirect(url_for('zapatillas_adm.listar_zapatillas'))
