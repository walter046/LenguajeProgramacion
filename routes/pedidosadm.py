from flask import Blueprint, render_template, request, redirect, url_for
from extensions import mysql

pedidosadm_bp = Blueprint('pedidosadm', __name__)

@pedidosadm_bp.route('/pedidosadm')
def listar_pedidos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM pedidos")
    pedidos = cursor.fetchall()
    return render_template('pedidosadm.html', pedidos=pedidos)

@pedidosadm_bp.route('/pedidosadm/eliminar/<int:id>')
def eliminar_pedido(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM pedidos WHERE id = %s", (id,))
    mysql.connection.commit()
    return redirect(url_for('pedidosadm.listar_pedidos'))

@pedidosadm_bp.route('/pedidosadm/editar/<int:id>', methods=['GET', 'POST'])
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
        return redirect(url_for('pedidosadm.listar_pedidos'))
    
    cursor.execute("SELECT * FROM pedidos WHERE id = %s", (id,))
    pedido = cursor.fetchone()
    return render_template('editar_pedidoadm.html', pedido=pedido)

@pedidosadm_bp.route('/pedidosadm/agregar', methods=['GET', 'POST'])
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
        return redirect(url_for('pedidosadm.listar_pedidos'))
    
    return render_template('agregar_pedidoadm.html')
