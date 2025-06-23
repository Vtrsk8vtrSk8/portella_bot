import os
import json
import logging
from datetime import datetime, timedelta
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from google.oauth2 import service_account
from googleapiclient.discovery import build
from utils.openai_helper import handle_natural_command
from utils.voice import transcribe_voice

# Configurações
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
TIMEZONE = os.getenv("TIMEZONE", "America/Sao_Paulo")
GOOGLE_CRED = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")

credentials = service_account.Credentials.from_service_account_info(GOOGLE_CRED)
service = build("calendar", "v3", credentials=credentials)

# Atividades
atividades_diarias = […]
estudos_semanais = […]

concluidos = set()

def agendar_evento(nome, hora, data=None):
    …

# [TODO: incluir funções: gerar_estudos_semana, agendar_rotina_diaria,
# eventos_do_dia, send_daily_agenda, start, done, relatorio, on_voice, on_text,
# send_course_recommendation, schedule_jobs]

def start_bot():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    # Handlers
    app.add_handler(CommandHandler("start", start))
    …
    app.run_polling()

if __name__ == "__main__":
    start_bot()
