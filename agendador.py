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
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
from pathlib import Path
import schedule
import time
from datetime import datetime, timedelta
import threading




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

def obter_id_usuario(cookies):
    url = "https://app.wiseoffices.com.br/api/v1/me"
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
        
        # Retorna diretamente o ID do usuário
        return response.json().get("id")
        
    except requests.RequestException as e:
        print(f"❌ Erro ao obter ID do usuário: {e}")
        return None
    
def verificar_cookies_validos(cookies):
    url = "https://app.wiseoffices.com.br/api/v1/me"
    headers = {
        "accept": "*/*",
        "user-agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=5)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ Erro ao verificar cookies: {e}")
        return False


PREFERENCIAS_ARQUIVO = "preferencias.json"

def salvar_preferencias(cadeira, data_inicio, dias_semana, intervalo, horario_inicio, horario_fim):
    preferencias = {
        "cadeira": cadeira,
        "data_inicio": data_inicio,
        "dias_semana": dias_semana,
        "intervalo": intervalo,
        "horario_inicio": horario_inicio,
        "horario_fim": horario_fim
    }
    
    # Salva o JSON com acentos corretamente
    with open(PREFERENCIAS_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(preferencias, f, indent=4, ensure_ascii=False)
    
    messagebox.showinfo("Sucesso", "Preferências salvas com sucesso!")


def carregar_preferencias():
    try:
        with open(PREFERENCIAS_ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo de preferências não encontrado. Execute a configuração inicial.")
        return None


def enviar_reserva(cookies):
    # Carregar preferências do arquivo
    preferencias = carregar_preferencias()
    if not preferencias:
        print("❌ Não foi possível carregar as preferências.")
        return False

    cadeira_id = CADEIRAS_IDS.get(preferencias["cadeira"])
    horario_inicio = preferencias["horario_inicio"]
    horario_fim = preferencias["horario_fim"]
    dias_semana_permitidos = preferencias["dias_semana"]

    # Tradução dos dias da semana para português
    dias_semana_traduzidos = {
        "Monday": "Segunda",
        "Tuesday": "Terça",
        "Wednesday": "Quarta",
        "Thursday": "Quinta",
        "Friday": "Sexta",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }

    # Verifica para os próximos 7 dias
    hoje = datetime.now()
    for offset in range(7):
        data_reserva = hoje + timedelta(days=offset)
        nome_dia_reserva = data_reserva.strftime("%A")
        dia_reserva_pt = dias_semana_traduzidos.get(nome_dia_reserva, nome_dia_reserva)

        # Verifica se o dia é permitido
        if dia_reserva_pt not in dias_semana_permitidos:
            continue

        # Converte para o formato esperado
        data_reserva_str = data_reserva.strftime("%Y-%m-%d")

        user_id = obter_id_usuario(cookies)
        if not user_id:
            print("❌ ID do usuário não encontrado. Não é possível enviar a reserva.")
            return False

        url = f"https://app.wiseoffices.com.br/api/v1/u/reservas/imoveis/3153/recursos/{cadeira_id}"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://app.wiseoffices.com.br",
            "Referer": "https://app.wiseoffices.com.br/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }

        payload = {
            "idsUsuariosConvidados": [user_id],
            "visitantes": [],
            "dataInicio": f"{data_reserva_str} {horario_inicio}",
            "dataFim": f"{data_reserva_str} {horario_fim}",
            "descricao": None,
            "idUsuarioRepresentado": None,
            "tituloReuniao": None,
            "agora": False
        }

        try:
            print(f"📦 Enviando payload para {data_reserva_str}: {json.dumps(payload, indent=4)}")
            response = requests.post(url, json=payload, headers=headers, cookies=cookies, timeout=10)
            if response.status_code == 201:
                print(f"✅ Reserva criada com sucesso para {data_reserva_str}!")
            else:
                print(f"❌ Falha ao criar reserva para {data_reserva_str}: {response.status_code}")
                print(response.text)
        except requests.RequestException as e:
            print(f"❌ Erro de conexão para {data_reserva_str}: {e}")

    return True




    
def verificar_reserva(cookies=None):
    # Se os cookies não forem passados ou não forem válidos, faz login novamente
    if cookies is None or not verificar_cookies_validos(cookies):
        print("🔄 Cookies expirados ou inválidos. Fazendo login novamente...")
        fazer_login()
        cookies = carregar_cookies()

    # Se ainda não conseguiu carregar os cookies, encerra a tentativa
    if not cookies:
        print("❌ Cookies não encontrados após login. Não é possível continuar.")
        return

    print("🚀 Tentando criar reserva para amanhã...")
    sucesso = enviar_reserva(cookies)

    # Feedback visual para o usuário
    if sucesso:
        print("✅ Reserva criada com sucesso!")
    else:
        print("❌ Falha ao criar reserva.")

def agendar_reserva():
    global cookies
    preferencias = carregar_preferencias()

    if not preferencias:
        print("❌ Não foi possível carregar as preferências.")
        return

    dias_semana_permitidos = preferencias["dias_semana"]

    # Verifica se os cookies ainda são válidos
    if not verificar_cookies_validos(cookies):
        print("🔄 Cookies expirados ou inválidos. Fazendo login novamente...")
        fazer_login()
        cookies = carregar_cookies()

    # Verifica os próximos 7 dias
    hoje = datetime.now()
    for offset in range(7):
        data_reserva = hoje + timedelta(days=offset)
        nome_dia_reserva = data_reserva.strftime("%A")
        dia_reserva_pt = {
            "Monday": "Segunda",
            "Tuesday": "Terça",
            "Wednesday": "Quarta",
            "Thursday": "Quinta",
            "Friday": "Sexta",
            "Saturday": "Sábado",
            "Sunday": "Domingo"
        }.get(nome_dia_reserva, nome_dia_reserva)

        # Se for um dos dias permitidos, tenta criar a reserva
        if dia_reserva_pt in dias_semana_permitidos:
            print(f"🚀 Tentando criar reserva para {dia_reserva_pt} ({data_reserva.strftime('%Y-%m-%d')})...")
            verificar_reserva(cookies)



def criar_interface():
    root = tk.Tk()
    root.title("WiseBot - Configurar Reservas")
    root.geometry("400x600")
    root.configure(bg="#F4F4F9")
    root.resizable(False, False)

    # Cadeiras
    tk.Label(root, text="Cadeira/Sala:", bg="#F4F4F9", fg="#1D3557", font=("Segoe UI", 12)).pack(pady=(15, 5))
    cadeira_var = tk.StringVar(value=list(CADEIRAS_IDS.keys())[0])
    cadeira_menu = ttk.Combobox(root, textvariable=cadeira_var, values=list(CADEIRAS_IDS.keys()), state="readonly", width=35)
    cadeira_menu.pack(pady=5)

    # Data de Início
    tk.Label(root, text="Data de Início:", bg="#F4F4F9", fg="#1D3557", font=("Segoe UI", 12)).pack(pady=(15, 5))
    data_inicio_var = tk.Entry(root, width=35, font=("Segoe UI", 10))
    data_inicio_var.insert(0, datetime.now().strftime("%Y-%m-%d"))
    data_inicio_var.pack(pady=5)

    def selecionar_data():
        calendario_win = tk.Toplevel(root)
        calendario_win.title("Selecionar Data de Início")
        calendario_win.geometry("350x400")
        calendario_win.configure(bg="#F4F4F9")

        cal = Calendar(calendario_win, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack(pady=20)

        tk.Button(
            calendario_win, 
            text="Confirmar", 
            command=lambda: (data_inicio_var.delete(0, tk.END), data_inicio_var.insert(0, cal.get_date()), calendario_win.destroy()),
            bg="#0077B6",
            fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=5
        ).pack(pady=10)

    tk.Button(
        root, 
        text="Selecionar Data", 
        command=selecionar_data,
        bg="#0077B6",
        fg="#FFFFFF",
        font=("Segoe UI", 10, "bold"),
        relief=tk.FLAT,
        bd=0,
        padx=10,
        pady=5,
        width=30
    ).pack(pady=5)

    # Dias da Semana
    tk.Label(root, text="Dias da Semana:", bg="#F4F4F9", fg="#1D3557", font=("Segoe UI", 12)).pack(pady=(15, 5))
    dias_semana_vars = {}
    dias_semana_frame = tk.Frame(root, bg="#F4F4F9")
    dias_semana_frame.pack()
    for dia in ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(dias_semana_frame, text=dia, variable=var, bg="#A8DADC", fg="#1D3557", font=("Segoe UI", 10, "bold"))
        chk.pack(side=tk.LEFT, padx=5, pady=5)
        dias_semana_vars[dia] = var

    # Intervalo de Repetição
    tk.Label(root, text="Repetir a cada X semanas:", bg="#F4F4F9", fg="#1D3557", font=("Segoe UI", 12)).pack(pady=(15, 5))
    intervalo_var = tk.Entry(root, width=35, font=("Segoe UI", 10))
    intervalo_var.insert(0, "1")
    intervalo_var.pack(pady=5)

    # Horários de Início
    horarios_inicio = [f"{h:02d}:{m:02d}" for h in range(7, 18) for m in (0, 30) if h > 7 or m >= 30]
    tk.Label(root, text="Horário de Início:", bg="#F4F4F9", fg="#1D3557", font=("Segoe UI", 12)).pack(pady=(15, 5))
    horario_inicio_var = ttk.Combobox(root, values=horarios_inicio, width=35, state="readonly")
    horario_inicio_var.set("07:30")
    horario_inicio_var.pack(pady=5)

    # Horários de Fim
    horarios_fim = [f"{h:02d}:{m:02d}" for h in range(8, 19) for m in (0, 30)]
    tk.Label(root, text="Horário de Fim:", bg="#F4F4F9", fg="#1D3557", font=("Segoe UI", 12)).pack(pady=(15, 5))
    horario_fim_var = ttk.Combobox(root, values=horarios_fim, width=35, state="readonly")
    horario_fim_var.set("08:30")
    horario_fim_var.pack(pady=5)

    # Botão Confirmar
    tk.Button(
        root, 
        text="Confirmar", 
        command=lambda: salvar_preferencias(
            cadeira_var.get(), 
            data_inicio_var.get(), 
            [dia for dia, var in dias_semana_vars.items() if var.get()],
            int(intervalo_var.get()),
            horario_inicio_var.get(),
            horario_fim_var.get()
        ),
        bg="#0077B6",
        fg="#FFFFFF",
        font=("Segoe UI", 11, "bold"),
        relief=tk.FLAT,
        bd=0,
        padx=10,
        pady=10,
        width=30
    ).pack(pady=20)

    root.mainloop()

import threading

import threading
import schedule
import time

if __name__ == "__main__":
    # Faz o login e carrega os cookies antes de abrir a interface
    fazer_login()
    cookies = carregar_cookies()

    # Inicia a interface do Tkinter em uma thread separada
    def iniciar_interface():
        criar_interface()

    interface_thread = threading.Thread(target=iniciar_interface)
    interface_thread.daemon = True
    interface_thread.start()

    # Define os horários para verificar as reservas
    horarios_preferidos = [
        "08:30",
        "09:00",
        "09:30",
        "16:01"
    ]

    # Configura o agendador para verificar as reservas nos horários definidos
    def agendar_reserva():
        global cookies
        preferencias = carregar_preferencias()

        if not preferencias:
            print("❌ Não foi possível carregar as preferências.")
            return

        dias_semana_permitidos = preferencias["dias_semana"]

        # Verifica se os cookies ainda são válidos
        if not verificar_cookies_validos(cookies):
            print("🔄 Cookies expirados ou inválidos. Fazendo login novamente...")
            fazer_login()
            cookies = carregar_cookies()

        # Verifica os próximos 7 dias
        hoje = datetime.now()
        for offset in range(7):
            data_reserva = hoje + timedelta(days=offset)
            nome_dia_reserva = data_reserva.strftime("%A")
            dia_reserva_pt = {
                "Monday": "Segunda",
                "Tuesday": "Terça",
                "Wednesday": "Quarta",
                "Thursday": "Quinta",
                "Friday": "Sexta",
                "Saturday": "Sábado",
                "Sunday": "Domingo"
            }.get(nome_dia_reserva, nome_dia_reserva)

            # Se for um dos dias permitidos, tenta criar a reserva
            if dia_reserva_pt in dias_semana_permitidos:
                print(f"🚀 Tentando criar reserva para {dia_reserva_pt} ({data_reserva.strftime('%Y-%m-%d')})...")
                verificar_reserva(cookies)

    # Registra as tarefas no agendador
    for horario in horarios_preferidos:
        print(f"⏰ Agendando reserva para: {horario}")
        schedule.every().day.at(horario).do(agendar_reserva)

    # Loop principal do agendador
    print("🔁 Iniciando loop do agendador...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Agendador interrompido manualmente. Encerrando...")
        navegador.quit()  # Fecha o navegador corretamente









    


