import customtkinter as ctk
import json
import os
from datetime import datetime
import openai
from dotenv import load_dotenv
import sqlite3
import pyttsx3
import speech_recognition as sr
from threading import Thread

# Carrega variáveis de ambiente
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "sua_chave_aqui":
    raise ValueError("""
    Por favor, configure sua chave API do OpenAI no arquivo .env
    1. Acesse https://platform.openai.com/api-keys
    2. Crie uma nova chave API
    3. Copie a chave
    4. Abra o arquivo .env neste diretório
    5. Substitua 'sua_chave_aqui' pela sua chave API
    """)
openai.api_key = api_key

class AssistenteIA:
    def __init__(self):
        self.setup_database()
        self.setup_interface()
        self.verificar_microfone()
        self.setup_voz()
        self.carregar_perfil()
        
    def setup_database(self):
        self.conn = sqlite3.connect('assistente.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversas (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                usuario TEXT,
                resposta TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferencias (
                chave TEXT PRIMARY KEY,
                valor TEXT
            )
        ''')
        self.conn.commit()

    def setup_interface(self):
        self.janela = ctk.CTk()
        self.janela.title("Assistente IA Pessoal")
        self.janela.geometry("800x600")
        
        # Configuração do tema escuro moderno
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Frame principal
        self.frame_principal = ctk.CTkFrame(self.janela)
        self.frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Área de chat
        self.area_chat = ctk.CTkTextbox(self.frame_principal, height=400)
        self.area_chat.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame para entrada
        self.frame_entrada = ctk.CTkFrame(self.frame_principal)
        self.frame_entrada.pack(fill="x", padx=10, pady=5)
        
        # Campo de entrada
        self.entrada = ctk.CTkEntry(self.frame_entrada, placeholder_text="Digite sua mensagem...")
        self.entrada.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Botão de envio
        self.btn_enviar = ctk.CTkButton(self.frame_entrada, text="Enviar", command=self.enviar_mensagem)
        self.btn_enviar.pack(side="left", padx=5)
        
        # Botão de voz
        self.btn_voz = ctk.CTkButton(self.frame_entrada, text="🎤", width=40, command=self.iniciar_reconhecimento_voz)
        self.btn_voz.pack(side="left", padx=5)
        
        # Bind Enter para enviar mensagem
        self.entrada.bind("<Return>", lambda event: self.enviar_mensagem())

    def verificar_microfone(self):
        try:
            with sr.Microphone() as source:
                self.recognizer = sr.Recognizer()
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Microfone configurado com sucesso!")
        except Exception as e:
            print(f"""
            Aviso: Não foi possível configurar o microfone: {str(e)}
            O programa funcionará normalmente, mas o recurso de voz estará desabilitado.
            Para usar o recurso de voz:
            1. Verifique se um microfone está conectado
            2. Verifique se o microfone é o dispositivo de entrada padrão
            3. Verifique se o microfone tem permissão para ser usado
            """)
            self.microfone_disponivel = False
        else:
            self.microfone_disponivel = True

    def setup_voz(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', self.engine.getProperty('voices')[0].id)
        self.engine.setProperty('rate', 200)

    def carregar_perfil(self):
        self.cursor.execute("SELECT * FROM preferencias")
        self.preferencias = dict(self.cursor.fetchall())
        if not self.preferencias:
            self.preferencias = {
                "nome_usuario": "Usuário",
                "tom_conversa": "amigável",
                "interesses": []
            }
            self.salvar_preferencias()

    def salvar_preferencias(self):
        for chave, valor in self.preferencias.items():
            if isinstance(valor, (list, dict)):
                valor = json.dumps(valor)
            self.cursor.execute("""
                INSERT OR REPLACE INTO preferencias (chave, valor)
                VALUES (?, ?)
            """, (chave, valor))
        self.conn.commit()

    def atualizar_perfil(self, mensagem):
        # Análise simples de preferências baseada na mensagem
        mensagem_lower = mensagem.lower()
        
        # Detecta possíveis interesses
        palavras_chave = ["gosto de", "adoro", "prefiro", "interesse em"]
        for palavra in palavras_chave:
            if palavra in mensagem_lower:
                interesse = mensagem_lower.split(palavra)[1].split(".")[0].strip()
                if interesse and interesse not in self.preferencias["interesses"]:
                    self.preferencias["interesses"].append(interesse)
        
        self.salvar_preferencias()

    def gerar_resposta(self, mensagem):
        # Contexto baseado no perfil do usuário
        contexto = f"""
        Perfil do usuário:
        - Nome: {self.preferencias['nome_usuario']}
        - Tom de conversa preferido: {self.preferencias['tom_conversa']}
        - Interesses: {', '.join(self.preferencias['interesses'])}
        """
        
        try:
            resposta = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Você é um assistente pessoal em português do Brasil. {contexto}"},
                    {"role": "user", "content": mensagem}
                ]
            )
            return resposta.choices[0].message.content
        except Exception as e:
            return f"Desculpe, ocorreu um erro: {str(e)}"

    def salvar_conversa(self, mensagem, resposta):
        timestamp = datetime.now().isoformat()
        self.cursor.execute("""
            INSERT INTO conversas (timestamp, usuario, resposta)
            VALUES (?, ?, ?)
        """, (timestamp, mensagem, resposta))
        self.conn.commit()

    def falar(self, texto):
        Thread(target=self.engine.say, args=(texto,)).start()
        Thread(target=self.engine.runAndWait).start()

    def iniciar_reconhecimento_voz(self):
        if not self.microfone_disponivel:
            self.area_chat.insert("end", "\nMicrofone não está disponível. Por favor, verifique a configuração do seu microfone.\n")
            return

        def reconhecer():
            try:
                with sr.Microphone() as source:
                    self.area_chat.insert("end", "\nOuvindo... (fale algo)\n")
                    self.area_chat.see("end")
                    
                    # Ajusta o reconhecedor para o ruído ambiente
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    # Captura o áudio
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    self.area_chat.insert("end", "Processando sua fala...\n")
                    self.area_chat.see("end")
                    
                    texto = self.recognizer.recognize_google(audio, language='pt-BR')
                    self.entrada.delete(0, "end")
                    self.entrada.insert(0, texto)
                    self.enviar_mensagem()
            
            except sr.WaitTimeoutError:
                self.area_chat.insert("end", "\nNão ouvi nada. Por favor, tente novamente.\n")
            except sr.UnknownValueError:
                self.area_chat.insert("end", "\nNão entendi o que você disse. Por favor, tente novamente.\n")
            except sr.RequestError as e:
                self.area_chat.insert("end", f"\nErro ao acessar o serviço de reconhecimento: {str(e)}\n")
            except Exception as e:
                self.area_chat.insert("end", f"\nErro no reconhecimento de voz: {str(e)}\n")
            
            self.area_chat.see("end")

        Thread(target=reconhecer).start()

    def enviar_mensagem(self):
        mensagem = self.entrada.get().strip()
        if not mensagem:
            return
        
        # Limpa campo de entrada
        self.entrada.delete(0, "end")
        
        # Mostra mensagem do usuário
        self.area_chat.insert("end", f"\nVocê: {mensagem}\n")
        
        # Atualiza perfil com base na mensagem
        self.atualizar_perfil(mensagem)
        
        # Gera e mostra resposta
        resposta = self.gerar_resposta(mensagem)
        self.area_chat.insert("end", f"\nAssistente: {resposta}\n")
        self.area_chat.see("end")
        
        # Salva conversa
        self.salvar_conversa(mensagem, resposta)
        
        # Fala a resposta
        self.falar(resposta)

    def iniciar(self):
        self.janela.mainloop()

if __name__ == "__main__":
    assistente = AssistenteIA()
    assistente.iniciar()
