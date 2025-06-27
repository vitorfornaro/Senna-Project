# Usa imagem leve com Python 3.11
FROM python:3.11-slim

# Corrige acesso aos repositórios Debian via HTTPS e instala dependências do sistema
RUN apt-get update || true && \
    apt-get install -y \
        tesseract-ocr \
        tesseract-ocr-por \
        libgl1 \
        poppler-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho dentro do container
WORKDIR /app

# Copia todos os arquivos do projeto local para dentro do container
COPY . .

# Define variável de ambiente para incluir o diretório src no caminho do Python
ENV PYTHONPATH=/app/src

# Atualiza pip e instala dependências Python listadas no requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Cria todas as pastas necessárias no container
RUN mkdir -p ./maps/encrypted/processed \
    ./maps/decrypted/processed \
    ./maps/outputs/json \
    ./maps/outputs/csv \
    ./maps/no_perfila \
    ./customers \
    ./logs

# Expõe a porta usada pela aplicação Flask
EXPOSE 5001

# Inicia a aplicação com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]