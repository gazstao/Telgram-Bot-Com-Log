# BotOllama

Bot de Telegram que responde mensagens usando um modelo de linguagem rodando **localmente** com o [Ollama](https://ollama.com). Sem API paga e sem enviar suas conversas para a nuvem.

## Funcionalidades

- Responde mensagens de texto usando qualquer modelo do Ollama
- Mantém o histórico da conversa separado por usuário
- Divide respostas longas automaticamente (o Telegram limita cada mensagem a 4096 caracteres)
- Log completo no terminal e no arquivo `bot.log`: mensagens recebidas, respostas enviadas e erros
- Tratamento de erros quando o Ollama está fora do ar ou o modelo não existe
- Comandos: `/start`, `/limpar` (zera a conversa) e `/id` (mostra seu ID do Telegram)

## Requisitos

- Python 3.10 ou superior
- [Ollama](https://ollama.com/download) instalado e em execução
- Um modelo baixado no Ollama (por exemplo, `llama3.1:8b`)
- Um bot criado no Telegram com o [@BotFather](https://t.me/BotFather)

## Instalação

```bash
git clone https://github.com/gazstao/Telgram-Bot-Com-Log
cd Telgram-Bot-Com-Log

python -m venv venv
```

Ative o ambiente virtual:

```powershell
# Windows (PowerShell)
venv\Scripts\activate
```

```bash
# Linux / macOS
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuração

### 1. Baixe um modelo no Ollama

```bash
ollama pull llama3.1:8b
ollama list
```

O nome exibido na coluna `NAME` do `ollama list` deve ser o mesmo configurado na variável `MODELO` do `bot_com_log.py`. Se sua máquina tem pouca memória, use um modelo menor, como `llama3.2:3b` ou `gemma3:4b`.

### 2. Crie o bot e pegue o token

1. No Telegram, abra o [@BotFather](https://t.me/BotFather)
2. Envie `/newbot`
3. Escolha um nome e um username (terminado em `bot`)
4. Copie o token que ele enviar

### 3. Defina o token como variável de ambiente

```powershell
# Windows (PowerShell), vale só para a janela atual
$env:TELEGRAM_TOKEN="seu_token_aqui"
```

```bash
# Linux / macOS
export TELEGRAM_TOKEN="seu_token_aqui"
```

> **Nunca coloque o token no código nem o suba para o GitHub.** Se ele vazar, gere outro com `/mybots` no BotFather.

## Como usar

Com o Ollama rodando e o token definido:

```bash
python bot_com_log.py
```

Abra seu bot no Telegram, envie `/start` e converse.

## Configurações do código

No início do `bot_com_log.py`:

| Variável | Descrição | Padrão |
|---|---|---|
| `MODELO` | Nome do modelo no Ollama | `llama3.1:8b` |
| `MAX_MENSAGENS_HISTORICO` | Quantas mensagens recentes são enviadas ao modelo | `20` |
| `LIMITE_TELEGRAM` | Tamanho máximo de cada mensagem enviada | `4000` |
| `ARQUIVO_LOG` | Arquivo onde o log é gravado | `bot.log` |
| `SISTEMA` | Prompt de sistema (personalidade do bot) | assistente prestativo em português |

## Logs

Cada mensagem recebida e cada resposta enviada é registrada:

```
2026-09-30 11:40:02 - botollama - INFO - UPDATE 512 | Maria (id=123456789, @maria) | tipo=texto | texto='oi'
2026-09-30 11:40:05 - botollama - INFO - RESPOSTA para id=123456789 | 58 caracteres em 1 mensagem(ns):
Olá! Como posso ajudar você hoje?
```

Para acompanhar o log em tempo real no Windows:

```powershell
Get-Content bot.log -Wait -Tail 50 -Encoding UTF8
```

> **Privacidade:** o bot grava o texto das conversas no `bot.log`. Se outras pessoas usarem o bot, avise-as ou registre apenas metadados.

## Solução de problemas

| Erro | Causa provável | Solução |
|---|---|---|
| `model '...' not found (status code: 404)` | O modelo não foi baixado | Rode `ollama list` e ajuste `MODELO`, ou use `ollama pull` |
| `Não consegui falar com o Ollama` | O Ollama não está rodando | Abra o app do Ollama ou rode `ollama serve` |
| `Message is too long` | Resposta maior que 4096 caracteres | Já tratado pela função `dividir_texto` |
| `Defina a variável de ambiente TELEGRAM_TOKEN` | Token não definido | Veja a seção Configuração |
| `Unauthorized` | Token inválido | Confira o token ou gere outro no BotFather |

## Segurança

- O bot aceita mensagens de **qualquer usuário** que encontre o username dele, e cada mensagem usa o processamento da sua máquina.
- Para restringir o acesso, é possível filtrar por `update.effective_user.id` (use o comando `/id` para descobrir o seu).
- Mantenha `TELEGRAM_TOKEN` fora do repositório.

## Estrutura do projeto

```
BotOllama/
├── bot_com_log.py      # bot com logging completo
├── requirements.txt    # dependências
├── .gitignore
└── README.md
```

## Tecnologias

- [python-telegram-bot](https://python-telegram-bot.org)
- [ollama-python](https://github.com/ollama/ollama-python)
- [Ollama](https://ollama.com)

## Licença

Defina a licença do projeto (por exemplo, MIT) e adicione um arquivo `LICENSE`.
