# Dockerfile para automação com Selenium + Chrome
# Usando imagem oficial do Selenium que já tem Chrome instalado
FROM selenium/standalone-chrome:latest

USER root

# Instalar Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Criar diretório de screenshots
RUN mkdir -p screenshots && chmod 777 screenshots

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["python3", "main.py"]
