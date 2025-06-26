import os
import asyncio
import logging
from datetime import datetime
import pytz
import requests

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
from dotenv import load_dotenv

# Carrega variáveis do ambiente
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Configura logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa o bot
bot = Bot(token=TOKEN)

# Função que busca dividendos simulados (substitua por scraping depois)
def buscar_dividendos():
    # Exemplo genérico; substitua por scraping real depois
    return [
        {"ativo": "MXRF11", "valor": 2.35},
        {"ativo": "TAEE11", "valor": 2.01},
        {"ativo": "ITUB4", "valor": 1.20},  # menor que 2
    ]

# Envia mensagem com dividendos acima de R$ 2,00
async def enviar_dividendos():
    logger.info("Verificando dividendos...")
    dividendos = buscar_dividendos()

    mensagem = ""
    for div in dividendos:
        if div["valor"] >= 2.00:
            mensagem += f"{div['ativo']}: R$ {div['valor']:.2f}\n"

    if mensagem:
        try:
            await bot.send_message(chat_id=CHAT_ID, text=f"📈 Dividendos acima de R$ 2,00:\n\n{mensagem}")
            logger.info("Mensagem enviada com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
    else:
        logger.info("Nenhum dividendo acima de R$ 2,00 hoje.")

# Configura agendamento
async def main():
    # Envia mensagem de teste ao iniciar
    await enviar_dividendos()

    # Inicia agendador
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("America/Sao_Paulo"))
    scheduler.add_job(
        enviar_dividendos,
        trigger=CronTrigger(hour=11, minute=11),
        id="dividendos_diarios"
    )
    scheduler.start()

    logger.info("Bot agendado para enviar dividendos diariamente às 11:11.")
    logger.info("Bot iniciado. Aguardando tarefas agendadas...")

    # Mantém o script rodando
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
