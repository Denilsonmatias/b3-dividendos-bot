import os
import logging
import datetime
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Configurações de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Token do Telegram via variável de ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    logger.error("Erro ao iniciar o bot: You must pass the token you received from https://t.me/Botfather!")
    exit(1)

# ID do chat do usuário (pode ser automatizado depois)
USER_CHAT_ID = os.getenv("USER_CHAT_ID")

# Inicializa o bot e scheduler
bot = Bot(token=TELEGRAM_TOKEN)
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher
scheduler = BackgroundScheduler()

# Comando /ajuda
def ajuda(update: Update, context: CallbackContext):
    mensagem = (
        "📌 *Comandos disponíveis:*\n"
        "/ajuda - Mostra esta mensagem\n"
        "/status - Verifica se o bot está ativo"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=mensagem, parse_mode="Markdown")

# Comando /status
def status(update: Update, context: CallbackContext):
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ Bot está funcionando.\n⏱️ Agora: {agora}")

# Função para envio automático de mensagem diária
def enviar_mensagem_diaria():
    try:
        hoje = datetime.datetime.now().date()
        if hoje.weekday() < 5:  # Segunda (0) a sexta (4)
            mensagem = f"📈 Atualização B3: Hoje é {hoje.strftime('%d/%m/%Y')} às 11:11h."
            bot.send_message(chat_id=USER_CHAT_ID, text=mensagem)
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem diária: {e}")

# Agendamento para 11:11h de segunda a sexta
scheduler.add_job(enviar_mensagem_diaria, 'cron', day_of_week='mon-fri', hour=11, minute=11, timezone='America/Sao_Paulo')
scheduler.start()

# Handlers de comandos
dispatcher.add_handler(CommandHandler("ajuda", ajuda))
dispatcher.add_handler(CommandHandler("status", status))

# Inicia o bot
if __name__ == '__main__':
    logger.info("🚀 Bot iniciado com sucesso.")
    updater.start_polling()
    updater.idle()
