from .entities.User import User

class ModelUser():
    
    @classmethod
    def login(self, db, user):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, nombre, username, password, direccion, telefono, fecha_registro FROM usuarios WHERE username = '{}'""".format(user.username)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                user = User(row[0], row[1], row[2], User.check_password(row[2], user.password), row[4], row[5], row[6])
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)