# Usa imagem leve com Python 3.11
FROM python:3.11-slim

# Define diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do seu projeto para o container
COPY . .

# Atualiza pip e instala as dependências
RUN pip install --upgrade pip && pip install -r requirements.txt

# Garante que as pastas necessárias existam
RUN mkdir -p ./maps/encrypted/processed \
    ./maps/decrypted/processed \
    ./maps/outputs/json \
    ./maps/outputs/csv \
    ./customers

# Comando padrão que será executado quando o container iniciar
CMD ["python", "src/main.py"]