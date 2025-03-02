import os
import subprocess
import pyautogui
import psutil
import keyboard
import json
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import wikipedia
import webbrowser
from datetime import datetime
import win32gui
import win32con
import win32process
import time

class SystemController:
    def __init__(self):
        self.app_paths = self.load_app_paths()
        self.weather_api_key = os.getenv('WEATHER_API_KEY')
        
    def load_app_paths(self):
        """Carrega os caminhos dos aplicativos comuns"""
        common_apps = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            "notepad": r"C:\Windows\System32\notepad.exe",
            "calculator": r"C:\Windows\System32\calc.exe",
            "explorer": r"C:\Windows\explorer.exe",
            "cmd": r"C:\Windows\System32\cmd.exe",
            "powershell": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
        }
        return common_apps

    def abrir_aplicativo(self, nome_app):
        """Abre um aplicativo pelo nome"""
        try:
            # Tenta encontrar o caminho do aplicativo
            if nome_app.lower() in self.app_paths:
                subprocess.Popen(self.app_paths[nome_app.lower()])
                return f"Abrindo {nome_app}..."
            else:
                # Tenta executar diretamente
                subprocess.Popen(nome_app)
                return f"Tentando abrir {nome_app}..."
        except Exception as e:
            return f"Não foi possível abrir {nome_app}: {str(e)}"

    def fechar_aplicativo(self, nome_app):
        """Fecha um aplicativo pelo nome"""
        try:
            os.system(f'taskkill /F /IM "{nome_app}.exe"')
            return f"Fechando {nome_app}..."
        except:
            return f"Não foi possível fechar {nome_app}"

    def pesquisar_web(self, query, engine="google"):
        """Realiza uma pesquisa na web"""
        if engine == "google":
            webbrowser.open(f"https://www.google.com/search?q={query}")
        elif engine == "youtube":
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return f"Pesquisando por '{query}' no {engine}..."

    def controlar_volume(self, acao):
        """Controla o volume do sistema"""
        if acao == "aumentar":
            pyautogui.press("volumeup", 5)
            return "Aumentando o volume..."
        elif acao == "diminuir":
            pyautogui.press("volumedown", 5)
            return "Diminuindo o volume..."
        elif acao == "mudo":
            pyautogui.press("volumemute")
            return "Alternando mudo..."

    def obter_info_sistema(self):
        """Obtém informações do sistema"""
        cpu = psutil.cpu_percent()
        memoria = psutil.virtual_memory().percent
        disco = psutil.disk_usage('/').percent
        return {
            'cpu': cpu,
            'memoria': memoria,
            'disco': disco
        }

    def capturar_tela(self, nome_arquivo=None):
        """Captura a tela atual"""
        if not nome_arquivo:
            nome_arquivo = f"captura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(nome_arquivo)
        return f"Captura de tela salva como {nome_arquivo}"

    def controlar_midia(self, acao):
        """Controla reprodução de mídia"""
        acoes = {
            "play": "playpause",
            "pause": "playpause",
            "proximo": "nexttrack",
            "anterior": "prevtrack",
            "parar": "stop"
        }
        if acao in acoes:
            pyautogui.press(acoes[acao])
            return f"Comando de mídia: {acao}"

    def pesquisar_wikipedia(self, query, lang='pt'):
        """Pesquisa um termo na Wikipedia"""
        wikipedia.set_lang(lang)
        try:
            resultado = wikipedia.summary(query, sentences=3)
            return resultado
        except:
            return "Não encontrei informações sobre isso na Wikipedia."

    def obter_clima(self, cidade):
        if not self.weather_api_key:
            return "Desculpe, a funcionalidade de clima ainda não está configurada. Use 'pesquisar clima em [cidade]' para uma busca na web."
        api_key = self.weather_api_key
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": cidade,
            "appid": api_key,
            "units": "metric",
            "lang": "pt_br"
        }
        
        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                return f"""
Clima em {cidade}:
Temperatura: {data['main']['temp']}°C
Sensação: {data['main']['feels_like']}°C
Condição: {data['weather'][0]['description']}
Umidade: {data['main']['humidity']}%
"""
            else:
                return "Não foi possível obter informações do clima"
        except:
            return "Erro ao consultar o clima"

    def criar_lembrete(self, texto, tempo_minutos):
        """Cria um lembrete com notificação"""
        def notificar():
            time.sleep(tempo_minutos * 60)
            pyautogui.alert(texto, "Lembrete")
        
        import threading
        threading.Thread(target=notificar, daemon=True).start()
        return f"Lembrete criado: {texto} (em {tempo_minutos} minutos)"

    def executar_comando(self, comando):
        """Executa um comando do sistema"""
        try:
            resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
            return resultado.stdout if resultado.stdout else resultado.stderr
        except Exception as e:
            return f"Erro ao executar comando: {str(e)}"

    def listar_processos(self):
        """Lista os processos em execução"""
        processos = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                processos.append({
                    'pid': proc.info['pid'],
                    'nome': proc.info['name'],
                    'memoria': f"{proc.info['memory_percent']:.1f}%"
                })
            except:
                pass
        return processos[:10]  # Retorna os 10 primeiros processos

    def minimizar_janelas(self):
        """Minimiza todas as janelas"""
        pyautogui.hotkey('win', 'd')
        return "Minimizando todas as janelas..."

    def alternar_janela(self):
        """Alterna entre janelas abertas"""
        pyautogui.hotkey('alt', 'tab')
        return "Alternando janelas..."
