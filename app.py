from flask import Flask, render_template, redirect, url_for, session, flash, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
from flask_mysqldb import MySQL
from flask_limiter import Limiter
from datetime import timedelta



app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'karjoel'
app.config['MYSQL_DB'] = 'tienda_zapatillas'
app.secret_key = '48dfa2e08c42b1fa67f5f6ffbcba98b73febe6972123259da3759a84c304b1f5'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Configuración adicional para sesiones
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

mysql = MySQL(app)


# Inicialización de Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(
    app=app,
    key_func=get_remote_address, # Usa la IP remota para limitar
    storage_uri="memory://",     # Almacenamiento en memoria para desarrollo
)


class RegisterForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    username = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    direccion = StringField("Direccion", validators=[DataRequired()])
    telefono = StringField("Telefono", validators=[DataRequired()])
    submit = SubmitField("Register")
    
    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username=%s", (field.data,))
        usuario = cursor.fetchone()
        cursor.close()
        if usuario:
            raise ValidationError('El email ya está en uso. Por favor, elige otro.')
        
class LoginForm(FlaskForm):
    username = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register(): 
    form = RegisterForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        username = form.username.data
        password = form.password.data
        direccion = form.direccion.data
        telefono = form.telefono.data
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        rol = 'USER'  # Rol por defecto para nuevos usuarios
        
        # Database
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (nombre, username, password, direccion, telefono, rol) VALUES (%s, %s, %s, %s, %s, %s)", 
                           (nombre, username, hashed_password, direccion, telefono, rol))
            mysql.connection.commit()
            flash("Cuenta creada exitosamente! Ya puedes iniciar sesión.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al registrar: {e}", "error")
            print(f"Error al registrar usuario: {e}")
        finally:
            cursor.close()
            
    return render_template('auth/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("15 per minute")  # Máximo 15 intentos por minuto
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        try:
            username = form.username.data.strip()
            password = form.password.data
            
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT id, nombre, password FROM usuarios WHERE username = %s", (username,))
            usuario = cursor.fetchone()
            cursor.close()
            
            if not usuario:
                flash("Usuario o contraseña incorrectos", "error")
                return render_template('auth/login.html', form=form)
            
            # Convertir ambas contraseñas a bytes
            hashed_password = usuario['password'].encode('utf-8')  # Acceder por el nombre de la columna
            input_password = password.encode('utf-8')

            if bcrypt.checkpw(input_password, hashed_password):
                session['usuario_id'] = usuario['id']    # Acceder por el nombre de la columna
                session['usuario_nombre'] = usuario['nombre']  # Acceder por el nombre de la columna
                session['usuario_username'] = username
                flash(f"Bienvenido, {usuario['nombre']}!", "success")
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash("Usuario o contraseña incorrectos", "error")
        
        except Exception as e:
            print(f"Error en login: {str(e)}")
            flash("Ocurrió un error durante el inicio de sesión", "error")
    
    return render_template('auth/login.html', form=form)


@app.route('/dashboard')
def dashboard():
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
            return redirect(url_for('login'))
            
    flash("Por favor inicia sesión para acceder.", "warning")
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    username = session.pop('usuario_nombre', 'Usuario') # Obtener y eliminar el nombre de la sesión
    session.pop('usuario_id', None)
    flash(f"Hasta luego, {username}! Cerraste sesión correctamente.", "info")
    return redirect(url_for('login'))

@app.route('/update_user', methods=['POST'])
def update_user():
    if 'usuario_id' not in session:
        flash("No tienes autorización para realizar esta acción.", "error")
        return redirect(url_for('login'))
    
    try:
        usuario_id = session['usuario_id']
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        direccion = request.form.get('direccion', '').strip()
        telefono = request.form.get('telefono', '').strip()
        
        # Validaciones básicas
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
        flash("Error al actualizar los datos. Por favor intenta nuevamente.", "error")
        print(f"Error updating user: {e}")
    
    return redirect(url_for('dashboard'))

@app.route('/delete_user')
def delete_user():
    if 'usuario_id' not in session:
        flash("No tienes autorización para realizar esta acción.", "error")
        return redirect(url_for('login'))
    
    try:
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
        flash("Error al eliminar la cuenta. Por favor intenta nuevamente.", "error")
        print(f"Error deleting user: {e}")
    
    return redirect(url_for('index'))

# Ruta para obtener información del usuario (API)
@app.route('/api/user_info')
def get_user_info():
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
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

@app.route('/category/<name>')
def category(name):
    # Puedes renderizar una plantilla específica para la categoría
    return render_template('category.html', category=name)

@app.route('/products')
def products():
    # pagina de productos su ruta
    return render_template('products.html')

@app.route('/novedades')
def novedades():

    cursor = mysql.connection.cursor()

    query = """
        SELECT
            z.id_zapatilla,
            z.nombre AS nombre_zapatilla,
            z.descripcion,
            z.precio AS precio,
            z.imagen,
            m.nombre AS nombre_marca
        FROM
            zapatillas z
        JOIN
            marcas m ON z.id_marca = m.id_marca;
    """
    
    cursor.execute(query)
    zapatillas = cursor.fetchall()
    cursor.close()
    
    return render_template('novedades.html', zapatillas=zapatillas)

@app.route('/ofertas')
def ofertas():
    return render_template('ofertas.html')

@app.route('/carrito')
def carrito():
    # pagina de carrito su ruta
    return render_template('carrito.html')

# Manejador de errores
@app.errorhandler(404)
def not_found(error):
    flash("Página no encontrada.", "error")
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    flash("Error interno del servidor. Por favor intenta nuevamente.", "error")
    return redirect(url_for('index'))



#Aqui va ir la ruta de la api para guardar los pedidos de los clientes

@app.route('/agregarCarrito', methods=['POST'])
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

@app.route('/actualizarCarrito', methods=['POST'])
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

@app.route('/get_cart')
def get_cart():
    print("=== GET CART ===")
    print("Session actual:", dict(session))
    print("Carrito actual:", session.get('cart', {}))
    return jsonify({'cart': session.get('cart', {})})

@app.route('/debug_cart')
def debug_cart():
    print("=== DEBUG CART ===")
    print("Session completa:", dict(session))
    print("Carrito:", session.get('cart', {}))
    return jsonify({
        'session': dict(session),
        'cart': session.get('cart', {}),
        'cart_keys': list(session.get('cart', {}).keys())
    })

@app.route('/guardar_carrito', methods=['POST'])
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
        print(f"Error al guardar carrito: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/mis_pedidos')
def mis_pedidos():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para ver tus pedidos", "error")
        return redirect(url_for('login'))
    
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
        print(f"Error al obtener pedidos: {e}")
        flash("Error al cargar los pedidos", "error")
        return redirect(url_for('dashboard'))

@app.route('/crear_pedido', methods=['POST'])
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

@app.route('/cancelar_pedido/<int:pedido_id>', methods=['POST'])
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

@app.route('/guardar_carrito_actual', methods=['POST'])
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

@app.route('/clear_cart', methods=['POST'])
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

@app.route('/update_cart_item', methods=['POST'])
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


if __name__ == '__main__':
    app.run(debug=True)

