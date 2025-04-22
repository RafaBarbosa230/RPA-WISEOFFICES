import subprocess
import sys

def instalar_requisitos():
    try:
         subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
         print("Requisitos instalados com sucesso.")
    except Exception as e:
         print(f"Erro ao instalar requisitos: {e}")

instalar_requisitos()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
# from selenium.webdriver.support.select import Select
from pathlib import Path

import os
from dotenv import load_dotenv
from pathlib import Path
import tkinter as tk
from tkinter import simpledialog, messagebox

def pedir_credenciais_e_salvar():
    root = tk.Tk()
    root.withdraw()

    email = simpledialog.askstring("Login", "Digite seu e-mail do Wise Offices:")
    senha = simpledialog.askstring("Login", "Digite sua senha do Wise Offices:", show='*')

    if not email or not senha:
        messagebox.showerror("Erro", "E-mail e senha são obrigatórios.")
        exit()

    with open(".env", "w") as f:
        f.write(f"WISE_EMAIL={email}\nWISE_SENHA={senha}")

    messagebox.showinfo("Sucesso", "Credenciais salvas com sucesso!")


env_path = Path(".env")
load_dotenv()

if not env_path.exists() or not os.getenv("WISE_EMAIL") or not os.getenv("WISE_SENHA"):
    pedir_credenciais_e_salvar()


load_dotenv()
email = os.getenv("WISE_EMAIL")
senha = os.getenv("WISE_SENHA")
if not email or not senha:
    raise ValueError("Email ou senha não encontrados no arquivo .env")


options = webdriver.ChromeOptions()
# options.add_argument("--headless")
navegador = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def fazer_login():
    navegador.get("https://id.wiseoffices.com.br/realms/wiseoffices/protocol/openid-connect/auth?client_id=wiseoffices&redirect_uri=https%3A%2F%2Fapp.wiseoffices.com.br%2Fdeimos%2Fcallback&response_type=code&scope=openid+profile+email&state=5Ssta2lqTl8UlryVjVmZXpww8n2PKIp_AbRnWiBlYkgOjrCI5SvYKnSoIY_bH73d")
    navegador.maximize_window()

    campo_email = WebDriverWait(navegador, 10).until(EC.presence_of_element_located((By.ID, "username")))
    campo_email.send_keys(email)

    campo_continuar = WebDriverWait(navegador, 10).until(EC.element_to_be_clickable((By.ID, "kc-login")))
    campo_continuar.click()

    input_senha = WebDriverWait(navegador, 10).until(EC.presence_of_element_located((By.ID, "password")))
    input_senha.send_keys(senha)

    campo_continuar_dois = WebDriverWait(navegador, 10).until(EC.element_to_be_clickable((By.NAME, "login")))
    campo_continuar_dois.click()


    print('Logado com sucesso')

    WebDriverWait(navegador, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "styles__ComplementsSelectBox-sc-1qitxh9-1"))
    )

def selecionar_andar():
    WebDriverWait(navegador, 10).until(EC.invisibility_of_element_located((By.ID, "wof-loading-spinner")))
    campo_andar = WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "styles__ComplementsSelectBox-sc-1qitxh9-1"))
    )
    campo_andar.click()
    campo_andar_dois = WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/main/div[1]/header/div[1]/div[2]/label[2]'))
    )
    campo_andar_dois.click()


def selecionar_data():
    hoje = datetime.now()
    dia_semana_atual = hoje.weekday()  
    dias_pra_quarta = (2 - dia_semana_atual) % 7
    if dias_pra_quarta == 0:  
        dias_pra_quarta = 7
    proxima_quarta = hoje + timedelta(days=dias_pra_quarta)

    dia_do_mes = proxima_quarta.day
    try:
        botao_data = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "styles__DateLabel-sc-1twe1n3-2"))
        )
        botao_data.click()
        WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "react-datepicker__day"))
        )
        dias_disponiveis = navegador.find_elements(By.CLASS_NAME, "react-datepicker__day")
        for dia in dias_disponiveis:
            if dia.text == str(dia_do_mes):
                navegador.execute_script("arguments[0].click();", dia)
                print(f"Quarta-feira {dia_do_mes} selecionada com sucesso.")
                WebDriverWait(navegador, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="7632"]'))
                )
                return "quarta"
        print(f"Quarta-feira {dia_do_mes} não disponível.")
    except Exception as e:
        print(f"Erro ao tentar quarta-feira {dia_do_mes}: {e}")

    dias_pra_quinta = (3 - dia_semana_atual) % 7
    if dias_pra_quinta == 0:  
        dias_pra_quinta = 7
    proxima_quinta = hoje + timedelta(days=dias_pra_quinta)

   
    dia_do_mes = proxima_quinta.day
    try:
        botao_data = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "styles__DateLabel-sc-1twe1n3-2"))
        )
        botao_data.click()
        WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "react-datepicker__day"))
        )
        dias_disponiveis = navegador.find_elements(By.CLASS_NAME, "react-datepicker__day")
        for dia in dias_disponiveis:
            if dia.text == str(dia_do_mes):
                navegador.execute_script("arguments[0].click();", dia)
                print(f"Quinta-feira {dia_do_mes} selecionada com sucesso.")
                WebDriverWait(navegador, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="7632"]'))
                )
                return "quinta"
        print(f"Quinta-feira {dia_do_mes} não disponível.")
    except Exception as e:
        print(f"Erro ao tentar quinta-feira {dia_do_mes}: {e}")

    
    print("Nem quarta nem quinta disponíveis.")
    return None


def selecionar_sala():
    try:
        sala = WebDriverWait(navegador, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="7632"]/div'))
        )
        sala.click()
    except:
        try:
            sala = WebDriverWait(navegador, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="7630"]/div[2]'))
            )
            sala.click()
        except Exception as e:
            print("Nenhuma sala disponível:", e)


def selecionar_horario(dia_semana):

    if dia_semana.lower() in ["quarta", "wednesday"]:
        horario_inicio = "13:00"
        horario_fim = "13:30"
    elif dia_semana.lower() in ["quinta", "thursday"]:
        horario_inicio = "17:30"
        horario_fim = "19:00"
    else:
        print(f"Dia '{dia_semana}' não é quarta nem quinta. Ignorando horário.")
        return

    try:
        
        print("Clicando no campo 'Início'...")
        campo_inicio = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="aside-content-ex-buttons"]/div[8]/div/div[1]/button'))
        )
        campo_inicio.click()

        print("Esperando os botões de início carregarem...")
        WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@id, 'start-')]"))
        )

        botoes_inicio = navegador.find_elements(By.XPATH, "//button[contains(@id, 'start-')]")
        horarios_disponiveis_inicio = {
            botao.get_attribute("id"): botao 
            for botao in botoes_inicio 
            if botao.is_displayed() and botao.is_enabled()
        }

        id_inicio = f"start-{horario_inicio}"
        if id_inicio not in horarios_disponiveis_inicio:
            raise Exception(f"Horário de início {horario_inicio} não disponível para {dia_semana}.")

        opcao_inicio = horarios_disponiveis_inicio[id_inicio]
        navegador.execute_script("arguments[0].scrollIntoView(true);", opcao_inicio)
        navegador.execute_script("arguments[0].click();", opcao_inicio)
        print(f"Horário de início {horario_inicio} selecionado com sucesso.")

        print("Clicando no campo 'Fim'...")
        campo_fim = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="aside-content-ex-buttons"]/div[8]/div/div[3]/button'))
        )
        campo_fim.click()

        print("Esperando os botões de fim carregarem...")
        WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@id, 'end-')]"))
        )

        botoes_fim = navegador.find_elements(By.XPATH, "//button[contains(@id, 'end-')]")
        horarios_disponiveis_fim = {
            botao.get_attribute("id"): botao 
            for botao in botoes_fim 
            if botao.is_displayed() and botao.is_enabled()
        }

        id_fim = f"end-{horario_fim}"
        if id_fim not in horarios_disponiveis_fim:
            raise Exception(f"Horário de fim {horario_fim} não disponível para {dia_semana}.")

        opcao_fim = horarios_disponiveis_fim[id_fim]
        navegador.execute_script("arguments[0].scrollIntoView(true);", opcao_fim)
        navegador.execute_script("arguments[0].click();", opcao_fim)
        print(f"Horário de fim {horario_fim} selecionado com sucesso.")
        print(f"Horários {horario_inicio} - {horario_fim} selecionados com sucesso para {dia_semana}.")

    except Exception as e:
        print(f"Erro ao selecionar horários: {e}")

def confirmar_reserva():
    reservar = WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "styles__ButtonContainer-sc-1xxf67x-0"))
    )
    reservar.click()
    WebDriverWait(navegador, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "styles__ButtonContainer-sc-1xxf67x-0"))
    )

def main():
    try:
        fazer_login()
        selecionar_andar()
        dia_reserva = selecionar_data()
        selecionar_sala()
        selecionar_horario(dia_reserva)
        confirmar_reserva()
        print("Reserva concluída com sucesso!")
    except Exception as e:
        print(f"Erro durante a reserva: {e}")
    finally:
        navegador.quit()

if __name__ == "__main__":
    main()
