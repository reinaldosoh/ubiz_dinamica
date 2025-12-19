# Deploy no EasyPanel (VPS Hostinger)

## Passo 1: Acessar o EasyPanel

Acesse: `http://SEU_IP_VPS:3000`

## Passo 2: Criar Novo Projeto

1. Clique em **"Create Project"**
2. Nome: `ubiz-automation`
3. Clique em **"Create"**

## Passo 3: Adicionar Serviço (App)

1. Dentro do projeto, clique em **"+ Service"**
2. Selecione **"App"**
3. Configure:
   - **Name:** `automation-api`
   - **Source:** GitHub
   - **Repository:** `reinaldosoh/ubiz_dinamica`
   - **Branch:** `main`
   - **Build Path:** `automation` (pasta onde está o Dockerfile)

## Passo 4: Configurar Build

Na aba **Build**:
- **Dockerfile Path:** `Dockerfile`
- **Context:** `.` (ponto)

## Passo 5: Configurar Variáveis de Ambiente

Na aba **Environment**:
```
CHROME_BIN=/usr/bin/chromium
PORT=8000
```

## Passo 6: Configurar Domínio/Porta

Na aba **Domains**:
1. Clique em **"Add Domain"**
2. Opção 1: Use o domínio automático do EasyPanel
3. Opção 2: Configure seu próprio domínio (ex: `automation.seudominio.com`)

**Port:** `8000`

## Passo 7: Configurar Recursos

Na aba **Resources** (opcional, mas recomendado):
- **Memory Limit:** `2048` MB (2GB por container)
- **CPU Limit:** `2` cores

Com 32GB RAM, você pode rodar vários containers se precisar.

## Passo 8: Deploy

1. Clique em **"Deploy"**
2. Aguarde o build (pode levar 2-5 minutos)
3. Verifique os logs para erros

## Passo 9: Testar

Acesse: `https://SEU_DOMINIO/health`

Deve retornar:
```json
{
  "status": "healthy",
  "service": "automation-api",
  "memory_mb": 150.5,
  "active_executions": 0,
  "mode": "parallel"
}
```

## Passo 10: Atualizar URL no Sistema

Após o deploy, atualize a URL da automação no banco de dados:

```sql
UPDATE cidades 
SET automation_url = 'https://SEU_DOMINIO_EASYPANEL'
WHERE automation_ativo = true;
```

---

## Comandos Úteis no EasyPanel

### Ver Logs
- Clique no serviço → Aba **"Logs"**

### Reiniciar Serviço
- Clique no serviço → Botão **"Restart"**

### Atualizar (Redeploy)
- Clique no serviço → Botão **"Deploy"** (puxa última versão do GitHub)

---

## Alternativa: Deploy via Docker Compose

Se preferir usar Docker Compose no EasyPanel:

1. Crie um serviço do tipo **"Docker Compose"**
2. Cole o conteúdo do `docker-compose.yml`:

```yaml
version: '3.8'
services:
  automation:
    build:
      context: ./automation
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - CHROME_BIN=/usr/bin/chromium
      - PORT=8000
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2'
```

---

## Troubleshooting

### Erro: Chrome não inicia
- Verifique se `CHROME_BIN=/usr/bin/chromium` está configurado
- Verifique logs para erros de permissão

### Erro: Out of Memory
- Aumente o limite de memória do container
- Com 32GB RAM, você pode dar 4GB+ por container

### Erro: Timeout na automação
- Aumente o timeout do proxy reverso no EasyPanel
- Vá em Settings → Proxy Timeout → 300s
