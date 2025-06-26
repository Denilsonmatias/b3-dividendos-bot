import os
import logging
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot
from datetime import datetime
import pytz

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Variáveis de ambiente
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

def buscar_dividendos_fiis():
    url = "https://www.fundsexplorer.com.br/ranking"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        tabela = soup.find("table")
        if not tabela:
            logging.error("Tabela de FIIs não encontrada no Funds Explorer.")
            return []

        linhas = tabela.find_all("tr")[1:]
        dividendos = []

        for linha in linhas:
            colunas = linha.find_all("td")
            if len(colunas) >= 11:
                codigo = colunas[0].text.strip()
                rendimento = colunas[5].text.strip().replace("R$", "").replace(",", ".")
                try:
                    valor = float(rendimento)
                    if valor >= 2.00:
                        dividendos.append(f"{codigo}: R${valor:.2f}")
                except ValueError:
                    continue

        return dividendos

    except Exception as e:
        logging.error(f"Erro ao buscar dividendos: {e}")
        return []

def enviar_dividendos():
    dividendos = buscar_dividendos_fiis()
    if not dividendos:
        mensagem = "Nenhum FII com dividendos acima de R$2,00 encontrado hoje."
    else:
        mensagem = "📈 FIIs com dividendos acima de R$2,00:\n" + "\n".join(dividendos)

    try:
        bot.send_message(chat_id=CHAT_ID, text=mensagem)
        logging.info("Mensagem enviada com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao enviar mensagem: {e}")

# Agendamento
scheduler = BackgroundScheduler(timezone=pytz.timezone("America/Sao_Paulo"))
scheduler.add_job(enviar_dividendos, 'cron', hour=11, minute=11)
scheduler.start()

logging.info("Bot agendado para enviar dividendos diariamente às 11:11.")
logging.info("Bot iniciado. Aguardando tarefas agendadas...")

# Manter o script em execução
import time
while True:
    time.sleep(60)
