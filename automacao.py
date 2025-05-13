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


# Função para pedir credenciais e criar o arquivo .env se necessário
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
    login_win.geometry("300x150")
    login_win.resizable(False, False)

    tk.Label(login_win, text="Email:").pack(pady=5)
    email_entry = tk.Entry(login_win, width=30)
    email_entry.pack()

    tk.Label(login_win, text="Senha:").pack(pady=5)
    senha_entry = tk.Entry(login_win, width=30, show='*')
    senha_entry.pack()

    def salvar_e_sair():
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

    tk.Button(login_win, text="Entrar", command=salvar_e_sair).pack(pady=10)

    login_win.mainloop()


# Verificar se o .env existe, caso contrário pedir credenciais
env_path = Path(".env")
if not env_path.exists() or not os.getenv("WISE_EMAIL") or not os.getenv("WISE_SENHA"):
    pedir_credenciais_custom()


# Carregar as credenciais do .env
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

        # Captura dos cookies após o login bem-sucedido
        cookies = navegador.get_cookies()
        with open("cookies.json", "w") as f:
            json.dump(cookies, f)
        print("✅ Cookies salvos em cookies.json")

    except Exception as e:
        print(f"❌ Erro ao fazer login: {e}")
        navegador.quit()
        sys.exit(1)


# IDs das cadeiras disponíveis
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


def enviar_reserva(cadeira_id, data, horario_inicio, horario_fim):
    url = f"https://app.wiseoffices.com.br/api/v1/u/reservas/imoveis/3153/recursos/{cadeira_id}"
    cookies = carregar_cookies()
    if not cookies:
        return
    
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

    response = requests.post(url, json=payload, headers=headers, cookies=cookies)

    if response.status_code == 201:
        print(f"✅ Reserva criada com sucesso para {data}!")
    else:
        print(f"❌ Falha ao criar reserva para {data}: {response.status_code}")
        print(response.text)
        messagebox.showerror("Erro", f"Falha ao criar reserva para {data}: {response.status_code}")



def selecionar_data(entry):
    calendario_win = tk.Toplevel()
    calendario_win.title("Selecionar Data")
    calendario_win.geometry("300x300")

    cal = Calendar(calendario_win, selectmode="day", date_pattern="yyyy-mm-dd", locale="pt_BR")
    cal.pack(pady=20)

    tk.Button(calendario_win, text="Confirmar", command=lambda: (entry.delete(0, tk.END), entry.insert(0, cal.get_date()), calendario_win.destroy())).pack(pady=10)


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
    root.geometry("450x700")
    root.resizable(False, False)

    # Cadeira
    tk.Label(root, text="Cadeira:").pack(pady=5)
    cadeira_var = tk.StringVar(value=list(CADEIRAS_IDS.keys())[0])
    cadeira_menu = ttk.Combobox(root, textvariable=cadeira_var, values=list(CADEIRAS_IDS.keys()), state="readonly", width=30)
    cadeira_menu.pack()

    # Data de Início
    tk.Label(root, text="Data de Início:").pack(pady=5)
    data_inicio_var = tk.Entry(root, width=30)
    data_inicio_var.pack(pady=5)
    tk.Button(root, text="Selecionar Data de Início", command=lambda: selecionar_data(data_inicio_var)).pack(pady=5)

    # Data de Término
    tk.Label(root, text="Data de Término:").pack(pady=5)
    data_termino_var = tk.Entry(root, width=30)
    data_termino_var.pack(pady=5)
    tk.Button(root, text="Selecionar Data de Término", command=lambda: selecionar_data(data_termino_var)).pack(pady=5)

    # Repetir Semanalmente
    tk.Label(root, text="Repetir semanalmente a cada:").pack(pady=5)
    dias_var = {}
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    dias_frame = tk.Frame(root)
    dias_frame.pack(pady=5)
    for dia in dias:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(dias_frame, text=dia, variable=var)
        chk.pack(side=tk.LEFT, padx=5)
        dias_var[dia] = var

    # Horário de Início
    tk.Label(root, text="Horário de Início:").pack(pady=5)
    horarios = [f"{h:02d}:{m:02d}" for h in range(7, 19) for m in (0, 30)]
    horario_inicio_var = ttk.Combobox(root, values=horarios, width=30)
    horario_inicio_var.set("07:30")
    horario_inicio_var.pack()

    # Horário de Fim
    tk.Label(root, text="Horário de Fim:").pack(pady=5)
    horario_fim_var = ttk.Combobox(root, values=horarios, width=30)
    horario_fim_var.set("19:00")
    horario_fim_var.pack()

    # Botão de confirmação
    tk.Button(root, text="Confirmar Reserva", command=confirmar_reserva).pack(pady=20)

    # Inicia o loop principal do Tkinter
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

    # Envia uma requisição para cada data
    for data in datas:
        enviar_reserva(cadeira_id, data, horario_inicio, horario_fim)





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
