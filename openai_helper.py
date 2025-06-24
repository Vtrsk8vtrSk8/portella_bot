def handle_natural_command(texto, service):
    texto = texto.lower()
    if "remarcar" in texto or "mudar" in texto:
        return "🛠️ Em breve vou conseguir remarcar eventos com IA."
    elif "agenda" in texto:
        return "📅 Quer ver a agenda de hoje ou da semana?"
    elif "curso" in texto:
        return "🎓 Em breve vou sugerir cursos baseados nos seus objetivos."
    return "Desculpa, ainda estou aprendendo a lidar com esse tipo de comando."
