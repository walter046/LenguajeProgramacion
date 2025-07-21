from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import mysql
from datetime import datetime

carrito_bp = Blueprint('carritoadm', __name__)

@carrito_bp.route('/carritoadm')
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
    return render_template('carritoadm.html', carrito=carrito)

@carrito_bp.route('/carritoadm/agregar', methods=['POST'])
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
    return redirect(url_for('carritoadm.ver_carrito'))

@carrito_bp.route('/carritoadm/editar/<int:id>', methods=['POST'])
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
    return redirect(url_for('carritoadm.ver_carrito'))

@carrito_bp.route('/carritoadm/eliminar/<int:id>', methods=['POST'])
def eliminar_carrito(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM carrito WHERE id = %s", (id,))
    mysql.connection.commit()
    flash('Producto eliminado del carrito')
    return redirect(url_for('carritoadm.ver_carrito'))
