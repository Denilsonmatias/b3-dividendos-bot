import os
import logging
import pytz
import time
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from asyncio import get_event_loop, run_coroutine_threadsafe

# Carrega variáveis do .env ou Render
load_dotenv()

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variáveis de ambiente
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise ValueError("TOKEN ou CHAT_ID não definidos")

# Bot do Telegram
bot = Bot(token=TOKEN)

# Função de envio de dividendos
def enviar_dividendos():
    logger.info("Verificando dividendos...")
    mensagem = "📈 Dividendos de hoje:\n- PETR4: R$ 2,01\n- ITSA4: R$ 2,10"
    try:
        loop = get_event_loop()
        run_coroutine_threadsafe(bot.send_message(chat_id=CHAT_ID, text=mensagem), loop)
        logger.info("Mensagem enviada com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")

# Agendador com timezone do Brasil (usando pytz)
scheduler = BackgroundScheduler(timezone=pytz.timezone("America/Sao_Paulo"))
scheduler.add_job(enviar_dividendos, 'cron', hour=11, minute=11)
scheduler.start()

logger.info("Bot agendado para enviar dividendos diariamente às 11:11.")
logger.info("Bot iniciado. Aguardando tarefas agendadas...")

try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
