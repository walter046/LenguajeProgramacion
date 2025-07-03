from flask import Flask, render_template, redirect, url_for, session, flash
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
    nombre = StringField("Nombre", validators = [DataRequired()])
    username = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    direccion = StringField("Direccion", validators = [DataRequired()])
    telefono = StringField("Telefono", validators = [DataRequired()])
    submit = SubmitField("Register")
    
    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username=%s", (field.data))
        usuario = cursor.fetchone()
        cursor.close()
        if usuario:
            raise ValidationError('El email esta en uso!')
        
class LoginForm(FlaskForm):
    username = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    submit = SubmitField("Login")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods = ['GET', 'POST'])
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
        cursor.execute("INSERT INTO usuarios (nombre, username, password, direccion, telefono) VALUES (%s, %s, %s, %s, %s)", (nombre, username, hashed_password, direccion, telefono))
        mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('login'))
        
    return render_template('auth/register.html', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username=%s", (username,))
        usuario = cursor.fetchone()
        cursor.close()
        if usuario and bcrypt.checkpw(password.encode('utf-8'), usuario[3].encode('utf-8')):
            session['usuario_id'] = usuario[0]
            return redirect(url_for('dashboard'))
        else:
            flash("Inicio de sesión fallido. Revisa tus datos ingresados!")
            return redirect(url_for('login'))
        
    return render_template('auth/login.html', form = form)

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' in session:
        usuario_id = session['usuario_id']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id=%s", (usuario_id,))
        usuario = cursor.fetchone()
        cursor.close()
        
        if usuario:
            return render_template('dashboard.html', usuario = usuario)
        
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash("Cerraste sesión correctamente!")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug = True)