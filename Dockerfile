# Usa imagem leve com Python 3.11
FROM python:3.11-slim

# Instala dependências do sistema necessárias para OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    libgl1 \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Atualiza pip e instala dependências Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Cria as pastas necessárias no container
RUN mkdir -p ./maps/encrypted/processed \
    ./maps/decrypted/processed \
    ./maps/outputs/json \
    ./maps/outputs/csv \
    ./maps/no_perfila \
    ./customers \
    ./logs

# Expõe a porta usada pela aplicação Flask
EXPOSE 5001

# Comando de entrada: inicia API com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "src.app:app"]