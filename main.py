import os
import json
import logging
from datetime import datetime, timedelta
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from google.oauth2 import service_account
from googleapiclient.discovery import build
from utils.calendar import gerar_estudos_semana, agendar_rotina_diaria, eventos_do_dia, agendar_evento
from utils.openai_helper import handle_natural_command
from utils.voice import transcribe_voice

# CONFIGURAÇÕES FIXAS PARA O VICTOR
TOKEN = "7462953420:AAGaLE5W-IO5ZVLm0BSz4sh9-0fQk0inRms"
USER_ID = 7815691606
TIMEZONE = "America/Sao_Paulo"
CALENDAR_ID = "primary"
GOOGLE_CRED = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))

credentials = service_account.Credentials.from_service_account_info(GOOGLE_CRED)
service = build("calendar", "v3", credentials=credentials)
concluidos = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fala! Eu sou o Portella 🤖. Estou pronto pra organizar tua agenda!")

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Diz o nome do evento que você concluiu. Ex: /done Leitura")
        return
    nome = " ".join(context.args)
    concluidos.add(nome.lower())
    await update.message.reply_text(f"✅ Marquei '{nome}' como concluído.")

async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hoje = datetime.now(pytz.timezone(TIMEZONE)).date()
    semana = [hoje + timedelta(days=i) for i in range(7)]
    resposta = []
    for dia in semana:
        eventos = eventos_do_dia(service, dia)
        for e in eventos:
            nome = e["summary"]
            status = "✅" if nome.lower() in concluidos else "❌"
            resposta.append(f"{status} {nome} - {dia.strftime('%a %d/%m')}")
    await update.message.reply_text("\n".join(resposta))

async def on_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await context.bot.get_file(update.message.voice.file_id)
    path = await file.download_to_drive()
    comando = transcribe_voice(str(path))
    if comando:
        msg = handle_natural_command(comando, service)
        await update.message.reply_text(msg)

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    msg = handle_natural_command(texto, service)
    await update.message.reply_text(msg)

def send_agenda(tipo="hoje"):
    from telegram import Bot
    bot = Bot(token=TOKEN)
    tz = pytz.timezone(TIMEZONE)
    hoje = datetime.now(tz).date()
    if tipo == "amanha":
        dia = hoje + timedelta(days=1)
    else:
        dia = hoje
    eventos = eventos_do_dia(service, dia)
    if not eventos:
        agenda = "Nenhum compromisso para " + tipo + "."
    else:
        agenda = "\n".join([f"{e['summary']} às {e['start']['dateTime'][11:16]}" for e in eventos])
    bot.send_message(chat_id=USER_ID, text=f"📅 Agenda de {tipo} ({dia.strftime('%d/%m')}):\n{agenda}")

def start_bot():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("relatorio", relatorio))
    app.add_handler(MessageHandler(filters.VOICE, on_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    scheduler = BackgroundScheduler(timezone=TIMEZONE)
    scheduler.add_job(lambda: send_agenda("hoje"), "cron", hour=7, minute=0)
    scheduler.add_job(lambda: send_agenda("amanha"), "cron", hour=23, minute=0)
    scheduler.add_job(lambda: send_agenda("amanha"), "cron", hour=22, minute=0)
    scheduler.start()

    gerar_estudos_semana(service, TIMEZONE)
    agendar_rotina_diaria(service, TIMEZONE)
    app.run_polling()

if __name__ == "__main__":
    start_bot()