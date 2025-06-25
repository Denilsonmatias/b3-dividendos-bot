import os
import requests
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Função para enviar mensagens
def send_message(message):
    bot = Bot(token=TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)

# Função que simula consulta de dividendos (aqui você pode adaptar com sua lógica real)
def verificar_dividendos():
    hoje = datetime.datetime.now().strftime("%d/%m/%Y")
    send_message(f"📢 Alerta de dividendos da B3 - {hoje}\n💰 Nenhum dividendo acima de R$2,00 foi identificado hoje.")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Olá! O bot B3 está ativo e pronto para enviar dividendos!")

# Comando /ajuda
async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🧾 *Comandos disponíveis:*\n\n"
        "/start - Iniciar o bot\n"
        "/ajuda - Mostrar esta lista de comandos\n"
        "/status - Verificar o status do envio automático\n"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

# Comando /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏰ O bot está programado para enviar dividendos automaticamente às 11:11h em dias úteis.")

# Inicialização do bot e agendamento
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("status", status))

    scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(verificar_dividendos, 'cron', day_of_week='mon-fri', hour=11, minute=11)
    scheduler.start()

    print("Bot iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main()
