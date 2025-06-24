from datetime import datetime, timedelta
import pytz

def agendar_evento(service, nome, hora, data, timezone="America/Sao_Paulo"):
    hora_dt = datetime.strptime(hora, "%H:%M").time()
    inicio = datetime.combine(data, hora_dt)
    tz = pytz.timezone(timezone)
    inicio = tz.localize(inicio)
    fim = inicio + timedelta(hours=1)
    event = {
        'summary': nome,
        'start': {'dateTime': inicio.isoformat(), 'timeZone': timezone},
        'end': {'dateTime': fim.isoformat(), 'timeZone': timezone},
        'reminders': {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 15}]}
    }
    service.events().insert(calendarId='primary', body=event).execute()

def eventos_do_dia(service, data, timezone="America/Sao_Paulo"):
    tz = pytz.timezone(timezone)
    inicio = tz.localize(datetime.combine(data, datetime.min.time()))
    fim = inicio + timedelta(days=1)
    eventos = service.events().list(
        calendarId='primary',
        timeMin=inicio.isoformat(),
        timeMax=fim.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])
    return eventos

def gerar_estudos_semana(service, timezone):
    hoje = datetime.now(pytz.timezone(timezone)).date()
    estudos = [("Inteligência Artificial", 3), ("Investimentos", 2), ("Produção Musical", 1), ("Administração", 1)]
    dias = [hoje + timedelta(days=i) for i in range(7)]
    idx = 0
    for nome, qtd in estudos:
        for _ in range(qtd):
            agendar_evento(service, nome, "20:00", dias[idx], timezone)
            idx = (idx + 1) % len(dias)

def agendar_rotina_diaria(service, timezone):
    hoje = datetime.now(pytz.timezone(timezone)).date()
    rotina = [("Acordar", "07:00"), ("Leitura", "07:30"), ("Treino", "18:00")]
    for i in range(7):
        dia = hoje + timedelta(days=i)
        for nome, hora in rotina:
            agendar_evento(service, nome, hora, dia, timezone)
