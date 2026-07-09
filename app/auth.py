import hashlib
import secrets


def generar_salt():
    return secrets.token_hex(16)  # 32 caracteres hexadecimales


def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def verificar_password(password, salt, password_hash):
    return hash_password(password, salt) == password_hash
