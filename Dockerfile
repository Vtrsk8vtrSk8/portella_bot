# Usar imagem Python oficial
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copiar os arquivos do projeto
COPY . /app

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Rodar o bot
CMD ["python", "main.py"]
