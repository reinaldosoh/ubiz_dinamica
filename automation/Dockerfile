# Dockerfile para automação com Selenium + Chromium
FROM python:3.11-slim-bookworm

# Instalar Chromium (mais leve que Chrome) e dependências
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p screenshots

# Configurar para usar Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

EXPOSE 8000

CMD ["python", "main.py"]
