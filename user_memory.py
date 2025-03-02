import json
import os
from datetime import datetime, time
import sqlite3

class MemoriaUsuario:
    def __init__(self, db_path='assistente.db'):
        self.db_path = db_path
        self.setup_database()
        self.carregar_memoria()
        
    def setup_database(self):
        """Configura o banco de dados para armazenar memórias e horários"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de informações do usuário
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuario_info (
                chave TEXT PRIMARY KEY,
                valor TEXT,
                ultima_atualizacao TIMESTAMP
            )
        ''')
        
        # Tabela de horários e compromissos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS horarios (
                id INTEGER PRIMARY KEY,
                titulo TEXT,
                descricao TEXT,
                data_hora TIMESTAMP,
                recorrente BOOLEAN,
                dias_semana TEXT,
                notificar BOOLEAN
            )
        ''')
        
        # Tabela de tópicos de interesse
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interesses (
                id INTEGER PRIMARY KEY,
                topico TEXT,
                nivel_interesse INTEGER,
                ultima_interacao TIMESTAMP
            )
        ''')
        
        # Tabela de conhecimento de programação
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conhecimento_programacao (
                id INTEGER PRIMARY KEY,
                linguagem TEXT,
                framework TEXT,
                nivel_experiencia INTEGER,
                ultima_interacao TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def carregar_memoria(self):
        """Carrega as informações básicas do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT chave, valor FROM usuario_info")
        self.info = dict(cursor.fetchall())
        
        if not self.info:
            self.info = {
                "nome": None,
                "tratamento_preferido": None,
                "horario_trabalho_inicio": "09:00",
                "horario_trabalho_fim": "18:00",
                "ultima_interacao": None
            }
        
        conn.close()
    
    def atualizar_info(self, chave, valor):
        """Atualiza uma informação do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO usuario_info (chave, valor, ultima_atualizacao)
            VALUES (?, ?, ?)
        """, (chave, valor, datetime.now()))
        
        self.info[chave] = valor
        conn.commit()
        conn.close()
    
    def adicionar_horario(self, titulo, descricao, data_hora, recorrente=False, dias_semana=None, notificar=True):
        """Adiciona um novo horário ou compromisso"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO horarios (titulo, descricao, data_hora, recorrente, dias_semana, notificar)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (titulo, descricao, data_hora, recorrente, dias_semana, notificar))
        
        conn.commit()
        conn.close()
    
    def obter_proximos_compromissos(self, limite=5):
        """Obtém os próximos compromissos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT titulo, descricao, data_hora 
            FROM horarios 
            WHERE data_hora >= datetime('now')
            ORDER BY data_hora
            LIMIT ?
        """, (limite,))
        
        compromissos = cursor.fetchall()
        conn.close()
        return compromissos
    
    def adicionar_interesse(self, topico, nivel_interesse=1):
        """Registra um novo tópico de interesse"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO interesses (topico, nivel_interesse, ultima_interacao)
            VALUES (?, ?, ?)
        """, (topico, nivel_interesse, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def atualizar_conhecimento_programacao(self, linguagem, framework=None, nivel_experiencia=1):
        """Atualiza o conhecimento de programação do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO conhecimento_programacao 
            (linguagem, framework, nivel_experiencia, ultima_interacao)
            VALUES (?, ?, ?, ?)
        """, (linguagem, framework, nivel_experiencia, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def obter_perfil_completo(self):
        """Retorna um perfil completo do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtém interesses
        cursor.execute("SELECT topico FROM interesses ORDER BY nivel_interesse DESC LIMIT 5")
        interesses = [row[0] for row in cursor.fetchall()]
        
        # Obtém conhecimentos de programação
        cursor.execute("SELECT linguagem, framework FROM conhecimento_programacao")
        programacao = cursor.fetchall()
        
        conn.close()
        
        return {
            "info_pessoal": self.info,
            "interesses": interesses,
            "conhecimento_programacao": programacao
        }
    
    def processar_mensagem(self, texto):
        """Processa uma mensagem para extrair informações relevantes"""
        texto = texto.lower()
        
        # Detecta nome
        if "meu nome é" in texto or "me chamo" in texto:
            for frase in ["meu nome é ", "me chamo "]:
                if frase in texto:
                    nome = texto.split(frase)[1].split()[0].title()
                    self.atualizar_info("nome", nome)
                    return f"Prazer em conhecê-lo, {nome}! Vou me lembrar do seu nome."
        
        # Detecta horários
        if "trabalho das" in texto or "trabalho entre" in texto:
            try:
                horarios = texto.split("das ")[1].split(" às ")
                inicio = horarios[0].strip()
                fim = horarios[1].strip()
                self.atualizar_info("horario_trabalho_inicio", inicio)
                self.atualizar_info("horario_trabalho_fim", fim)
                return f"Entendi! Você trabalha das {inicio} às {fim}. Vou me lembrar disso."
            except:
                pass
        
        # Detecta interesses em programação
        linguagens = ["python", "javascript", "java", "c#", "php", "ruby"]
        frameworks = ["django", "flask", "react", "angular", "vue", "laravel"]
        
        for linguagem in linguagens:
            if f"programo em {linguagem}" in texto or f"uso {linguagem}" in texto:
                self.atualizar_conhecimento_programacao(linguagem)
                return f"Legal! Vou lembrar que você programa em {linguagem}."
        
        for framework in frameworks:
            if framework in texto:
                self.atualizar_conhecimento_programacao(None, framework)
                return f"Anotei que você tem experiência com {framework}!"
        
        return None
