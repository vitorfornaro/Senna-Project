# Usa imagem base leve com Python 3.11
FROM python:3.11-slim

# Evita .pyc e garante logs sem buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependências do sistema (OCR + PDF)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-por \
        libgl1 \
        poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho base
WORKDIR /app

# Copia só requirements primeiro (cache melhor)
COPY requirements.txt ./requirements.txt

# Instala dependências Python (inclua gunicorn no requirements.txt)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Agora copia o resto do projeto
COPY . .

# ⚠️ IMPORTANTE: habilita imports de 'src' e de 'services' usados como caminho raiz
# - /app/senna-project     -> permite "from src...."
# - /app/senna-project/src -> permite "from services...."
ENV PYTHONPATH=/app/senna-project:/app/senna-project/src

# Roda a partir do diretório do projeto
WORKDIR /app/senna-project

# Porta da API Flask
EXPOSE 5001

# Sobe com gunicorn apontando para o módulo "src.api.app:app"
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "src.api.app:app"]