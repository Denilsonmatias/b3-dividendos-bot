# Usar imagem base com Python
FROM python:3.10-slim

# Criar diretório de trabalho
WORKDIR /app

# Copiar arquivos
COPY . .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Rodar o bot
CMD ["python", "main.py"]
