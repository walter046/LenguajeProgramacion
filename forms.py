from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError

# Formulario para registro
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

# Formulario para login
class LoginForm(FlaskForm):
    username = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")