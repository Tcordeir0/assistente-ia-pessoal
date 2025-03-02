import sys
import openai
from dotenv import load_dotenv
import os
import time
from threading import Thread
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                          QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sqlite3
import json
import psutil
import pyttsx3
from typing import Optional
import random
from system_commands import SystemController
from user_memory import MemoriaUsuario
from knowledge_base import BaseConhecimento

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class MonitorThread(QThread):
    update_signal = pyqtSignal(dict)
    
    def run(self):
        while True:
            try:
                info = {
                    'cpu': psutil.cpu_percent(),
                    'ram': psutil.virtual_memory().percent,
                    'disk': psutil.disk_usage('/').percent
                }
                self.update_signal.emit(info)
                time.sleep(1)
            except Exception as e:
                print(f"Erro no monitoramento: {e}")
                time.sleep(5)

class VoiceThread(QThread):
    def __init__(self, engine, text):
        super().__init__()
        self.engine = engine
        self.text = text
    
    def run(self):
        try:
            self.engine.say(self.text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Erro na síntese de voz: {e}")

class AssistenteIA(QMainWindow):
    def __init__(self):
        super().__init__()
        self.system = SystemController()
        self.memoria = MemoriaUsuario()
        self.conhecimento = BaseConhecimento()
        self.nome_chamada = ["ed", "ei ed", "ed?", "ed está aí", "ed está ai", "ia ai ed"]
        self.setup_database()
        self.setup_voz()
        self.setup_interface()
        self.historico_conversa = []
        self.max_historico = 10
        self.show()

    def setup_voz(self):
        """Configura o sistema de voz"""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            
            # Debug para ver as vozes disponíveis
            print("Vozes disponíveis:")
            for idx, voice in enumerate(voices):
                print(f"{idx}: {voice.name} ({voice.id}) - Línguas: {voice.languages}")
            
            # Tenta encontrar uma voz em português
            voz_pt = None
            for voice in voices:
                if "portuguese" in voice.name.lower() or "brazil" in voice.name.lower():
                    voz_pt = voice
                    break
            
            # Se não encontrar voz em português, usa a primeira disponível
            if voz_pt:
                print(f"Usando voz em português: {voz_pt.name}")
                self.engine.setProperty('voice', voz_pt.id)
            else:
                print("Voz em português não encontrada, usando voz padrão")
                self.engine.setProperty('voice', voices[0].id)
            
            self.engine.setProperty('rate', 180)  # Velocidade normal
            self.engine.setProperty('volume', 1.0)  # Volume máximo
            
            # Testa a voz
            print("Testando voz...")
            self.engine.say("Teste de voz do assistente ED")
            self.engine.runAndWait()
            
        except Exception as e:
            print(f"Erro ao configurar voz: {e}")
            self.engine = None

    def falar(self, texto):
        """Fala o texto usando síntese de voz"""
        if self.engine:
            try:
                thread = VoiceThread(self.engine, texto)
                thread.start()
            except Exception as e:
                print(f"Erro ao falar: {e}")

    def setup_interface(self):
        # Configuração da janela principal
        self.setWindowTitle("ED - Assistente Pessoal")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #2d2d2d;
                border: 2px solid #0288D1;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 2px solid #0288D1;
                border-radius: 20px;
                padding: 10px;
                font-size: 14px;
                height: 40px;
            }
            QPushButton {
                background-color: #0288D1;
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #01579B;
            }
            QLabel {
                color: #4FC3F7;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Cabeçalho com status e monitoramento
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header.setStyleSheet("background-color: #0D47A1; border-radius: 10px; padding: 10px;")
        
        # Status do sistema
        status_label = QLabel("⚡ SISTEMA ONLINE")
        status_label.setStyleSheet("font-size: 16px; color: #4FC3F7;")
        header_layout.addWidget(status_label)
        
        # Monitoramento
        self.cpu_label = QLabel("CPU: 0%")
        self.ram_label = QLabel("RAM: 0%")
        self.disk_label = QLabel("DISK: 0%")
        
        for label in [self.cpu_label, self.ram_label, self.disk_label]:
            header_layout.addWidget(label)
        
        layout.addWidget(header)

        # Área de chat
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)

        # Área de entrada
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Digite sua mensagem...")
        self.input_field.returnPressed.connect(self.enviar_mensagem)
        
        send_button = QPushButton("ENVIAR")
        send_button.clicked.connect(self.enviar_mensagem)
        send_button.setFixedWidth(100)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_button)
        
        layout.addWidget(input_container)

        # Inicia o monitoramento em uma thread separada
        self.monitor_thread = MonitorThread()
        self.monitor_thread.update_signal.connect(self.atualizar_monitor)
        self.monitor_thread.start()

        # Mensagem inicial
        self.adicionar_mensagem("ED", "Olá! Eu sou o ED, seu assistente pessoal. Como posso ajudar?")

    def atualizar_monitor(self, info):
        self.cpu_label.setText(f"CPU: {info['cpu']}%")
        self.ram_label.setText(f"RAM: {info['ram']}%")
        self.disk_label.setText(f"DISK: {info['disk']}%")

    def adicionar_mensagem(self, nome, mensagem):
        cor = "#4FC3F7" if nome == "ED" else "#FFFFFF"
        formato = f'<div style="margin: 10px 0;"><span style="color: {cor}; font-weight: bold;">{nome}:</span> {mensagem}</div>'
        self.chat_area.append(formato)
        if nome == "ED":
            self.falar(mensagem)

    def enviar_mensagem(self):
        mensagem = self.input_field.text().strip()
        if mensagem:
            self.input_field.clear()
            self.adicionar_mensagem("Você", mensagem)
            
            # Processa a mensagem e obtém resposta
            try:
                resposta = self.processar_comando(mensagem)
                if not resposta:
                    resposta = self.gerar_resposta(mensagem)
                
                self.adicionar_mensagem("ED", resposta)
            except Exception as e:
                self.adicionar_mensagem("ED", f"Desculpe, ocorreu um erro: {str(e)}")

    def gerar_resposta(self, mensagem):
        try:
            # Prepara o contexto para a OpenAI
            perfil = self.memoria.obter_perfil_completo()
            
            # Adiciona a mensagem ao histórico
            self.historico_conversa.append({"role": "user", "content": mensagem})
            if len(self.historico_conversa) > self.max_historico * 2:
                self.historico_conversa = self.historico_conversa[-self.max_historico * 2:]

            # Sistema de mensagens com contexto personalizado
            system_message = {
                "role": "system",
                "content": f"""Você é ED, um assistente pessoal em português do Brasil.
                
                Informações do usuário:
                - Nome: {perfil['info_pessoal'].get('nome', 'Usuário')}
                - Horário de trabalho: {perfil['info_pessoal'].get('horario_trabalho_inicio', '09:00')} às {perfil['info_pessoal'].get('horario_trabalho_fim', '18:00')}
                
                Interesses: {', '.join(perfil['interesses']) if perfil['interesses'] else 'Ainda não definidos'}
                
                Conhecimentos de programação: {', '.join(f"{lang} ({fw})" if fw else lang for lang, fw in perfil['conhecimento_programacao'])}
                
                Diretrizes:
                1. Sempre responda em português do Brasil
                2. Use o nome do usuário quando disponível
                3. Considere o horário de trabalho ao sugerir atividades
                4. Aproveite o conhecimento prévio em programação
                5. Seja conciso e direto nas respostas
                """
            }

            # Prepara todas as mensagens
            messages = [system_message] + self.historico_conversa

            # Faz a chamada para a API
            resposta = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return resposta.choices[0].message.content

        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}"

    def setup_database(self):
        self.conn = sqlite3.connect('assistente.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            usuario TEXT,
            resposta TEXT
        )
        ''')
        self.conn.commit()

    def processar_comando(self, texto):
        """Processa comandos do usuário"""
        texto = texto.lower()

        # Respostas básicas sem usar API
        respostas_basicas = {
            "oi": "Olá! Como posso ajudar?",
            "olá": "Oi! Como posso ajudar?",
            "tudo bem": "Tudo ótimo! Como posso ajudar você hoje?",
            "tudo bem?": "Tudo ótimo! Como posso ajudar você hoje?",
            "como vai": "Estou muito bem, obrigado por perguntar! Como posso ajudar?",
            "como você está": "Estou funcionando perfeitamente! Como posso ajudar?",
            "bom dia": "Bom dia! Como posso ajudar?",
            "boa tarde": "Boa tarde! Como posso ajudar?",
            "boa noite": "Boa noite! Como posso ajudar?"
        }

        # Verifica se é uma resposta básica
        for pergunta, resposta in respostas_basicas.items():
            if pergunta in texto:
                return resposta
        
        # Comandos do sistema
        if "abrir" in texto:
            app = texto.split("abrir")[-1].strip()
            return self.system.abrir_aplicativo(app)
            
        elif "fechar" in texto:
            app = texto.split("fechar")[-1].strip()
            return self.system.fechar_aplicativo(app)
            
        elif "volume" in texto:
            if "aumentar" in texto:
                return self.system.controlar_volume("aumentar")
            elif "diminuir" in texto:
                return self.system.controlar_volume("diminuir")
            elif "mudo" in texto:
                return self.system.controlar_volume("mudo")
                
        elif "pesquisar" in texto:
            termo = texto.split("pesquisar")[-1].strip()
            return self.system.pesquisar_web(termo)
            
        # Outros comandos...
        return None

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        assistente = AssistenteIA()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Erro ao iniciar o assistente: {str(e)}")
