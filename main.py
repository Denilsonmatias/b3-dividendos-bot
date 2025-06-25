import os
import datetime
import time
import requests
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Carrega variáveis do arquivo .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

HORA_ENVIO = 11
MINUTO_ENVIO = 11

def buscar_dividendos():
    headers = {'User-Agent': 'Mozilla/5.0'}
    dividendos_validos = []
    tickers = ['VALE3', 'BBSE3', 'UNIP6', 'TAEE11', 'PETR4', 'ITUB4']

    for ticker in tickers:
        try:
            url = f"https://statusinvest.com.br/acao/getevents?ticker={ticker}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                dados = response.json()
                for evento in dados:
                    valor = evento.get("value", 0)
                    data_pagamento = evento.get("paymentDate", "")
                    tipo = evento.get("type", "")
                    if valor >= 2.0 and tipo in ["Dividendos", "JCP"]:
                        dividendos_validos.append({
                            'acao': ticker,
                            'valor': valor,
                            'data_pagamento': data_pagamento
                        })
        except Exception as e:
            print(f"Erro ao buscar {ticker}: {e}")

    return dividendos_validos

def enviar_mensagem():
    dividendos = buscar_dividendos()
    if dividendos:
        mensagem = "🌟 Dividendos acima de R$ 2,00:\n"
        for d in dividendos:
            mensagem += f"\n✅ {d['acao']}: R$ {d['valor']} (pagamento: {d['data_pagamento']})"
    else:
        mensagem = "📢 Nenhuma ação/FII com dividendos acima de R$ 2,00 no momento."

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)

def teste_command(update: Update, context: CallbackContext):
    update.message.reply_text("📢 [B3] Bot de Dividendos funcionando!")

if __name__ == "__main__":
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("teste", teste_command))
    updater.start_polling()

    while True:
        now = datetime.datetime.now()
        if now.weekday() < 5 and now.hour == HORA_ENVIO and now.minute == MINUTO_ENVIO:
            enviar_mensagem()
            time.sleep(60)
        else:
            time.sleep(10)
