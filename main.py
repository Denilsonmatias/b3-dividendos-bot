import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# Carrega variáveis do .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Configura logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Mensagem principal
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Olá! O bot B3 está ativo e pronto para enviar dividendos!")

# Busca os dividendos acima de R$2,00 por cota
def verificar_dividendos():
    try:
        url = "https://dividendobr.com/api/dividendos"
        response = requests.get(url)
        response.raise_for_status()
        dividendos = response.json()

        mensagens = []
        for ativo in dividendos:
            valor = ativo.get("valor", 0)
            if valor >= 2:
                mensagens.append(f"💰 {ativo['codigo']} pagará R${valor:.2f} por cota em {ativo['data_pagamento']}")

        if mensagens:
            mensagem_final = "\n".join(mensagens)
        else:
            mensagem_final = "Nenhum dividendo acima de R$2,00 encontrado hoje."

        send_message(mensagem_final)

    except Exception as e:
        logging.error(f"Erro ao verificar dividendos: {e}")

# Envia a mensagem para o Telegram
def send_message(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem}
    requests.post(url, data=payload)

# Agendador
def agendar_tarefa_diaria(app):
    scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(verificar_dividendos, trigger='cron', day_of_week='mon-fri', hour=11, minute=11)
    scheduler.start()

# Inicializa o bot
if __name__ == '__main__':
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        agendar_tarefa_diaria(app)

        print("Bot iniciado com sucesso.")
        app.run_polling(stop_signals=None)  # Sem sinais do sistema (ideal para Render)

    except Exception as e:
        logging.error(f"Erro ao iniciar o bot: {e}")
