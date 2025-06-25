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

# Simulação de carteira personalizada
carteira = ['PETR4', 'MXRF11', 'VGIR11', 'SYNE3']

def buscar_dividendos():
    headers = {'User-Agent': 'Mozilla/5.0'}
    dividendos_validos = []
    tickers = list(set(carteira + ['VALE3', 'BBSE3', 'UNIP6', 'TAEE11', 'ITUB4']))

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
        mensagem = "\U0001F31F Dividendos acima de R$ 2,00:\n"
        for d in dividendos:
            mensagem += f"\n\u2705 {d['acao']}: R$ {d['valor']} (pagamento: {d['data_pagamento']})"
    else:
        mensagem = "\U0001F4E3 Nenhuma ação/FII com dividendos acima de R$ 2,00 no momento."

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)

def teste_command(update: Update, context: CallbackContext):
    update.message.reply_text("\U0001F4E2 Bot de Dividendos funcionando perfeitamente!")

def hoje_command(update: Update, context: CallbackContext):
    hoje = datetime.datetime.now().strftime("%Y-%m-%d")
    resultados = []
    for d in buscar_dividendos():
        if d["data_pagamento"] == hoje:
            resultados.append(d)
    if resultados:
        msg = "\U0001F4C6 Dividendos com pagamento HOJE:\n"
        for d in resultados:
            msg += f"\n\u2705 {d['acao']}: R$ {d['valor']}"
    else:
        msg = "\U0001F4ED Nenhum dividendo com pagamento hoje."
    update.message.reply_text(msg)

def semana_command(update: Update, context: CallbackContext):
    hoje = datetime.datetime.now()
    inicio_semana = hoje - datetime.timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + datetime.timedelta(days=6)

    resultados = []
    for d in buscar_dividendos():
        try:
            data = datetime.datetime.strptime(d["data_pagamento"], "%Y-%m-%d")
            if inicio_semana.date() <= data.date() <= fim_semana.date():
                resultados.append(d)
        except:
            continue
    if resultados:
        msg = "\U0001F4C6 Dividendos previstos para esta semana:\n"
        for d in resultados:
            msg += f"\n\u2705 {d['acao']}: R$ {d['valor']} (pagamento: {d['data_pagamento']})"
    else:
        msg = "\U0001F4ED Nenhum dividendo previsto para esta semana."
    update.message.reply_text(msg)

def carteira_command(update: Update, context: CallbackContext):
    msg = "\U0001F4CA Sua carteira atual:\n"
    for ativo in carteira:
        msg += f"• {ativo}\n"
    update.message.reply_text(msg)

def ajuda_command(update: Update, context: CallbackContext):
    msg = (
        "\U0001F4D8 Comandos disponíveis:\n\n"
        "/hoje - Dividendos com pagamento hoje\n"
        "/semana - Dividendos previstos para esta semana\n"
        "/carteira - Exibe sua carteira\n"
        "/ajuda - Mostra esta ajuda"
    )
    update.message.reply_text(msg)

if __name__ == "__main__":
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("teste", teste_command))
    dp.add_handler(CommandHandler("hoje", hoje_command))
    dp.add_handler(CommandHandler("semana", semana_command))
    dp.add_handler(CommandHandler("carteira", carteira_command))
    dp.add_handler(CommandHandler("ajuda", ajuda_command))

    updater.start_polling()

    while True:
        now = datetime.datetime.now()
        if now.weekday() < 5 and now.hour == HORA_ENVIO and now.minute == MINUTO_ENVIO:
            enviar_mensagem()
            time.sleep(60)
        else:
            time.sleep(10)
