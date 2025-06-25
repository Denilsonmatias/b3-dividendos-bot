import logging
import os
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

bot = Bot(token=TOKEN)

# ---------------------- FONTES ----------------------

def buscar_dividendos_statusinvest(ticker):
    url = f"https://statusinvest.com.br/acao/getevents?ticker={ticker}"
    try:
        r = requests.get(url)
        if r.ok:
            for e in r.json():
                if e["value"] >= 2 and e["type"] in ["Dividendos", "JCP"]:
                    yield {
                        "fonte": "StatusInvest",
                        "ticker": ticker,
                        "valor": e["value"],
                        "data": e["paymentDate"]
                    }
    except Exception as err:
        logging.error(f"Erro StatusInvest {ticker}: {err}")

def buscar_dividendos_fundsexplorer(ticker):
    try:
        r = requests.get("https://fundsexplorer.com.br/wp-json/funds/v1/get-ranking")
        if r.ok:
            for f in r.json():
                if f["ticker"] == ticker and float(f.get("dividendo", 0)) >= 2:
                    yield {
                        "fonte": "Fundsexplorer",
                        "ticker": ticker,
                        "valor": float(f["dividendo"]),
                        "data": f.get("data_pagamento", "") or f.get("data_ex", "")
                    }
    except Exception as err:
        logging.error(f"Erro Fundsexplorer {ticker}: {err}")

# ---------------------- AÇÃO PRINCIPAL ----------------------

def verificar_dividendos():
    tickers = ["MXRF11", "PETR4", "ITUB3"]  # Atualize conforme necessário
    resultados = []
    for ticker in tickers:
        resultados.extend(buscar_dividendos_statusinvest(ticker))
        resultados.extend(buscar_dividendos_fundsexplorer(ticker))

    if resultados:
        mensagem = "\u2705 DIVIDENDOS ENCONTRADOS:\n"
        for r in resultados:
            mensagem += f"{r['fonte']} | {r['ticker']} - R$ {r['valor']:.2f} em {r['data']}\n"
    else:
        mensagem = "Nenhum dividendo \u2265 R$2,00 encontrado hoje."

    bot.send_message(chat_id=CHAT_ID, text=mensagem)

# ---------------------- COMANDOS BOT ----------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot B3 Ativo! Use /status para consultar dividendos.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    verificar_dividendos()
    await update.message.reply_text("Consulta enviada para o grupo.")

# ---------------------- APLICAÇÃO E SCHEDULER ----------------------

if __name__ == '__main__':
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("status", status))

        scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
        scheduler.add_job(verificar_dividendos, 'cron', day_of_week='mon-fri', hour=11, minute=11)
        scheduler.start()

        app.run_polling()

    except Exception as e:
        logging.error(f"Erro ao iniciar o bot: {e}")
