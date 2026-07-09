import pyodbc

SERVER = "localhost"
DATABASE = "Tienda_Total_Sport"

UMBRAL_STOCK_CRITICO = 15


def get_connection():
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    conn = pyodbc.connect(conn_str)
    # Los datos de prueba se cargaron como UTF-8 crudo en columnas VARCHAR.
    # Le indicamos a pyodbc que decodifique/codifique el texto como UTF-8 para
    # que los acentos y la ñ se muestren correctamente (Almacén, Estándar, etc.).
    conn.setdecoding(pyodbc.SQL_CHAR, encoding="utf-8")
    conn.setdecoding(pyodbc.SQL_WCHAR, encoding="utf-8")
    conn.setencoding(encoding="utf-8")
    return conn


def query(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        columns = [c[0] for c in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]
        return rows
    finally:
        conn.close()


def execute(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
    finally:
        conn.close()
