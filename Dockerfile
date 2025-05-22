# Usa imagem leve com Python 3.11
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos para dentro do container
COPY . .

# Instala dependências
RUN pip install --upgrade pip && pip install -r requirements.txt

# Cria as pastas necessárias
RUN mkdir -p ./maps/encrypted/processed \
    ./maps/decrypted/processed \
    ./maps/outputs/json \
    ./maps/outputs/csv \
    ./customers

# Expõe a porta do Flask
EXPOSE 5001

# Comando para iniciar a aplicação com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "src.app:app"]