import os
import logging
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obter token e chat_id do ambiente
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Verificação de segurança
if not TOKEN or not CHAT_ID:
    logger.error("TOKEN ou CHAT_ID não foram definidos nas variáveis de ambiente.")
    raise ValueError("TOKEN ou CHAT_ID ausentes.")

# Criar instância do bot
bot = Bot(token=TOKEN)

# Função para buscar e enviar dividendos
def enviar_dividendos():
    logger.info("Verificando dividendos...")

    # Exemplo de mensagem simulada
    mensagem = "📈 Dividendos de hoje:\n- PETR4: R$ 2,01\n- ITSA4: R$ 2,10"

    # Enviar mensagem
    try:
        # CORREÇÃO: uso de 'await' com run_coroutine_threadsafe
        from asyncio import get_event_loop, run_coroutine_threadsafe
        loop = get_event_loop()
        run_coroutine_threadsafe(bot.send_message(chat_id=CHAT_ID, text=mensagem), loop)
        logger.info("Mensagem enviada com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")

# Agendar a tarefa
scheduler = BackgroundScheduler()
scheduler.add_job(enviar_dividendos, 'cron', hour=11, minute=11)
scheduler.start()

logger.info("Bot agendado para enviar dividendos diariamente às 11:11.")
logger.info("Bot iniciado. Aguardando tarefas agendadas...")

# Manter a aplicação rodando
import time
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
