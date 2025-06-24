import speech_recognition as sr
from pydub import AudioSegment

def transcribe_voice(file_path):
    try:
        ogg = AudioSegment.from_file(file_path)
        wav_path = file_path.replace(".oga", ".wav")
        ogg.export(wav_path, format="wav")
        r = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = r.record(source)
            return r.recognize_google(audio, language="pt-BR")
    except Exception:
        return None
