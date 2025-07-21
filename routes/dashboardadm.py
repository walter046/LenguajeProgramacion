from flask import Blueprint, render_template
from extensions import mysql

admin_dashboard_bp = Blueprint('admin_dashboard', __name__)

@admin_dashboard_bp.route('/dashboardadm')
def dashboard_admin():
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
    total_usuarios = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM pedidos")
    total_pedidos = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM zapatillas")
    total_zapatillas = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM carrito")
    total_carritos = cursor.fetchone()['total']


    return render_template(
        'dashboardadm.html',
        total_usuarios=total_usuarios,
        total_pedidos=total_pedidos,
        total_zapatillas=total_zapatillas,
        total_carritos=total_carritos
    )
