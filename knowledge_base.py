import requests
from bs4 import BeautifulSoup
from googlesearch import search
import wikipedia
import json
import os

class BaseConhecimento:
    def __init__(self):
        wikipedia.set_lang('pt')
        self.cache_dir = 'cache'
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def pesquisar_programacao(self, query):
        """Pesquisa específica sobre programação"""
        # Tenta primeiro no Stack Overflow em português
        try:
            url = f"https://pt.stackoverflow.com/search?q={query}"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            resultados = []
            
            for pergunta in soup.select('.question-summary'):
                titulo = pergunta.select_one('.question-hyperlink').text
                resumo = pergunta.select_one('.excerpt').text
                votos = pergunta.select_one('.vote-count-post').text
                resultados.append({
                    'titulo': titulo,
                    'resumo': resumo,
                    'votos': votos,
                    'fonte': 'Stack Overflow PT'
                })
            
            return resultados[:3]  # Retorna os 3 melhores resultados
        except:
            pass
        
        # Se não encontrar no SO-PT, pesquisa no Google
        try:
            sites_tech = ['developer.mozilla.org', 'github.com', 'stackoverflow.com', 'medium.com']
            resultados = []
            
            for url in search(f"{query} programming", num_results=5):
                if any(site in url for site in sites_tech):
                    response = requests.get(url)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    titulo = soup.title.string if soup.title else url
                    resultados.append({
                        'titulo': titulo,
                        'url': url,
                        'fonte': 'Google'
                    })
            
            return resultados
        except:
            return None
    
    def pesquisar_wikipedia(self, query):
        """Pesquisa na Wikipedia em português"""
        try:
            resultados = wikipedia.search(query)
            if resultados:
                page = wikipedia.page(resultados[0])
                return {
                    'titulo': page.title,
                    'resumo': wikipedia.summary(resultados[0], sentences=3),
                    'url': page.url
                }
        except:
            return None
    
    def pesquisar_documentacao(self, tecnologia):
        """Retorna links para documentação oficial"""
        docs = {
            'python': 'https://docs.python.org/pt-br/3/',
            'javascript': 'https://developer.mozilla.org/pt-BR/docs/Web/JavaScript',
            'react': 'https://pt-br.reactjs.org/docs/getting-started.html',
            'django': 'https://docs.djangoproject.com/pt-br/latest/',
            'flask': 'https://flask.palletsprojects.com/',
            'html': 'https://developer.mozilla.org/pt-BR/docs/Web/HTML',
            'css': 'https://developer.mozilla.org/pt-BR/docs/Web/CSS',
        }
        return docs.get(tecnologia.lower())
    
    def obter_tutorial_rapido(self, tecnologia, nivel='iniciante'):
        """Gera um tutorial rápido baseado na tecnologia"""
        # Aqui você pode expandir com mais tutoriais
        tutoriais = {
            'python': {
                'iniciante': """
                # Tutorial Rápido de Python
                1. Instalação: python.org/downloads
                2. Primeiros passos:
                   ```python
                   print("Olá, Mundo!")
                   ```
                3. Variáveis:
                   ```python
                   nome = "ED"
                   idade = 1
                   ```
                4. Condicionais:
                   ```python
                   if idade > 0:
                       print("Positivo!")
                   ```
                """,
                'intermediario': """
                # Python Intermediário
                1. Funções:
                   ```python
                   def saudacao(nome):
                       return f"Olá, {nome}!"
                   ```
                2. Classes:
                   ```python
                   class Pessoa:
                       def __init__(self, nome):
                           self.nome = nome
                   ```
                """
            }
        }
        return tutoriais.get(tecnologia.lower(), {}).get(nivel)
    
    def formatar_resposta_programacao(self, resultados):
        """Formata os resultados da pesquisa de programação"""
        if not resultados:
            return "Desculpe, não encontrei informações específicas sobre isso."
        
        resposta = "Encontrei algumas informações que podem ajudar:\n\n"
        
        for i, res in enumerate(resultados, 1):
            resposta += f"{i}. {res['titulo']}\n"
            if 'resumo' in res:
                resposta += f"   {res['resumo']}\n"
            if 'url' in res:
                resposta += f"   Link: {res['url']}\n"
            resposta += "\n"
        
        return resposta
