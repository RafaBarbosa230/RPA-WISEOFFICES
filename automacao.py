import subprocess
import sys
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import os
from datetime import datetime, timedelta
from PIL import Image, ImageTk
from datetime import datetime



def pedir_credenciais_custom():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    ico_path = os.path.join(base_path, "favicon.ico")

    root = tk.Tk()
    root.withdraw()

    
    login_win = tk.Toplevel()
    login_win.title("Login WiseBot")
    login_win.iconbitmap(ico_path)
    login_win.geometry("350x220")
    login_win.configure(bg="#F4F4F9")
    login_win.resizable(False, False)

    entry_style = {"font": ("Segoe UI", 11), "relief": tk.FLAT, "bg": "#FFFFFF", "fg": "#1D3557", "bd": 1}

    
    tk.Label(login_win, text="Email:", bg="#F4F4F9", fg="#1D3557", font=("Segoe UI", 12, "bold")).pack(pady=(20, 5))
    email_entry = tk.Entry(login_win, width=30, **entry_style)
    email_entry.pack(pady=5, padx=20)

    tk.Label(login_win, text="Senha:", bg="#F4F4F9", fg="#1D3557", font=("Segoe UI", 12, "bold")).pack(pady=5)
    senha_entry = tk.Entry(login_win, width=30, show="*", **entry_style)
    senha_entry.pack(pady=5, padx=20)

    
    btn_entrar = tk.Button(
        login_win, 
        text="Entrar", 
        command=lambda: salvar_e_sair(email_entry, senha_entry, login_win, root),
        bg="#0077B6",
        fg="#FFFFFF",
        activebackground="#005792",
        activeforeground="#FFFFFF",
        font=("Segoe UI", 11, "bold"),
        relief=tk.FLAT,
        bd=0,
        padx=20,
        pady=10,
        width=20
    )
    btn_entrar.pack(pady=(15, 20))

    login_win.mainloop()


def salvar_e_sair(email_entry, senha_entry, login_win, root):
    email = email_entry.get()
    senha = senha_entry.get()
    if not email or not senha:
        messagebox.showerror("Erro", "Preencha ambos os campos.", parent=login_win)
        return
    with open(".env", "w") as f:
        f.write(f"WISE_EMAIL={email}\nWISE_SENHA={senha}")
    messagebox.showinfo("Sucesso", "Credenciais salvas!", parent=login_win)
    login_win.destroy()
    root.destroy()




env_path = Path(".env")
if not env_path.exists() or not os.getenv("WISE_EMAIL") or not os.getenv("WISE_SENHA"):
    pedir_credenciais_custom()


load_dotenv()
email = os.getenv("WISE_EMAIL")
senha = os.getenv("WISE_SENHA")

if not email or not senha:
    raise ValueError("Email ou senha não encontrados no arquivo .env")


# Configurações do WebDriver
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
navegador = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def fazer_login():
    try:
        navegador.get("https://id.wiseoffices.com.br/realms/wiseoffices/protocol/openid-connect/auth?client_id=wiseoffices&redirect_uri=https%3A%2F%2Fapp.wiseoffices.com.br%2Fdeimos%2Fcallback&response_type=code&scope=openid+profile+email")
        navegador.maximize_window()

        campo_email = WebDriverWait(navegador, 10).until(EC.presence_of_element_located((By.ID, "username")))
        campo_email.send_keys(email)

        campo_continuar = WebDriverWait(navegador, 10).until(EC.element_to_be_clickable((By.ID, "kc-login")))
        campo_continuar.click()

        input_senha = WebDriverWait(navegador, 10).until(EC.presence_of_element_located((By.ID, "password")))
        input_senha.send_keys(senha)

        campo_continuar_dois = WebDriverWait(navegador, 10).until(EC.element_to_be_clickable((By.NAME, "login")))
        campo_continuar_dois.click()

        WebDriverWait(navegador, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "styles__ComplementsSelectBox-sc-1qitxh9-1"))
        )
        print('✅ Logado com sucesso')

        cookies = navegador.get_cookies()
        with open("cookies.json", "w") as f:
            json.dump(cookies, f)
        print("✅ Cookies salvos em cookies.json")

    except Exception as e:
        print(f"❌ Erro ao fazer login: {e}")
        navegador.quit()
        sys.exit(1)


CADEIRAS_IDS = {
    "Cabine 2": "7638",
    "Sala de entrevista": "7623",
    "Sala 2": "7632",
    "Sala 1": "7630",
    "Cabine 1": "7637"
}


def carregar_cookies():
    try:
        with open("cookies.json", "r") as f:
            cookies = json.load(f)
        return {cookie["name"]: cookie["value"] for cookie in cookies}
    except FileNotFoundError:
        print("❌ Arquivo cookies.json não encontrado. Faça login primeiro.")
        return None


def enviar_reserva(cadeira_id, data, horario_inicio, horario_fim, cookies):
    url = f"https://app.wiseoffices.com.br/api/v1/u/reservas/imoveis/3153/recursos/{cadeira_id}"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://app.wiseoffices.com.br",
        "Referer": "https://app.wiseoffices.com.br/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }

    payload = {
        "idsUsuariosConvidados": [37859],
        "visitantes": [],
        "dataInicio": f"{data} {horario_inicio}",
        "dataFim": f"{data} {horario_fim}",
        "descricao": None,
        "idUsuarioRepresentado": None,
        "tituloReuniao": None,
        "agora": False
    }

    try:
        response = requests.post(url, json=payload, headers=headers, cookies=cookies, timeout=10)
        if response.status_code == 201:
            print(f"✅ Reserva criada com sucesso para {data}!")
            return True
        else:
            print(f"❌ Falha ao criar reserva para {data}: {response.status_code}")
            print(response.text)
            return False
    except requests.RequestException as e:
        print(f"❌ Erro de conexão para {data}: {e}")
        return False




def selecionar_data(entry):
     calendario_win = tk.Toplevel()
     calendario_win.title("Selecionar Data")
     calendario_win.geometry("320x350")
     calendario_win.configure(bg="#F4F4F9")

     cal = Calendar(
        calendario_win, 
        selectmode="day", 
        date_pattern="yyyy-mm-dd", 
        locale="pt_BR", 
        background="#F4F4F9", 
        foreground="#0077B6", 
        headersbackground="#A8DADC",
        headersforeground="#1D3557",
        normalbackground="#FFFFFF",
        normalforeground="#1D3557",
        weekendbackground="#F4F4F9",
        weekendforeground="#1D3557",
        selectbackground="#0077B6",
        selectforeground="#FFFFFF"
    )
     cal.pack(pady=20)

     btn_confirmar = tk.Button(
        calendario_win, 
        text="Confirmar", 
        command=lambda: (entry.delete(0, tk.END), entry.insert(0, cal.get_date()), calendario_win.destroy()),
        bg="#0077B6",
        fg="#FFFFFF",
        activebackground="#005792",
        activeforeground="#FFFFFF",
        font=("Segoe UI", 12, "bold"),
        relief=tk.FLAT,
        bd=0,
        padx=10,
        pady=5
    )
     btn_confirmar.pack(pady=10)

     calendario_win.mainloop()


def filtrar_datas(data_inicio, data_fim, dias_selecionados):
    dias_semana_map = {
        "Segunda": 0,
        "Terça": 1,
        "Quarta": 2,
        "Quinta": 3,
        "Sexta": 4
    }
    dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
    dt_fim = datetime.strptime(data_fim, "%Y-%m-%d")
    datas_filtradas = []
    dia_atual = dt_inicio
    while dia_atual <= dt_fim:
        if dia_atual.weekday() in [dias_semana_map[dia] for dia in dias_selecionados if dias_selecionados[dia].get()]:
            datas_filtradas.append(dia_atual.strftime("%Y-%m-%d"))
        dia_atual += timedelta(days=1)
    return datas_filtradas



def abrir_interface():
    global root, cadeira_var, data_inicio_var, data_termino_var, dias_var, horario_inicio_var, horario_fim_var

       # Criação da interface principal
    root = tk.Tk()
    root.title("WiseBot")
    root.configure(bg="#F4F4F9")
    root.resizable(False, False)

    # Centralização da janela
    window_width = 450
    window_height = 650
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width - window_width) / 2)
    y = int((screen_height - window_height) / 2) - 50
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Carregar a logo e redimensionar
    logo_path = "logo.png"
    logo_img = Image.open(logo_path)
    logo_img = logo_img.resize((40, 40), Image.LANCZOS)
    logo_tk = ImageTk.PhotoImage(logo_img)

    # Frame para o título com logo centralizado
    titulo_frame = tk.Frame(root, bg="#0077B6")
    titulo_frame.pack(fill=tk.X, pady=(10, 20))

    # Conteúdo centralizado
    titulo_container = tk.Frame(titulo_frame, bg="#0077B6")
    titulo_container.pack(anchor=tk.CENTER)

    # Texto do título
    titulo_label = tk.Label(
        titulo_container, 
        text="WiseBot", 
        bg="#0077B6", 
        fg="#FFFFFF", 
        font=("Segoe UI", 18, "bold")
    )
    titulo_label.pack(side=tk.LEFT, padx=5)

    # Logo
    logo_label = tk.Label(titulo_container, image=logo_tk, bg="#0077B6")
    logo_label.image = logo_tk  # Para evitar que o garbage collector remova a imagem
    logo_label.pack(side=tk.LEFT, padx=5)

    # Cadeira
    tk.Label(root, text="Cadeira:", bg="#F4F4F9", fg="#1D3557", font=("Segoe UI", 11)).pack(pady=5)
    cadeira_var = tk.StringVar(value=list(CADEIRAS_IDS.keys())[0])
    cadeira_menu = ttk.Combobox(root, textvariable=cadeira_var, values=list(CADEIRAS_IDS.keys()), state="readonly", width=28)
    cadeira_menu.pack(pady=5)

    # Data de Início
    tk.Label(root, text="Data de Início:", bg="#F4F4F9", fg="#1D3557", font=("Segoe UI", 11)).pack(pady=5)
    data_inicio_var = tk.Entry(root, width=28, font=("Segoe UI", 10))
    data_inicio_var.pack(pady=5)
    tk.Button(
        root, 
        text="Selecionar Data de Início", 
        command=lambda: selecionar_data(data_inicio_var),
        bg="#0077B6",
        fg="#FFFFFF",
        activebackground="#005792",
        activeforeground="#FFFFFF",
        font=("Segoe UI", 10, "bold"),
        relief=tk.FLAT,
        bd=0,
        padx=8,
        pady=5,
        width=24
    ).pack(pady=5)

    # Data de Término
    tk.Label(root, text="Data de Término:", bg="#F4F4F9", fg="#1D3557", font=("Segoe UI", 11)).pack(pady=5)
    data_termino_var = tk.Entry(root, width=28, font=("Segoe UI", 10))
    data_termino_var.pack(pady=5)
    tk.Button(
        root, 
        text="Selecionar Data de Término", 
        command=lambda: selecionar_data(data_termino_var),
        bg="#0077B6",
        fg="#FFFFFF",
        activebackground="#005792",
        activeforeground="#FFFFFF",
        font=("Segoe UI", 10, "bold"),
        relief=tk.FLAT,
        bd=0,
        padx=8,
        pady=5,
        width=24
    ).pack(pady=5)

    # Repetir Semanalmente
    tk.Label(root, text="Repetir Semanalmente:", bg="#F4F4F9", fg="#1D3557", font=("Segoe UI", 11)).pack(pady=10)
    dias_var = {}
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    dias_frame = tk.Frame(root, bg="#F4F4F9")
    dias_frame.pack(pady=5)
    for dia in dias:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(
            dias_frame, 
            text=dia, 
            variable=var,
            bg="#A8DADC",
            fg="#1D3557",
            activebackground="#A8DADC",
            activeforeground="#1D3557",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=3,
            pady=2,
            width=8
        )
        chk.pack(side=tk.LEFT, padx=2)
        dias_var[dia] = var

    # Horário de Início
    tk.Label(root, text="Horário de Início:", bg="#F4F4F9", fg="#1D3557", font=("Segoe UI", 11)).pack(pady=5)
    horarios = [f"{h:02d}:{m:02d}" for h in range(7, 19) for m in (0, 30)]
    horario_inicio_var = ttk.Combobox(root, values=horarios, width=28)
    horario_inicio_var.set("07:30")
    horario_inicio_var.pack(pady=5)

    # Horário de Fim
    tk.Label(root, text="Horário de Fim:", bg="#F4F4F9", fg="#1D3557", font=("Segoe UI", 11)).pack(pady=5)
    horario_fim_var = ttk.Combobox(root, values=horarios, width=28)
    horario_fim_var.set("19:00")
    horario_fim_var.pack(pady=5)

    # Botão de confirmação
    tk.Button(
        root, 
        text="Confirmar Reserva", 
        command=confirmar_reserva,
        bg="#0077B6",
        fg="#FFFFFF",
        activebackground="#005792",
        activeforeground="#FFFFFF",
        font=("Segoe UI", 11, "bold"),
        relief=tk.FLAT,
        bd=0,
        padx=10,
        pady=10,
        width=28
    ).pack(pady=20)

    root.mainloop()


def confirmar_reserva():
    cadeira_id = CADEIRAS_IDS[cadeira_var.get()]
    data_inicio = data_inicio_var.get()
    data_fim = data_termino_var.get()
    horario_inicio = horario_inicio_var.get()
    horario_fim = horario_fim_var.get()

    # Gera as datas com base nos dias selecionados
    datas = filtrar_datas(data_inicio, data_fim, dias_var)

    # Verifica se todos os campos estão preenchidos
    if not datas or not cadeira_id or not horario_inicio or not horario_fim:
        messagebox.showerror("Erro", "Preencha todos os campos corretamente.")
        return

    # Carrega os cookies uma vez
    cookies = carregar_cookies()
    if not cookies:
        messagebox.showerror("Erro", "Não foi possível carregar os cookies.")
        return

    # Lista para armazenar datas que falharam
    datas_falhadas = []

    # Envia uma requisição para cada data
    for data in datas:
        if not enviar_reserva(cadeira_id, data, horario_inicio, horario_fim, cookies):
            datas_falhadas.append(data)

    # Mensagem de sucesso (sempre aparece primeiro)
    messagebox.showinfo("Sucesso", "Reservas concluídas! ✅")

    # Exibe as datas que falharam, se houver alguma
    if datas_falhadas:
        messagebox.showerror(
            "Erro nas Reservas",
            f"Não foi possível criar reservas para as seguintes datas:\n{', '.join(datas_falhadas)}"
        )







def main():
    try:
        fazer_login()
        abrir_interface()
    except Exception as e:
        print(f"❌ Erro no fluxo principal: {e}")
    finally:
        navegador.quit()


if __name__ == "__main__":
    main()