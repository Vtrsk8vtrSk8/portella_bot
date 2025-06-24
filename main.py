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

# -------- CONFIGURAÇÕES --------
TOKEN = "7462953420:AAGaLE5W-IO5ZVLm0BSz4sh9-0fQk0inRms"
USER_ID = 7815691606
TIMEZONE = "America/Sao_Paulo"
CALENDAR_ID = "primary"

GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
GOOGLE_CRED = json.loads(GOOGLE_CREDENTIALS_JSON)

credentials = service_account.Credentials.from_service_account_info(GOOGLE_CRED)
service = build("calendar", "v3", credentials=credentials)

# -------- TAREFAS --------
atividades_diarias = [
    {"nome": "Acordar", "hora": "07:00"},
    {"nome": "Leitura", "hora": "07:30"},
    {"nome": "Treino", "hora": "18:00"}
]

estudos_semanais = [
    ("Inteligência Artificial", 3),
    ("Investimentos", 2),
    ("Produção Musical", 1),
    ("Administração de Empresas", 1)
]

concluidos = set()

# -------- FUNÇÕES --------
def agendar_evento(nome, hora, data=None):
    tz = pytz.timezone(TIMEZONE)
    if not data:
        data = datetime.now(tz)
    else:
        if isinstance(data, datetime):
            data = tz.localize(data)
        else:
            data = tz.localize(datetime.combine(data, datetime.strptime(hora, "%H:%M").time()))

    inicio = data
    fim = inicio + timedelta(hours=1)

    evento = {
        'summary': nome,
        'start': {'dateTime': inicio.isoformat(), 'timeZone': TIMEZONE},
        'end': {'dateTime': fim.isoformat(), 'timeZone': TIMEZONE},
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 15},
                {'method': 'popup', 'minutes': 0},
            ],
        },
    }
    service.events().insert(calendarId=CALENDAR_ID, body=evento).execute()

def gerar_estudos_semana():
    hoje = datetime.now(pytz.timezone(TIMEZONE)).date()
    dias_disponiveis = [hoje + timedelta(days=i) for i in range(7)]
    pos = 0
    for nome, qtd in estudos_semanais:
        for _ in range(qtd):
            data = dias_disponiveis[pos]
            agendar_evento(nome, "20:00", data)
            pos = (pos + 1) % len(dias_disponiveis)

def agendar_rotina_diaria():
    hoje = datetime.now(pytz.timezone(TIMEZONE)).date()
    for i in range(7):
        dia = hoje + timedelta(days=i)
        for atividade in atividades_diarias:
            agendar_evento(atividade["nome"], atividade["hora"], dia)

def eventos_do_dia(data):
    tz = pytz.timezone(TIMEZONE)
    inicio = tz.localize(datetime.combine(data, datetime.min.time()))
    fim = inicio + timedelta(days=1)
    eventos = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=inicio.isoformat(),
        timeMax=fim.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])
    return eventos

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Eu sou o Portella Bot. Pronto para gerenciar sua agenda!")

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Informe a tarefa concluída. Ex: /done Leitura")
        return
    nome = " ".join(context.args)
    concluidos.add(nome.lower())
    await update.message.reply_text(f"✔️ Atividade marcada como concluída: {nome}")

async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hoje = datetime.now(pytz.timezone(TIMEZONE)).date()
    semana = [hoje + timedelta(days=i) for i in range(7)]
    relatorio = []
    for dia in semana:
        eventos = eventos_do_dia(dia)
        for e in eventos:
            nome = e["summary"]
            status = "✅" if nome.lower() in concluidos else "❌"
            relatorio.append(f"{status} {nome} - {dia.strftime('%A, %d/%m')}")
    await update.message.reply_text("\n".join(relatorio))

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resposta = handle_natural_command(update.message.text)
    await update.message.reply_text(resposta)

async def on_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.voice.get_file()
    audio_path = "voice.ogg"
    await file.download_to_drive(audio_path)
    comando = transcribe_voice(audio_path)
    resposta = handle_natural_command(comando)
    await update.message.reply_text(resposta)

def send_daily_agenda():
    tz = pytz.timezone(TIMEZONE)
    hoje = datetime.now(tz).date()
    eventos = eventos_do_dia(hoje)
    if not eventos:
        agenda = "Nenhum compromisso para hoje."
    else:
        agenda = "\n".join([f"🕒 {e['summary']} às {e['start']['dateTime'][11:16]}" for e in eventos])
    bot = Bot(token=TOKEN)
    bot.send_message(chat_id=USER_ID, text=f"📅 Agenda do dia:\n{agenda}")

def start_bot():
    logging.basicConfig(level=logging.INFO)
    scheduler = BackgroundScheduler(timezone=TIMEZONE)
    scheduler.add_job(send_daily_agenda, "cron", hour=7, minute=0)
    scheduler.start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("relatorio", relatorio))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_handler(MessageHandler(filters.VOICE, on_voice))
    app.run_polling()

if __name__ == "__main__":
    gerar_estudos_semana()
    agendar_rotina_diaria()
    start_bot()
