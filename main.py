import os
import json
import logging
from datetime import datetime, timedelta
import pytz
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from google.oauth2 import service_account
from googleapiclient.discovery import build

# =============== CONFIGURAÇÕES ==================

TELEGRAM_BOT_TOKEN = "7462953420:AAGaLE5W-IO5ZVLm0BSz4sh9-0fQk0inRms"
TELEGRAM_USER_ID = 7815691606
TIMEZONE = "America/Sao_Paulo"
CALENDAR_ID = "primary"

GOOGLE_CREDENTIALS_JSON = os.environ["GOOGLE_CREDENTIALS_JSON"]
creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
credentials = service_account.Credentials.from_service_account_info(creds_dict)
service = build("calendar", "v3", credentials=credentials)

# =============== ATIVIDADES FIXAS ==================

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

# =============== FUNÇÕES AUXILIARES ==================

def agendar_evento(nome, hora, data=None):
    tz = pytz.timezone(TIMEZONE)
    if not data:
        data = datetime.now(tz)
    else:
        if isinstance(data, datetime):
            data = data.date()
        data = datetime.combine(data, datetime.strptime(hora, "%H:%M").time())
        data = tz.localize(data)
    inicio = data
    fim = inicio + timedelta(hours=1)

    event = {
        'summary': nome,
        'start': {'dateTime': inicio.isoformat(), 'timeZone': TIMEZONE},
        'end': {'dateTime': fim.isoformat(), 'timeZone': TIMEZONE},
        'reminders': {
            'useDefault': False,
            'overrides': [{'method': 'popup', 'minutes': 15}]
        },
    }
    service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

def gerar_estudos_semana():
    hoje = datetime.now(pytz.timezone(TIMEZONE)).date()
    dias = [hoje + timedelta(days=i) for i in range(7)]
    pos = 0
    for nome, qtd in estudos_semanais:
        for _ in range(qtd):
            agendar_evento(nome, "20:00", dias[pos])
            pos = (pos + 1) % len(dias)

def agendar_rotina_diaria():
    hoje = datetime.now(pytz.timezone(TIMEZONE)).date()
    for i in range(7):
        dia = hoje + timedelta(days=i)
        for a in atividades_diarias:
            agendar_evento(a["nome"], a["hora"], dia)

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

def send_agenda(do_dia):
    eventos = eventos_do_dia(do_dia)
    if not eventos:
        msg = "Nenhum compromisso agendado."
    else:
        msg = "\n".join([f"📌 {e['summary']} às {e['start']['dateTime'][11:16]}" for e in eventos])
    Bot(token=TELEGRAM_BOT_TOKEN).send_message(chat_id=TELEGRAM_USER_ID, text=f"🗓️ Agenda de {do_dia.strftime('%d/%m')}:\n{msg}")

def send_cursos():
    cursos = [
        "Curso de IA (Coursera): https://www.coursera.org/learn/machine-learning",
        "Curso de Investimentos (FGV): https://educacao-executiva.fgv.br/cursos/gratuitos/financas",
        "Curso de Administração (Sebrae): https://sebrae.com.br/cursosonline",
        "Curso de Violão (Udemy): https://www.udemy.com/course/violao-do-zero/",
        "Curso de Educação Financeira: https://edx.org/course/educacao-financeira"
    ]
    texto = "🎓 SUGESTÕES DE CURSOS GRATUITOS:\n\n" + "\n".join(f"- {c}" for c in cursos)
    Bot(token=TELEGRAM_BOT_TOKEN).send_message(chat_id=TELEGRAM_USER_ID, text=texto)

# =============== COMANDOS TELEGRAM ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fala, aqui é o Portella. Tô pronto pra organizar sua agenda.")

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Diga o nome do evento que você concluiu. Ex: /done Leitura")
        return
    nome = " ".join(context.args)
    concluidos.add(nome.lower())
    await update.message.reply_text(f"Beleza, marquei '{nome}' como concluído.")

async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hoje = datetime.now(pytz.timezone(TIMEZONE)).date()
    semana = [hoje - timedelta(days=i) for i in range(7)]
    eventos = []
    for dia in semana:
        for e in eventos_do_dia(dia):
            nome = e["summary"]
            status = "✅" if nome.lower() in concluidos else "❌"
            eventos.append(f"{status} {nome} - {dia.strftime('%a %d/%m')}")
    await update.message.reply_text("📋 Relatório semanal:\n" + "\n".join(eventos))

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    if "agenda" in texto:
        hoje = datetime.now(pytz.timezone(TIMEZONE)).date()
        send_agenda(hoje)
        await update.message.reply_text("Enviei sua agenda do dia.")
    elif "curso" in texto:
        send_cursos()
        await update.message.reply_text("Enviei sugestões de cursos.")
    else:
        await update.message.reply_text("Mensagem recebida. Em breve saberei responder melhor com IA!")

# =============== INICIALIZAÇÃO ==================

def agendar_tarefas():
    scheduler = BackgroundScheduler(timezone=TIMEZONE)
    scheduler.add_job(lambda: send_agenda(datetime.now(pytz.timezone(TIMEZONE)).date()), "cron", hour=7)
    scheduler.add_job(lambda: send_agenda(datetime.now(pytz.timezone(TIMEZONE)).date() + timedelta(days=1)), "cron", hour=23)
    scheduler.add_job(send_cursos, "cron", hour=22, day="*/2")
    scheduler.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agendar_rotina_diaria()
    gerar_estudos_semana()
    agendar_tarefas()

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("relatorio", relatorio))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.run_polling()
