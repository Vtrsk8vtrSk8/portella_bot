FROM python:3.10-slim

WORKDIR /app

# Instala ffmpeg e dependências
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

COPY . .

# Instala dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
