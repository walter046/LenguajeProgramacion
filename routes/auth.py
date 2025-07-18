from flask import Blueprint, redirect, url_for, session, flash, render_template, request
from forms import RegisterForm, LoginForm
from extensions import mysql
import bcrypt

auth_bp = Blueprint('auth', __name__)

# Ruta de registro
@auth_bp.route('/register', methods=['GET', 'POST'])
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
            # Insertar el nuevo usuario en la base de datos
            cursor.execute("INSERT INTO usuarios (nombre, username, password, direccion, telefono, rol) VALUES (%s, %s, %s, %s, %s, %s)", 
                           (nombre, username, hashed_password, direccion, telefono, rol))
            mysql.connection.commit()
            flash("Cuenta creada exitosamente! Ya puedes iniciar sesión.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            # Manejo de errores
            mysql.connection.rollback()
            flash(f"Error al registrar: {e}", "error")
            print(f"Error al registrar usuario: {e}")
        finally:
            cursor.close()
    
    # Renderizar el formulario de registro      
    return render_template('auth/register.html', form=form)

# Ruta de inicio de sesión
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        try:
            # Verificar las credenciales del usuario
            username = form.username.data.strip()
            password = form.password.data
            
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT id, nombre, rol, password FROM usuarios WHERE username = %s", (username,))
            usuario = cursor.fetchone()
            cursor.close()
            
            if not usuario:
                flash("Usuario o contraseña incorrectos", "error")
                return render_template('auth/login.html', form=form)
            
            # Convertir ambas contraseñas a bytes
            hashed_password = usuario['password'].encode('utf-8')
            input_password = password.encode('utf-8')

            if bcrypt.checkpw(input_password, hashed_password):
                session['usuario_id'] = usuario['id']
                session['usuario_nombre'] = usuario['nombre']
                session['usuario_username'] = username
                session['usuario_rol'] = usuario['rol']
                flash(f"Bienvenido, {usuario['nombre']}!", "success")
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('user.dashboard'))
            else:
                flash("Usuario o contraseña incorrectos", "error")
        
        except Exception as e:
            # Manejo de errores
            print(f"Error en login: {str(e)}")
            flash("Ocurrió un error durante el inicio de sesión", "error")
    
    # Renderizar el formulario de login
    return render_template('auth/login.html', form=form)

# Ruta de logout
@auth_bp.route('/logout')
def logout():
    if 'usuario_id' not in session:
        abort(401)  # No autorizado si no hay sesión activa
    username = session.pop('usuario_nombre', 'Usuario') # Obtener y eliminar el nombre de la sesión
    session.pop('usuario_id', None)
    flash(f"Hasta luego, {username}! Cerraste sesión correctamente.", "info")
    return redirect(url_for('auth.login'))