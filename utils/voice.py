import os
import tempfile
import requests
import speech_recognition as sr
from pydub import AudioSegment

def transcribe_voice(file_url):
    response = requests.get(file_url)
    if response.status_code != 200:
        return "Não consegui baixar o áudio."

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_audio:
        temp_audio.write(response.content)
        temp_audio_path = temp_audio.name

    wav_path = temp_audio_path.replace(".ogg", ".wav")
    try:
        audio = AudioSegment.from_file(temp_audio_path)
        audio.export(wav_path, format="wav")
    except Exception as e:
        return f"Erro ao converter o áudio: {str(e)}"

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data, language="pt-BR")
        except sr.UnknownValueError:
            return "Não entendi o que você disse."
        except sr.RequestError:
            return "Erro ao acessar o serviço de reconhecimento de voz."
