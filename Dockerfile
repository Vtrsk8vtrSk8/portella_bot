# Usa imagem oficial do Python
FROM python:3.11-slim

# Cria diretório no container
WORKDIR /app

# Copia os arquivos do repositório para o container
COPY . .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Comando para iniciar o bot
CMD ["python", "main.py"]
