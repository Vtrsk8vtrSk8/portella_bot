# utils/openai_helper.py

def handle_natural_command(message: str):
    """
    Interpreta comandos de texto em linguagem natural e retorna ação e dados.
    Exemplo:
        Entrada: "remarcar leitura para amanhã às 10h"
        Saída: ("remarcar", {"evento": "leitura", "data": "amanhã", "hora": "10:00"})
    """
    message = message.lower()
    if "remarcar" in message:
        return "remarcar", message
    elif "desmarcar" in message:
        return "desmarcar", message
    elif "agendar" in message:
        return "agendar", message
    elif "agenda" in message:
        return "ver_agenda", message
    else:
        return "comando_desconhecido", message
