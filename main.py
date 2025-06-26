import logging
import os
import requests
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from datetime import datetime
import pytz

# Carrega variáveis do arquivo .env
load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Instancia o bot
bot = Bot(token=TOKEN)

def enviar_dividendos():
    try:
        logger.info("Verificando dividendos...")

        # Aqui é um exemplo fixo, você pode trocar pelo web scraping real depois
        mensagem = "📈 Ação XPTO3 vai pagar R$ 2,34 por ação em 30/06/2025."

        bot.send_message(chat_id=CHAT_ID, text=mensagem)
        logger.info("Mensagem enviada com sucesso.")

    except Exception as e:
        logger.error(f"Erro ao enviar dividendos: {e}")

# Agenda a execução para 11:11 (horário de Brasília)
def agendar_envio():
    fuso = pytz.timezone("America/Sao_Paulo")
    scheduler = BackgroundScheduler(timezone=fuso)

    # Segunda a sexta (dias úteis), às 11:11h
    scheduler.add_job(enviar_dividendos, 'cron', day_of_week='mon-fri', hour=11, minute=11)
    scheduler.start()

    logger.info("Bot agendado para enviar dividendos diariamente às 11:11.")

if __name__ == "__main__":
    try:
        enviar_dividendos()  # opcional: envia na inicialização
        agendar_envio()
        logger.info("Bot iniciado. Aguardando tarefas agendadas...")

        # Mantém o bot rodando
        import time
        while True:
            time.sleep(60)

    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}")
