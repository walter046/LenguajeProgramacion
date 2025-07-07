from flask import Flask, render_template, redirect, url_for, session, flash, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tienda_zapatillas'
app.secret_key = '48dfa2e08c42b1fa67f5f6ffbcba98b73febe6972123259da3759a84c304b1f5'

mysql = MySQL(app)

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
        
        # Database
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (nombre, username, password, direccion, telefono, rol) VALUES (%s, %s, %s, %s, %s)", 
                           (nombre, username, hashed_password, direccion, telefono, 'USER'))
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
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, nombre, password FROM usuarios WHERE username=%s", (username,))
        usuario = cursor.fetchone()
        cursor.close()
        
        if usuario and bcrypt.checkpw(password.encode('utf-8'), usuario[2].encode('utf-8')):
            session['usuario_id'] = usuario[0]
            session['usuario_nombre'] = usuario[1] # Guardar el nombre en la sesión
            flash(f"Bienvenido, {usuario[1]}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Inicio de sesión fallido. Revisa tus datos ingresados!", "error")
            # No redirigir, para que el usuario pueda corregir en el mismo formulario
            
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
                'id': usuario[0],
                'nombre': usuario[1],
                'username': usuario[2],
                'direccion': usuario[3],
                'telefono': usuario[4]
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
    # Puedes renderizar una plantilla de productos o solo un mensaje de prueba
    return render_template('products.html')

# Manejador de errores
@app.errorhandler(404)
def not_found(error):
    flash("Página no encontrada.", "error")
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    flash("Error interno del servidor. Por favor intenta nuevamente.", "error")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
