import bcrypt

class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self._password_hash = self._hash_password(password)

    def _hash_password(self, password) -> bytes:
        """Retorna la contraseña hasheada con bcrypt."""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt)

    def check_password(self, password):
        """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
        return bcrypt.checkpw(password.encode('utf-8'), self._password_hash)
