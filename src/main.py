import flet as ft
import sqlite3
import os

# Caminho do banco de dados na mesma pasta do script
DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

# ==================== BANCO DE DADOS (SQLite3) ====================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Criação das tabelas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    
    # Verifica especificamente se o usuário 'admin' existe. Se não existir, insere.
    cursor.execute("SELECT * FROM system_users WHERE username = 'admin'")
    if cursor.fetchone() is None:
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


# ==================== INTERFACE (Flet App) ====================
def main(page: ft.Page):
    page.title = "App Mobile - Flet"
    page.window_width = 390
    page.window_height = 844
    page.window_resizable = False
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # Força a inicialização e inserção do usuário padrão no SQLite
    init_db()

    # --- FUNÇÃO DA TELA DE LOGIN ---
    def mostrar_tela_login():
        page.controls.clear()
        
        user_input = ft.TextField(label="Usuário", border_radius=10, value="admin")
        pass_input = ft.TextField(label="Senha", password=True, can_reveal_password=True, border_radius=10, value="admin123")
        error_message = ft.Text(value="", color=ft.Colors.RED, size=13, weight=ft.FontWeight.W_500)

        def handle_login(e):
            if not user_input.value or not pass_input.value:
                error_message.value = "Preencha todos os campos."
                page.update()
                return
            if verify_login(user_input.value, pass_input.value):
                mostrar_tela_cadastro()
            else:
                error_message.value = "Usuário ou senha incorretos!"
                page.update()

        page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("🔒", size=60),
                        ft.Text("Acesso ao Sistema", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                        ft.Text("Faça login para continuar", size=14, color=ft.Colors.GREY_600),
                        ft.Container(height=15), 
                        user_input,
                        pass_input,
                        error_message,
                        ft.Container(height=10),
                        ft.Button(
                            content=ft.Text("Entrar", color=ft.Colors.WHITE),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_600, padding=15, shape=ft.RoundedRectangleBorder(radius=10)
                            ),
                            width=340,
                            on_click=handle_login
                        ),
                        ft.Text("Dica: use admin / admin123", size=11, color=ft.Colors.GREY_400, italic=True)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12
                ),
                alignment=ft.Alignment.CENTER,
                expand=True
            )
        )

    # --- FUNÇÃO DA TELA DE CADASTRO ---
    def mostrar_tela_cadastro():
        page.controls.clear()

        name_input = ft.TextField(label="Nome Completo", border_radius=10)
        email_input = ft.TextField(label="E-mail", border_radius=10)
        status_message = ft.Text(value="", size=13, weight=ft.FontWeight.W_500)
        contacts_list = ft.ListView(expand=True, spacing=10, padding=10)

        def refresh_list():
            contacts_list.controls.clear()
            records = get_all_contacts()
            if not records:
                contacts_list.controls.append(
                    ft.Text("Nenhum cadastro realizado.", color=ft.Colors.GREY_500, italic=True, text_align=ft.TextAlign.CENTER)
                )
            for name, email in records:
                contacts_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text("👤", size=20),
                                ft.Column(
                                    controls=[
                                        ft.Text(name, weight=ft.FontWeight.BOLD, size=14),
                                        ft.Text(email, size=12, color=ft.Colors.GREY_600)
                                    ],
                                    spacing=2
                                )
                            ],
                            spacing=10
                        ),
                        bgcolor=ft.Colors.GREY_100,
                        padding=10,
                        border_radius=8
                    )
                )
            page.update()

        def handle_register(e):
            if not name_input.value or not email_input.value:
                status_message.value = "Preencha Nome e E-mail!"
                status_message.color = ft.Colors.RED
                page.update()
                return
            if insert_contact(name_input.value, email_input.value):
                status_message.value = "Cadastro realizado com sucesso!"
                status_message.color = ft.Colors.GREEN
                name_input.value = ""
                email_input.value = ""
                refresh_list()
            else:
                status_message.value = "Erro ao salvar no banco."
                status_message.color = ft.Colors.RED
                page.update()

        def handle_logout(e):
            mostrar_tela_login()

        refresh_list()

        page.add(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Cadastro", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                            ft.TextButton(content=ft.Text("Sair 🚪"), on_click=handle_logout)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(height=20),
                    name_input,
                    ft.Container(height=5),
                    email_input,
                    status_message,
                    ft.Container(height=5),
                    # ft.Button(
                    #     content=ft.Text("Salvar Registro", color=ft.Colors.WHITE),
                    #     style=ft.ButtonStyle(
                    #         bgcolor=ft.Colors.GREEN_600, padding=15, shape=ft.RoundedRectangleBorder(radius=10)
                    #     ),
                    #     width=340,
                    #     on_click=handle_register
                    # ),
                    ft.Button(
                        content=ft.Row(
                            controls=[
                                ft.Image(
                                    src="add.png", 
                                    width=20, 
                                    height=20, 
                                    fit="contain"
                                ),
                                ft.Text("Salvar Registro", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.GREEN_600, 
                            padding=15, 
                            shape=ft.RoundedRectangleBorder(radius=10)
                        ),
                        width=340,
                        on_click=handle_register
                    ),




                    ft.Divider(height=30),
                    ft.Text("Registros Salvos:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                    # CORREÇÃO AQUI: Alterado de ft.border.all para ft.Border.all()
                    ft.Container(
                        content=contacts_list,
                        expand=True,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=10,
                        padding=5
                    )
                ],
                expand=True
            )
        )

    mostrar_tela_login()

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
