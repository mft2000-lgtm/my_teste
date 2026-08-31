import sqlite3
import os

# Define o caminho do banco de dados junto ao script
DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de controle de acessos (Login)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    # Tabela para salvar os cadastros do formulário (Nome e E-mail)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    
    # Insere um usuário de testes caso a tabela esteja limpa
    cursor.execute("SELECT COUNT(*) FROM system_users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO system_users (username, password) VALUES (?, ?)", ("admin", "admin123"))
        
    conn.commit()
    conn.close()

def verify_login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM system_users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def insert_contact(name, email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO contacts (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        success = True
    except Exception:
        success = False
    finally:
        conn.close()
    return success

def get_all_contacts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, email FROM contacts ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
