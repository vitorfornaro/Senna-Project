# Usa imagem base leve com Python 3.11
FROM python:3.11-slim

# Define variável de ambiente para não gerar arquivos `.pyc`
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-por \
        libgl1 \
        poppler-utils \
        && apt-get clean && \
        rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto para o container
COPY . .

# Define o caminho do código-fonte como variável de ambiente
ENV PYTHONPATH=/app/src

# Instala as dependências do projeto
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Garante que os diretórios necessários existem
RUN mkdir -p \
    ./maps/encrypted/processed \
    ./maps/decrypted/processed \
    ./maps/outputs/json \
    ./maps/outputs/csv \
    ./maps/no_perfila \
    ./customers \
    ./logs

# Expõe a porta usada pela aplicação Flask
EXPOSE 5001

# Define o comando padrão de inicialização com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]