from flask import Flask
from flask import render_template
from flaskext.mysql import MySQL

app = Flask(__name__)

mysql = MySQL()
app.config['MySQL_DATABASE_HOST'] = 'localhost'
app.config['MySQL_DATABASE_USER'] = 'root'
app.config['MySQL_DATABASE_PASSWORD'] = ''
app.config['MySQL_DATABASE_DB'] = 'zapatillas'
mysql.init_app(app)

@app.route('/')
def index():
    return render_template('/index.html')

if __name__ == '__main__':
    app.run(debug = True)