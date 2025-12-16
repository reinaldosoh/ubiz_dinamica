# TaxiMachine Automation API

API Python com FastAPI + Selenium para automação de login no TaxiMachine Cloud.

## Instalação

```bash
cd automation
pip install -r requirements.txt
```

## Executar

```bash
python main.py
```

O servidor iniciará em `http://localhost:8000`

## Endpoints

- `GET /` - Status da API
- `GET /health` - Health check
- `POST /login` - Login com credenciais customizadas
- `POST /login/test` - Login com credenciais padrão

## Exemplo de uso

```bash
# Testar login com credenciais padrão
curl -X POST http://localhost:8000/login/test

# Login com credenciais customizadas
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "seu@email.com", "password": "suasenha"}'
```
