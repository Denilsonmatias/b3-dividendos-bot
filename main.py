import os
import logging
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise ValueError("Você deve configurar TOKEN e CHAT_ID nas variáveis de ambiente.")

bot = Bot(token=TOKEN)

# Função para buscar dividendos reais de FIIs do FundsExplorer
def buscar_dividendos():
    url = "https://www.fundsexplorer.com.br/ranking"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resposta = requests.get(url, headers=headers)
        soup = BeautifulSoup(resposta.content, "html.parser")
        tabela = soup.find("table")

        dividendos_altos = []

        if tabela:
            linhas = tabela.find_all("tr")[1:]  # pula o cabeçalho
            for linha in linhas:
                colunas = linha.find_all("td")
                if len(colunas) >= 10:
                    codigo = colunas[0].text.strip()
                    dy = colunas[5].text.strip().replace("R$", "").replace(",", ".")
                    try:
                        dy_float = float(dy)
                        if dy_float >= 2.0:
                            dividendos_altos.append(f"{codigo}: R$ {dy_float:.2f}")
                    except ValueError:
                        continue

        return dividendos_altos
    except Exception as e:
        logging.error(f"Erro ao buscar dados: {e}")
        return []

# Enviar mensagem com os dividendos
async def enviar_dividendos():
    logging.info("Verificando dividendos...")

    dividendos = buscar_dividendos()

    if dividendos:
        mensagem = "💸 FIIs com dividendos acima de R$ 2,00:\n\n" + "\n".join(dividendos)
    else:
        mensagem = "Nenhum FII com dividendos acima de R$ 2,00 foi encontrado hoje."

    try:
        await bot.send_message(chat_id=CHAT_ID, text=mensagem)
        logging.info("Mensagem enviada com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao enviar mensagem: {e}")

# Agendar tarefa
async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(enviar_dividendos, 'cron', hour=11, minute=11)
    scheduler.start()

    logging.info("Bot agendado para enviar dividendos diariamente às 11:11.")
    logging.info("Bot iniciado. Aguardando tarefas agendadas...")

    while True:
        await asyncio.sleep(60)

# Iniciar
if __name__ == "__main__":
    asyncio.run(main())
