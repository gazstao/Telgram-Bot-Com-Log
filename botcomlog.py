import os
import logging

import ollama
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    TypeHandler,
    filters,
)

# ---------------- Configuração ----------------
MODELO = "aiconjured/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-MTP-GGUF-NVFP4:latest"
LIMITE_TELEGRAM = 4000          # o Telegram aceita no máximo 4096 caracteres
MAX_MENSAGENS_HISTORICO = 20    # quantas mensagens recentes enviar ao modelo
ARQUIVO_LOG = "bot.log"

SISTEMA = {
    "role": "system",
    "content": "Você é um assistente prestativo. Responda em português, de forma objetiva e concisa.",
}

# ---------------- Logging (terminal + arquivo) ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(ARQUIVO_LOG, encoding="utf-8"),
    ],
)
# Mostra as chamadas HTTP à API do Telegram (getUpdates, sendMessage).
# Troque INFO por WARNING se achar barulhento demais.
logging.getLogger("httpx").setLevel(logging.INFO)
logger = logging.getLogger("botollama")

client = ollama.AsyncClient()


# ---------------- Funções auxiliares ----------------
def dividir_texto(texto: str, limite: int = LIMITE_TELEGRAM) -> list[str]:
    """Quebra o texto em pedaços que cabem em uma mensagem do Telegram."""
    partes = []
    while len(texto) > limite:
        corte = texto.rfind("\n", 0, limite)
        if corte == -1:
            corte = texto.rfind(" ", 0, limite)
        if corte == -1:
            corte = limite
        partes.append(texto[:corte].strip())
        texto = texto[corte:].strip()
    if texto:
        partes.append(texto)
    return partes


# ---------------- Log de tudo que chega ----------------
async def logar_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Registra qualquer update recebido, antes dos outros handlers."""
    if update.message:
        user = update.effective_user
        texto = update.message.text
        if texto is None:
            tipo = "outro (foto, áudio, sticker...)"
        elif texto.startswith("/"):
            tipo = "comando"
        else:
            tipo = "texto"
        logger.info(
            "UPDATE %s | %s (id=%s, @%s) | tipo=%s | texto=%r",
            update.update_id,
            user.first_name,
            user.id,
            user.username,
            tipo,
            texto,
        )


# ---------------- Comandos ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["historico"] = [SISTEMA]
    await update.message.reply_text(
        "Oi! Me mande uma mensagem. Use /limpar para zerar a conversa."
    )


async def limpar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["historico"] = [SISTEMA]
    await update.message.reply_text("Conversa reiniciada.")


async def mostrar_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Seu ID: {update.effective_user.id}")


# ---------------- Resposta às mensagens ----------------
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    historico = context.user_data.setdefault("historico", [SISTEMA])
    historico.append({"role": "user", "content": update.message.text})

    await update.message.chat.send_action("typing")

    try:
        mensagens = [SISTEMA] + historico[1:][-MAX_MENSAGENS_HISTORICO:]
        resp = await client.chat(model=MODELO, messages=mensagens)
        texto = resp["message"]["content"].strip()
    except Exception:
        logger.exception("Erro ao chamar o Ollama")
        historico.pop()  # remove a pergunta que falhou
        await update.message.reply_text(
            "Não consegui falar com o Ollama. Verifique se ele está rodando."
        )
        return

    if not texto:
        texto = "Não consegui gerar uma resposta."

    historico.append({"role": "assistant", "content": texto})

    partes = dividir_texto(texto)
    logger.info(
        "RESPOSTA para id=%s | %d caracteres em %d mensagem(ns) | início=%r",
        update.effective_user.id,
        len(texto),
        len(partes),
        texto,
    )

    for parte in partes:
        await update.message.reply_text(parte)


# ---------------- Erros não tratados ----------------
async def tratar_erro(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Erro não tratado", exc_info=context.error)


# ---------------- Inicialização ----------------
def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise SystemExit("Defina a variável de ambiente TELEGRAM_TOKEN antes de rodar.")

    app = ApplicationBuilder().token(token).build()

    # group=-1 roda antes dos demais handlers, sem impedi-los de executar
    app.add_handler(TypeHandler(Update, logar_update), group=-1)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("limpar", limpar))
    app.add_handler(CommandHandler("id", mostrar_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.add_error_handler(tratar_erro)

    logger.info("Bot rodando... (log também em %s)", ARQUIVO_LOG)
    app.run_polling()


if __name__ == "__main__":
    main()
