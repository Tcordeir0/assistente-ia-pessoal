# 🤖 Assistente IA Pessoal

Um assistente pessoal inteligente desenvolvido em Python que aprende com suas interações, oferecendo uma experiência personalizada através de uma interface gráfica moderna e recursos de voz.

## ✨ Funcionalidades

- 🎯 **Interface Moderna**
  - Design limpo e intuitivo usando CustomTkinter
  - Modo escuro por padrão
  - Interface responsiva e amigável

- 🧠 **Inteligência Artificial**
  - Processamento de linguagem natural em português
  - Integração com OpenAI GPT
  - Aprendizado contínuo baseado nas interações
  - Personalização através do perfil do usuário

- 🗣️ **Recursos de Voz**
  - Reconhecimento de voz em português do Brasil
  - Síntese de voz para respostas
  - Ajuste automático para ruído ambiente
  - Funciona mesmo sem microfone (modo texto)

- 💾 **Persistência de Dados**
  - Armazenamento local usando SQLite
  - Histórico de conversas
  - Perfil de usuário personalizável
  - Preferências salvas automaticamente

## 🚀 Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/Tcordeir0/assistente-ia-pessoal.git
cd assistente-ia-pessoal
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure sua chave API**
- Crie uma conta na [OpenAI](https://platform.openai.com/)
- Gere uma chave API em https://platform.openai.com/api-keys
- Copie o arquivo `.env.example` para `.env`
- Adicione sua chave API no arquivo `.env`

## 💻 Como Usar

1. **Inicie o programa**
```bash
python main.py
```

2. **Interaja com o assistente**
- Digite suas mensagens na caixa de texto
- Use o botão de microfone para entrada por voz
- Pressione Enter ou clique em Enviar

3. **Personalize sua experiência**
- O assistente aprende com suas interações
- Suas preferências são salvas automaticamente
- O histórico de conversas é mantido localmente

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**: Linguagem de programação principal
- **CustomTkinter**: Framework para interface gráfica moderna
- **OpenAI GPT**: Motor de processamento de linguagem natural
- **SQLite**: Banco de dados local para persistência
- **SpeechRecognition**: Reconhecimento de voz
- **pyttsx3**: Síntese de voz

## 📝 Requisitos do Sistema

- Python 3.8 ou superior
- Conexão com internet (para API do OpenAI)
- Microfone (opcional, para recursos de voz)
- Windows 11 (testado)

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---
Desenvolvido com 💜 por [Tcordeir0](https://github.com/Tcordeir0)
