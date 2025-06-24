import os
import json
import logging
from datetime import datetime, timedelta
import pytz
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from apscheduler.schedulers.background import BackgroundScheduler
from google.oauth2 import service_account
from googleapiclient.discovery import build
from utils.openai_helper import handle_natural_command
from utils.voice import transcribe_voice

TOKEN = "7462953420:AAGaLE5W-IO5ZVLm0BSz4sh9-0fQk0inRms"
USER_ID = 7815691606
TIMEZONE = "America/Sao_Paulo"
CALENDAR_ID = "primary"
GOOGLE_CREDENTIALS_JSON = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
credentials = service_account.Credentials.from_service_account_info(GOOGLE_CREDENTIALS_JSON)
service = build("calendar", "v3", credentials=credentials)

atividades_diarias = [
    {"nome": "Acordar", "hora": "07:00"},
    {"nome": "Leitura", "hora": "07:30"},
    {"nome": "Treino", "hora": "18:00"}
]

estudos_semanais = [
    ("Inteligência Artificial", 3),
    ("Investimentos", 2),
    ("Produção Musical", 1),
    ("Administração de Empresas", 1),
]

concluidos = set()

def start_bot():
    logging.basicConfig(level=logging.INFO)
    scheduler = BackgroundScheduler(timezone=TIMEZONE)
    scheduler.start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", lambda update, context: update.message.reply_text("Portella está ativo!")))
    app.run_polling()

if __name__ == "__main__":
    start_bot()