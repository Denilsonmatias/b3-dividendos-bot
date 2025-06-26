import os
import logging
import requests
import pytz
from telegram import Bot, Update
from telegram.ext import CommandHandler, ApplicationBuilder
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from datetime import datetime

# Carrega variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa o bot
bot = Bot(token=TOKEN)

def buscar_dividendos():
    try:
        url = "https://dividend-yield-api.vercel.app/api/b3"
        response = requests.get(url)
        data = response.json()

        mensagem = "📈 *Dividendos acima de R$2,00 por ação/cota:*\n\n"
        encontrou = False

        for ativo in data:
            valor = ativo.get("valor", 0)
            if valor and float(valor.replace("R$", "").replace(",", ".")) >= 2:
                codigo = ativo.get("codigo", "N/A")
                pagamento = ativo.get("dataPagamento", "Data N/D")
                mensagem += f"🔹 {codigo}: *{valor}* → Pagamento em *{pagamento}*\n"
                encontrou = True

        if not encontrou:
            mensagem = "⚠️ Nenhum dividendo acima de R$2,00 encontrado hoje."

        return mensagem

    except Exception as e:
        logger.error(f"Erro ao buscar dividendos: {e}")
        return "❌ Erro ao buscar dividendos."

async def enviar_dividendos():
    mensagem = buscar_dividendos()
    try:
        await bot.send_message(chat_id=CHAT_ID, text=mensagem, parse_mode="Markdown")
        logger.info("Mensagem enviada com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")

# Comandos do bot
async def ajuda(update: Update, _):
    await update.message.reply_text("🤖 Comandos disponíveis:\n/status – Verifica se o bot está ativo\n/ajuda – Mostra esta mensagem")

async def status(update: Update, _):
    await update.message.reply_text("✅ Bot está rodando e agendado para 11:11.")

# Inicialização principal
if __name__ == "__main__":
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("ajuda", ajuda))
        app.add_handler(CommandHandler("status", status))

        # Agenda a tarefa
        scheduler = BackgroundScheduler(timezone=pytz.timezone("America/Sao_Paulo"))
        scheduler.add_job(lambda: app.create_task(enviar_dividendos()), 'cron', hour=11, minute=11)
        scheduler.start()

        logger.info("Bot agendado para enviar dividendos diariamente às 11:11.")
        logger.info("Bot iniciado. Aguardando tarefas agendadas...")

        app.run_polling()
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}")
