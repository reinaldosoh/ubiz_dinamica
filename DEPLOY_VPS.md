# Deploy na VPS Hostinger

## 1. Acessar a VPS via SSH

```bash
ssh root@SEU_IP_DA_VPS
```

## 2. Atualizar Sistema e Instalar Dependências

```bash
# Atualizar pacotes
apt update && apt upgrade -y

# Instalar Python 3.11+ e pip
apt install -y python3 python3-pip python3-venv

# Instalar dependências do Chrome/Chromium
apt install -y wget curl unzip gnupg2

# Instalar Chromium (mais leve que Chrome)
apt install -y chromium-browser chromium-chromedriver

# Instalar Git
apt install -y git

# Instalar supervisor (para manter o serviço rodando)
apt install -y supervisor

# Instalar nginx (proxy reverso - opcional mas recomendado)
apt install -y nginx
```

## 3. Clonar o Repositório

```bash
cd /opt
git clone https://github.com/reinaldosoh/ubiz_dinamica.git
cd ubiz_dinamica/automation
```

## 4. Criar Ambiente Virtual e Instalar Dependências

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install psutil  # Para monitoramento de memória
```

## 5. Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
cat > /opt/ubiz_dinamica/automation/.env << 'EOF'
CHROME_BIN=/usr/bin/chromium-browser
PORT=8000
EOF
```

## 6. Testar Manualmente

```bash
cd /opt/ubiz_dinamica/automation
source venv/bin/activate
python3 main.py
```

Acesse: `http://SEU_IP:8000/health`

## 7. Configurar Supervisor (Manter Rodando 24/7)

```bash
cat > /etc/supervisor/conf.d/ubiz_automation.conf << 'EOF'
[program:ubiz_automation]
command=/opt/ubiz_dinamica/automation/venv/bin/python3 /opt/ubiz_dinamica/automation/main.py
directory=/opt/ubiz_dinamica/automation
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/ubiz_automation.err.log
stdout_logfile=/var/log/ubiz_automation.out.log
environment=CHROME_BIN="/usr/bin/chromium-browser",PORT="8000"
EOF

# Recarregar supervisor
supervisorctl reread
supervisorctl update
supervisorctl start ubiz_automation
```

## 8. Configurar Nginx (Proxy Reverso com HTTPS)

```bash
cat > /etc/nginx/sites-available/ubiz_automation << 'EOF'
server {
    listen 80;
    server_name SEU_DOMINIO_OU_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
EOF

ln -s /etc/nginx/sites-available/ubiz_automation /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

## 9. (Opcional) Configurar HTTPS com Let's Encrypt

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d SEU_DOMINIO
```

## 10. Comandos Úteis

```bash
# Ver status do serviço
supervisorctl status ubiz_automation

# Reiniciar serviço
supervisorctl restart ubiz_automation

# Ver logs em tempo real
tail -f /var/log/ubiz_automation.out.log

# Ver erros
tail -f /var/log/ubiz_automation.err.log

# Atualizar código do GitHub
cd /opt/ubiz_dinamica
git pull
supervisorctl restart ubiz_automation
```

## 11. Firewall (UFW)

```bash
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

## 12. Monitoramento de Recursos

```bash
# Instalar htop para monitorar CPU/RAM
apt install -y htop

# Ver uso de memória
htop
```

---

## Endpoints Disponíveis

- `GET /health` - Status do serviço e uso de memória
- `POST /dinamica/atualizar` - Atualizar dinâmica
- `POST /login` - Testar login

## Exemplo de Chamada

```bash
curl -X POST http://SEU_IP:8000/dinamica/atualizar \
  -H "Content-Type: application/json" \
  -d '{
    "multiplicador": 1.2,
    "headless": true,
    "email": "seu@email.com",
    "password": "suasenha",
    "cidade": "Ourinhos",
    "estado": "SP"
  }'
```
