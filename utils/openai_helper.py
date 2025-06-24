import re
from datetime import datetime, timedelta
import pytz

TIMEZONE = "America/Sao_Paulo"

def handle_natural_command(text):
    padrao = r"(?:agendar|marcar|remarcar|desmarcar)\s+(.*?)\s*(hoje|amanhã)?\s*(às\s*\d{1,2}(:\d{2})?)?"
    match = re.search(padrao, text.lower())
    if not match:
        return None

    acao = "agendar"
    if "remarcar" in text:
        acao = "remarcar"
    elif "desmarcar" in text:
        acao = "desmarcar"

    tarefa = match.group(1).strip()
    dia = match.group(2)
    hora = match.group(3)

    tz = pytz.timezone(TIMEZONE)
    data = datetime.now(tz)
    if dia == "amanhã":
        data += timedelta(days=1)

    hora_final = "09:00"  # padrão
    if hora:
        hora_final = re.sub(r"[^\d:]", "", hora.strip())

    return {
        "acao": acao,
        "tarefa": tarefa,
        "data": data.strftime("%Y-%m-%d"),
        "hora": hora_final
    }
