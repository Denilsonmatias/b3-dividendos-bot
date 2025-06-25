import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot de dividendos ativo!")

def buscar_dividendos():
    headers = {'User-Agent': 'Mozilla/5.0'}
    tickers = ['VALE3', 'BBSE3', 'UNIP6', 'TAEE11', 'PETR4', 'ITUB4']
    resultados = []

    for ticker in tickers:
        try:
            r = requests.get(f"https://statusinvest.com.br/acao/getevents?ticker={ticker}", headers=headers)
            if r.status_code == 200:
                eventos = r.json()
                for evento in eventos:
                    if evento["value"] >= 2.0 and evento["type"] in ["Dividendos", "JCP"]:
                        resultados.append(f"✅ {ticker} - R$ {evento['value']} - {evento['paymentDate']}")
        except:
            continue
    return "\n".join(resultados) or "🔔 Nenhum dividendo acima de R$2,00."

async def dividendos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = buscar_dividendos()
    await update.message.reply_text(msg)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dividendos", dividendos))
    app.run_polling()
