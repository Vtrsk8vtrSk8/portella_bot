import os, json, logging
from datetime import datetime, timedelta
import pytz
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÕES ---
TOKEN = "6389209747:AAEpGRZxyHbLtJ1R_l6uvayv7bdnGeFuEkE"
USER_ID = 6715433690
TIMEZONE = "America/Sao_Paulo"
GOOGLE_CRED = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")

credentials = service_account.Credentials.from_service_account_info(GOOGLE_CRED)
service = build("calendar", "v3", credentials=credentials)

# --- FUNÇÕES ---
def eventos_do_dia(data):
    tz = pytz.timezone(TIMEZONE)
    inicio = tz.localize(datetime.combine(data, datetime.min.time()))
    fim = inicio + timedelta(days=1)
    return service.events().list(calendarId=CALENDAR_ID, timeMin=inicio.isoformat(), timeMax=fim.isoformat(), singleEvents=True, orderBy='startTime').execute().get('items', [])

def send_daily_agenda():
    bot = Bot(TOKEN)
    dia = datetime.now(pytz.timezone(TIMEZONE)) + timedelta(days=1)
    eventos = eventos_do_dia(dia.date())
    text = "Nenhum evento amanhã." if not eventos else "\n".join([f"{e['summary']} às {e['start']['dateTime'][11:16]}" for e in eventos])
    bot.send_message(USER_ID, f"📅 Agenda de amanhã:\n{text}")

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Olá! Portella Bot ativo e pronto para te ajudar!")

async def relatorio(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    hoje = datetime.now(pytz.timezone(TIMEZONE)).date()
    eventos = eventos_do_dia(hoje)
    if not eventos:
        await update.message.reply_text("✅ Nada marcado hoje.")
        return
    texto = "\n".join([
        f"📌 {e['summary']} — {e['start']['dateTime'][11:16]}"
        for e in eventos
    ])
    await update.message.reply_text(f"📋 Agenda de hoje:\n{texto}")

def main():
    logging.basicConfig(level=logging.INFO)
    scheduler = BackgroundScheduler(timezone=TIMEZONE)
    scheduler.add_job(send_daily_agenda, "cron", hour=23, minute=0)
    scheduler.start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("relatorio", relatorio))
    app.run_polling()

if __name__ == "__main__":
    main()
