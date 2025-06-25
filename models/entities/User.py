from werkzeug.security import check_password_hash, generate_password_hash

class User():
    
    def __init__(self, id, nombre, username, password, direccion, telefono, fecha_registro) -> None:
        self.id = id
        self.nombre = nombre
        self.username = username
        self.password = password
        self.direccion = direccion
        self.telefono = telefono
        self.fecha_registro = fecha_registro
    
    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)
    
print(generate_password_hash("julian999"))