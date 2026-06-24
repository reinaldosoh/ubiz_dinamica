from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import threading
import gc

load_dotenv()

# Configuração Supabase via REST API (fallback se corridas_stats não for passado)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def js_preencher_nome_area(driver, area_busca: str) -> str:
    """Preenche o campo obrigatório 'Nome da área' no formulário de edição TM."""
    return driver.execute_script("""
        var areaNome = arguments[0];

        function setNativeValue(element, value) {
            var prototype = Object.getPrototypeOf(element);
            var valueSetter = Object.getOwnPropertyDescriptor(prototype, 'value').set;
            valueSetter.call(element, value);
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
        }

        function labelText(inp) {
            if (inp.id) {
                var lbl = document.querySelector('label[for="' + inp.id + '"]');
                if (lbl) return (lbl.innerText || lbl.textContent || '').toLowerCase();
            }
            var parent = inp.closest('div, label, fieldset');
            if (parent) {
                var lbl2 = parent.querySelector('label');
                if (lbl2) return (lbl2.innerText || lbl2.textContent || '').toLowerCase();
            }
            return '';
        }

        var roots = document.querySelectorAll('[role="dialog"], [class*="modal" i], [class*="Modal"], form');
        var searchRoots = roots.length ? Array.from(roots) : [document];

        for (var r = 0; r < searchRoots.length; r++) {
            var root = searchRoots[r];
            var inputs = root.querySelectorAll('input, textarea');

            for (var i = 0; i < inputs.length; i++) {
                var inp = inputs[i];
                var rect = inp.getBoundingClientRect();
                var type = (inp.type || 'text').toLowerCase();
                if (rect.width <= 0 || rect.height <= 0) continue;
                if (type === 'hidden' || type === 'checkbox' || type === 'radio' || type === 'number') continue;

                var label = labelText(inp);
                var placeholder = (inp.placeholder || '').toLowerCase();
                var name = (inp.name || '').toLowerCase();
                var pareceNomeArea =
                    label.includes('nome da área') || label.includes('nome da area') ||
                    (label.includes('nome') && (label.includes('área') || label.includes('area'))) ||
                    placeholder.includes('nome da área') || placeholder.includes('nome da area') ||
                    (placeholder.includes('nome') && (placeholder.includes('área') || placeholder.includes('area'))) ||
                    (name.includes('nome') && (name.includes('area') || name.includes('área')));

                if (pareceNomeArea) {
                    setNativeValue(inp, areaNome);
                    return 'nome_area_label:' + areaNome + ':val=' + inp.value;
                }
            }

            var visibleText = [];
            for (var j = 0; j < inputs.length; j++) {
                var inp2 = inputs[j];
                var rect2 = inp2.getBoundingClientRect();
                var type2 = (inp2.type || 'text').toLowerCase();
                if (rect2.width <= 0 || rect2.height <= 0) continue;
                if (type2 === 'hidden' || type2 === 'checkbox' || type2 === 'radio' || type2 === 'number') continue;
                visibleText.push(inp2);
            }
            if (visibleText.length >= 1) {
                setNativeValue(visibleText[0], areaNome);
                return 'nome_area_primeiro_text:' + areaNome + ':val=' + visibleText[0].value;
            }
        }
        return 'nome_area_nao_encontrado';
    """, area_busca)


def dump_form_estrutura(driver) -> str:
    """Retorna JSON compacto dos campos visíveis do formulário de edição (diagnóstico)."""
    try:
        return driver.execute_script("""
            function labelText(inp) {
                if (inp.id) {
                    var lbl = document.querySelector('label[for="' + inp.id + '"]');
                    if (lbl) return (lbl.innerText || lbl.textContent || '').trim();
                }
                var parent = inp.closest('div, label, fieldset');
                if (parent) {
                    var lbl2 = parent.querySelector('label');
                    if (lbl2) return (lbl2.innerText || lbl2.textContent || '').trim();
                }
                return '';
            }
            var out = [];
            var els = document.querySelectorAll('input, textarea, select');
            for (var i = 0; i < els.length; i++) {
                var e = els[i];
                var r = e.getBoundingClientRect();
                if (r.width <= 0 || r.height <= 0) continue;
                out.push({
                    tag: e.tagName,
                    type: (e.type || '').toLowerCase(),
                    name: e.name || '',
                    id: e.id || '',
                    placeholder: e.placeholder || '',
                    aria: e.getAttribute('aria-label') || '',
                    label: labelText(e),
                    value: (e.value || '').slice(0, 40)
                });
            }
            return JSON.stringify(out);
        """)
    except Exception as e:
        return f"dump_falhou:{e}"


def preencher_nome_area(driver, wait, area_busca: str) -> str:
    """Garante que o campo Nome da área (#nome_tarifa) do form de edição esteja preenchido."""
    try:
        return driver.execute_script("""
            var valor = arguments[0];
            var inp = document.querySelector('#nome_tarifa');
            if (!inp) return 'nome_tarifa_ausente';
            if (inp.value && inp.value.trim()) return 'nome_tarifa_ja_preenchido:' + inp.value;
            var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            setter.call(inp, valor);
            inp.dispatchEvent(new Event('input', { bubbles: true }));
            inp.dispatchEvent(new Event('change', { bubbles: true }));
            return 'nome_tarifa_preenchido:' + inp.value;
        """, area_busca)
    except Exception as e:
        return f"nome_area_erro:{e}"


def dismiss_onboarding(driver) -> str:
    """Fecha modais de introdução e tooltips de onboarding do TM Cloud."""
    try:
        return driver.execute_script("""
            var acoes = [];
            // 1. Fechar botões de close (X) de modais/explanations
            document.querySelectorAll('.mapa__explanation__close, .close, button[aria-label="Close"]').forEach(function(b){
                var r = b.getBoundingClientRect();
                if (r.width > 0 && r.height > 0) { try { b.click(); acoes.push('close'); } catch(e){} }
            });
            // 2. Clicar em botões "Entendi"/"Concluir"/"Explorar" de tooltips
            document.querySelectorAll('button, a').forEach(function(b){
                var t = (b.innerText || '').trim();
                if (t === 'Entendi' || t === 'Concluir' || t === 'Finalizar') {
                    var r = b.getBoundingClientRect();
                    if (r.width > 0 && r.height > 0) { try { b.click(); acoes.push(t); } catch(e){} }
                }
            });
            // 3. Remover ícones "close" (material) de modais visíveis no topo
            document.querySelectorAll('i, span').forEach(function(el){
                if ((el.innerText || '').trim() === 'close') {
                    var r = el.getBoundingClientRect();
                    if (r.width > 0 && r.height > 0 && r.top < 300) { try { el.click(); acoes.push('icon_close'); } catch(e){} }
                }
            });
            return acoes.join(',') || 'nenhum';
        """)
    except Exception as e:
        return f"dismiss_erro:{e}"


def buscar_corridas_stats_fallback(cidade_nome: str) -> dict:
    """Busca estatísticas de corridas via REST API (fallback)"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Supabase não configurado")
        return None
    
    try:
        quinze_min_atras = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
        
        url = f"{SUPABASE_URL}/rest/v1/taximachine_webhooks"
        params = f"select=request_id,status_code&event_datetime=gte.{quinze_min_atras}&cidade_nome=eq.{cidade_nome}&order=event_datetime.desc"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        
        response = requests.get(f"{url}?{params}", headers=headers, timeout=5)
        
        if response.status_code != 200:
            print(f"Erro Supabase: {response.status_code}")
            return None
        
        data = response.json()
        if not data:
            return {'total': 0, 'pendentes': 0, 'finalizadas': 0, 'canceladas': 0, 'nao_atendidas': 0, 'aceitas': 0, 'em_espera': 0}
        
        # Agrupar por request_id
        corridas_unicas = {}
        for corrida in data:
            rid = corrida.get('request_id')
            if rid and rid not in corridas_unicas:
                corridas_unicas[rid] = corrida.get('status_code', '')
        
        # Contar por status
        stats = {'total': 0, 'pendentes': 0, 'finalizadas': 0, 'canceladas': 0, 'nao_atendidas': 0, 'aceitas': 0, 'em_espera': 0}
        for status in corridas_unicas.values():
            stats['total'] += 1
            if status == 'P': stats['pendentes'] += 1
            elif status == 'F': stats['finalizadas'] += 1
            elif status == 'C': stats['canceladas'] += 1
            elif status == 'N': stats['nao_atendidas'] += 1
            elif status == 'A': stats['aceitas'] += 1
            elif status == 'S': stats['em_espera'] += 1
        
        print(f"Stats corridas {cidade_nome}: {stats}")
        return stats
    except Exception as e:
        print(f"Erro ao buscar corridas: {e}")
        return None

app = FastAPI(title="TaxiMachine Automation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MODO POOL: Reutiliza drivers por cidade com timeout de 5 minutos
# Reduz consumo de recursos e tempo de execução (não precisa logar toda vez)

# Pool de drivers por email (cada cidade tem seu próprio driver)
driver_pool = {}  # {email: {"driver": driver, "last_used": timestamp}}
pool_lock = threading.Lock()
DRIVER_TIMEOUT_SECONDS = 300  # 5 minutos de inatividade

# Contador de execuções ativas (apenas para monitoramento)
active_executions = 0
executions_lock = threading.Lock()

def cleanup_idle_drivers():
    """Remove drivers que estão inativos há mais de 5 minutos"""
    import time
    with pool_lock:
        now = time.time()
        emails_to_remove = []
        for email, data in driver_pool.items():
            if now - data["last_used"] > DRIVER_TIMEOUT_SECONDS:
                try:
                    data["driver"].quit()
                    print(f"Driver fechado por inatividade: {email}")
                except:
                    pass
                emails_to_remove.append(email)
        for email in emails_to_remove:
            del driver_pool[email]

def get_or_create_driver(email: str, headless: bool = True):
    """Obtém driver existente do pool ou cria um novo"""
    import time
    cleanup_idle_drivers()  # Limpar drivers inativos
    
    with pool_lock:
        if email in driver_pool:
            driver_data = driver_pool[email]
            driver = driver_data["driver"]
            # Verificar se o driver ainda está funcionando
            try:
                driver.current_url  # Teste simples
                driver_data["last_used"] = time.time()
                print(f"Reutilizando driver existente para: {email}")
                return driver, False  # False = não é novo
            except:
                # Driver morreu, remover do pool
                try:
                    driver.quit()
                except:
                    pass
                del driver_pool[email]
        
        # Criar novo driver
        driver = create_driver(headless=headless)
        driver_pool[email] = {"driver": driver, "last_used": time.time()}
        print(f"Novo driver criado para: {email}")
        return driver, True  # True = é novo, precisa logar

def release_driver(email: str):
    """Atualiza timestamp do driver (mantém no pool)"""
    import time
    with pool_lock:
        if email in driver_pool:
            driver_pool[email]["last_used"] = time.time()

def force_close_driver(email: str):
    """Força fechamento do driver (em caso de erro grave)"""
    with pool_lock:
        if email in driver_pool:
            try:
                driver_pool[email]["driver"].quit()
            except:
                pass
            del driver_pool[email]
            print(f"Driver forçadamente fechado: {email}")

class LoginCredentials(BaseModel):
    email: str = "reinaldo@painel.com.br"
    password: str = "Reinaldo@ubizcar10"
    headless: bool = True

class LoginResponse(BaseModel):
    success: bool
    message: str
    screenshot_path: Optional[str] = None

class CorridasStats(BaseModel):
    total: int = 0
    pendentes: int = 0
    finalizadas: int = 0
    canceladas: int = 0
    nao_atendidas: int = 0
    aceitas: int = 0
    em_espera: int = 0

class DinamicaRequest(BaseModel):
    multiplicador: float
    headless: bool = False
    email: str
    password: str
    cidade: str = "Não informada"
    estado: str = "Não informado"
    is_test: bool = False  # Se True, adiciona "OBS: ENVIADO COMO TESTE" no webhook
    teste: bool = False  # alias usado pelo Radar
    corridas_stats: Optional[CorridasStats] = None  # Estatísticas passadas por quem chama a API
    area_busca: str = "***Geral"  # termo de busca do card manual no TaxiMachine Cloud (por cidade/projeto)

class DinamicaResponse(BaseModel):
    success: bool
    message: str
    multiplicador_aplicado: Optional[float] = None
    screenshot_path: Optional[str] = None

def create_driver(headless: bool = True):
    """Cria e configura o driver do Chrome/Chromium"""
    import os
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Usar Chromium se disponível (para Docker)
    chrome_bin = os.environ.get('CHROME_BIN')
    if chrome_bin:
        chrome_options.binary_location = chrome_bin
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

@app.get("/")
async def root():
    return {"message": "TaxiMachine Automation API", "version": "1.0.0"}

@app.get("/health")
async def health():
    import psutil
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    return {
        "status": "healthy", 
        "service": "automation-api",
        "memory_mb": round(memory_mb, 2),
        "active_executions": active_executions,
        "mode": "parallel",
        "version": "3.1.1-menu-dump"
    }

@app.post("/driver/close")
async def close_driver():
    """Endpoint mantido para compatibilidade - no modo paralelo cada driver é fechado após uso"""
    gc.collect()
    return {"success": True, "message": "Modo paralelo: drivers são fechados automaticamente após cada execução"}

@app.post("/login", response_model=LoginResponse)
async def login_taximachine(credentials: LoginCredentials):
    """
    Realiza login no TaxiMachine Cloud
    """
    driver = None
    try:
        driver = create_driver(headless=credentials.headless)
        
        driver.get("https://cloud.taximachine.com.br/site/login")
        
        wait = WebDriverWait(driver, 15)
        
        email_field = wait.until(
            EC.presence_of_element_located((By.NAME, "LoginForm[username]"))
        )
        email_field.clear()
        email_field.send_keys(credentials.email)
        
        password_field = driver.find_element(By.NAME, "LoginForm[password]")
        password_field.clear()
        password_field.send_keys(credentials.password)
        
        login_button = None
        selectors = [
            "button[type='submit']",
            "input[type='submit']",
            ".btn-primary",
            ".btn-login",
            "button.btn",
            "#login-btn",
            "form button",
            "form input[type='submit']"
        ]
        
        for selector in selectors:
            try:
                login_button = driver.find_element(By.CSS_SELECTOR, selector)
                if login_button:
                    break
            except:
                continue
        
        if not login_button:
            try:
                login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Entrar') or contains(text(), 'Login') or contains(text(), 'Acessar')]")
            except:
                pass
        
        if not login_button:
            try:
                login_button = driver.find_element(By.XPATH, "//input[@type='submit']")
            except:
                pass
        
        if login_button:
            login_button.click()
        else:
            password_field.submit()
        
        time.sleep(3)
        
        screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshots_dir, f"login_{int(time.time())}.png")
        driver.save_screenshot(screenshot_path)
        
        current_url = driver.current_url
        page_source = driver.page_source.lower()
        
        if "login" not in current_url.lower() or "verificação" in page_source or "2fa" in page_source or "duas etapas" in page_source:
            return LoginResponse(
                success=True,
                message="Login realizado com sucesso! (Página atual pode requerer 2FA)",
                screenshot_path=screenshot_path
            )
        else:
            return LoginResponse(
                success=False,
                message="Login falhou - ainda na página de login",
                screenshot_path=screenshot_path
            )
            
    except Exception as e:
        return LoginResponse(
            success=False,
            message=f"Erro durante o login: {str(e)}",
            screenshot_path=None
        )
    finally:
        if driver:
            driver.quit()

@app.post("/login/test")
async def test_login():
    """
    Testa o login com credenciais padrão (headless)
    """
    return await login_taximachine(LoginCredentials())

@app.post("/login/visual")
async def visual_login():
    """
    Testa o login com navegador visível (abre o Chrome)
    """
    return await login_taximachine(LoginCredentials(headless=False))

@app.post("/dinamica/atualizar", response_model=DinamicaResponse)
async def atualizar_dinamica(request: DinamicaRequest):
    """
    MODO POOL: Reutiliza driver existente ou cria novo
    Driver fica aberto por 5 minutos de inatividade
    """
    global active_executions
    
    # Incrementar contador de execuções ativas
    with executions_lock:
        active_executions += 1
    
    print(f"=== INICIANDO AUTOMAÇÃO (Execuções ativas: {active_executions}, Pool: {len(driver_pool)}) ===")
    print(f"Email recebido: {request.email}")
    print(f"Multiplicador: {request.multiplicador}")
    print(f"Headless: {request.headless}")
    print(f"Area busca: {request.area_busca}")
    
    if not request.email or not request.password:
        with executions_lock:
            active_executions -= 1
        raise HTTPException(status_code=400, detail="email e password são obrigatórios")
    
    area_busca = (request.area_busca or "***Geral").strip() or "***Geral"
    driver = None
    is_new_driver = True
    form_debug = ""
    try:
        # Obter driver do pool ou criar novo
        driver, is_new_driver = get_or_create_driver(request.email, headless=request.headless)
        wait = WebDriverWait(driver, 20)
        screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # 1. LOGIN - Só faz login se for driver novo ou se não estiver logado
        if is_new_driver:
            driver.get("https://cloud.taximachine.com.br/site/login")
            time.sleep(1)  # OTIMIZADO: 2s -> 1s
        else:
            # Driver existente - verificar se ainda está logado
            driver.get("https://cloud.taximachine.com.br/tarifaCategoria/dinamica")
            time.sleep(1)  # OTIMIZADO: 2s -> 1s
        
        # Verificar se precisa logar
        current_url = driver.current_url.lower()
        if "login" in current_url:
            # Tentar diferentes seletores para o campo de email
            email_field = None
            email_selectors = [
                (By.NAME, "LoginForm[username]"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, "input[name='email']"),
                (By.XPATH, "//input[@placeholder='Email' or contains(@placeholder, 'email')]"),
                (By.CSS_SELECTOR, "input.form-control[type='text']"),
            ]
            
            for by, selector in email_selectors:
                try:
                    email_field = wait.until(EC.presence_of_element_located((by, selector)))
                    if email_field:
                        break
                except:
                    continue
            
            if email_field:
                email_field.clear()
                email_field.send_keys(request.email)
                
                # Campo de senha
                password_field = None
                password_selectors = [
                    (By.NAME, "LoginForm[password]"),
                    (By.CSS_SELECTOR, "input[type='password']"),
                ]
                
                for by, selector in password_selectors:
                    try:
                        password_field = driver.find_element(by, selector)
                        if password_field:
                            break
                    except:
                        continue
                
                if password_field:
                    password_field.clear()
                    password_field.send_keys(request.password)
                    time.sleep(0.5)
                    
                    # Clicar no botão de login
                    login_button = None
                    for by, selector in [(By.XPATH, "//button[contains(text(), 'Entrar')]"), 
                                        (By.CSS_SELECTOR, "button[type='submit']")]:
                        try:
                            login_button = driver.find_element(by, selector)
                            if login_button and login_button.is_displayed():
                                break
                        except:
                            continue
                    
                    if login_button:
                        driver.execute_script("arguments[0].click();", login_button)
                    else:
                        # Fallback: clicar via JavaScript
                        driver.execute_script("""
                            var btn = document.querySelector('button[type="submit"]') || 
                                      document.querySelector('button');
                            if (btn) btn.click();
                        """)
                    
                    time.sleep(1)  # OTIMIZADO: 2s -> 1s
                    
                    # Verificar se logou
                    current_url = driver.current_url.lower()
                    if "login" in current_url:
                        # Fechar driver antes de retornar erro
                        if driver:
                            try:
                                driver.quit()
                            except:
                                pass
                        with executions_lock:
                            active_executions -= 1
                        return DinamicaResponse(
                            success=False,
                            message="Falha no login",
                            screenshot_path=None
                        )
                    
                    print(f"Login realizado com sucesso como {request.email}!")
        
        # 2. NAVEGAR DIRETAMENTE PARA A URL DE TARIFAS DINÂMICAS
        driver.get("https://cloud.taximachine.com.br/tarifaCategoria/dinamica")
        time.sleep(1)  # OTIMIZADO: 2s -> 1s
        
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        
        # Fechar modais de introdução e tooltips de onboarding (Entendi/Explorar/X)
        for _ in range(5):
            acoes = dismiss_onboarding(driver)
            print(f"Onboarding dismiss: {acoes}")
            if acoes in ("nenhum", "") or str(acoes).startswith("dismiss_erro"):
                break
            time.sleep(0.4)

        # 3. CLICAR NA ABA "MANUAIS"
        driver.execute_script("""
            var alvo = null;
            document.querySelectorAll('button, a, span, div').forEach(function(el) {
                if (!alvo && (el.innerText || '').trim() === 'Manuais') alvo = el;
            });
            if (alvo) alvo.click();
        """)
        time.sleep(0.8)
        dismiss_onboarding(driver)

        # 3.5. BUSCAR a área pelo campo real (placeholder "Buscar por nome da área")
        search_result = driver.execute_script("""
            var areaBusca = arguments[0];
            var inp = document.querySelector('input[placeholder*="Buscar"]');
            if (!inp) {
                var ins = document.querySelectorAll('input[type="text"], input:not([type])');
                for (var i = 0; i < ins.length; i++) {
                    var r = ins[i].getBoundingClientRect();
                    if (r.width > 0 && r.height > 0) { inp = ins[i]; break; }
                }
            }
            if (!inp) return 'campo_busca_nao_encontrado';
            var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            inp.focus();
            setter.call(inp, areaBusca);
            inp.dispatchEvent(new Event('input', { bubbles: true }));
            inp.dispatchEvent(new Event('change', { bubbles: true }));
            return 'busca_preenchida';
        """, area_busca)
        print(f"Campo de busca: {search_result}")
        time.sleep(1)

        # 4. ABRIR MENU (3 pontos = more_vert) DO CARD CORRETO
        menu_result = driver.execute_script("""
            var area = (arguments[0] || '').toLowerCase();
            var cards = document.querySelectorAll('.box-fator');
            var alvo = null;
            for (var i = 0; i < cards.length; i++) {
                if ((cards[i].innerText || '').toLowerCase().indexOf(area) !== -1) { alvo = cards[i]; break; }
            }
            if (!alvo && cards.length === 1) alvo = cards[0];
            if (!alvo) return 'card_nao_encontrado';
            var nodes = alvo.querySelectorAll('*');
            for (var j = 0; j < nodes.length; j++) {
                if ((nodes[j].innerText || '').trim() === 'more_vert') {
                    var r = nodes[j].getBoundingClientRect();
                    var top = document.elementFromPoint(r.x + r.width/2, r.y + r.height/2);
                    (top || nodes[j]).click();
                    return 'menu_aberto';
                }
            }
            return 'menu_nao_encontrado';
        """, area_busca)
        print(f"Menu card: {menu_result}")
        time.sleep(0.5)

        # 4.5. CLICAR EM "Editar" no dropdown (classe real: dropdown__editar)
        editar_result = "editar_nao_encontrado"
        for _ in range(8):
            editar_result = driver.execute_script("""
                function clicar(el){
                    var r = el.getBoundingClientRect();
                    if (r.width <= 0 || r.height <= 0) return false;
                    var top = document.elementFromPoint(r.x + r.width/2, r.y + r.height/2);
                    (top || el).click();
                    return true;
                }
                // 1. Seletor por classe real
                var a = document.querySelector('a.dropdown__editar, .dropdown__editar, [class*="editar"]');
                if (a && clicar(a)) return 'editar_clicado_classe';
                // 2. Fallback por texto (item de dropdown)
                var els = document.querySelectorAll('a, button, li');
                for (var i = 0; i < els.length; i++) {
                    var t = (els[i].innerText || '').trim();
                    if (t === 'Editar' || t.endsWith('Editar') || t.indexOf('Editar') !== -1) {
                        if ((els[i].innerText || '').indexOf('Deletar') !== -1) continue;
                        if (clicar(els[i])) return 'editar_clicado_texto';
                    }
                }
                return 'editar_nao_encontrado';
            """)
            if editar_result != "editar_nao_encontrado":
                break
            time.sleep(0.4)
        print(f"Editar: {editar_result}")

        # 5. AGUARDAR o formulário de edição abrir (campo #nome_tarifa visível)
        try:
            wait.until(EC.visibility_of_element_located((By.ID, "nome_tarifa")))
        except Exception:
            menu_dump = driver.execute_script("""
                var out = [];
                var els = document.querySelectorAll('a, li, button, [class*="dropdown"]');
                for (var i = 0; i < els.length; i++) {
                    var e = els[i];
                    var t = (e.innerText || e.textContent || '').trim();
                    if (!t) continue;
                    if (t.indexOf('Editar') === -1 && t.indexOf('Deletar') === -1) continue;
                    var r = e.getBoundingClientRect();
                    out.push({tag:e.tagName, cls:(e.className||'').toString().slice(0,60), t:t.slice(0,30), w:Math.round(r.width), h:Math.round(r.height), x:Math.round(r.x), y:Math.round(r.y)});
                }
                return JSON.stringify(out);
            """)
            raise Exception(
                f"Formulário de edição não abriu (menu={menu_result}, editar={editar_result}) MENU_DUMP: {menu_dump}"
            )
        time.sleep(0.5)

        form_debug = dump_form_estrutura(driver)
        print(f"FORM_DEBUG: {form_debug}")

        # 6. Garantir Nome da área (#nome_tarifa) preenchido
        nome_area_result = preencher_nome_area(driver, wait, area_busca)
        print(f"Nome área: {nome_area_result}")

        # 7. ALTERAR O FATOR MULTIPLICADOR (#fator_tarifa)
        mult_result = driver.execute_script("""
            var valor = arguments[0];
            var inp = document.querySelector('#fator_tarifa');
            if (!inp) return 'fator_ausente';
            var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            inp.focus();
            setter.call(inp, valor);
            inp.dispatchEvent(new Event('input', { bubbles: true }));
            inp.dispatchEvent(new Event('change', { bubbles: true }));
            inp.blur();
            return 'fator_preenchido:' + inp.value;
        """, str(request.multiplicador))
        print(f"Multiplicador: {mult_result}")
        time.sleep(0.3)

        deve_desativar = request.multiplicador <= 1.1

        # 8. SALVAR (#btn-salvar)
        def clicar_salvar():
            return driver.execute_script("""
                var b = document.querySelector('#btn-salvar');
                if (!b) {
                    var bs = document.querySelectorAll('button');
                    for (var i = 0; i < bs.length; i++) {
                        if ((bs[i].innerText || '').indexOf('Salvar') !== -1) { b = bs[i]; break; }
                    }
                }
                if (!b) return 'btn_salvar_ausente';
                var r = b.getBoundingClientRect();
                var top = document.elementFromPoint(r.x + r.width/2, r.y + r.height/2);
                (top || b).click();
                return 'salvar_clicado';
            """)

        try:
            print(f"Salvar: {clicar_salvar()}")
        except UnexpectedAlertPresentException:
            print("Alert ao salvar — preenchendo nome da área e tentando novamente")
            try:
                driver.switch_to.alert.accept()
            except Exception:
                pass
            preencher_nome_area(driver, wait, area_busca)
            time.sleep(0.3)
            clicar_salvar()

        time.sleep(1.5)
        
        # 7. ENVIAR NOTIFICAÇÃO PARA WEBHOOK N8N (logo após salvar)
        try:
            webhook_url = "https://n8n-webhook.api.soureino.com/webhook/1e765e17-4e6d-4b12-a2ac-533c0d981c62"
            
            # Usar timezone de Brasília (UTC-3)
            tz_brasilia = timezone(timedelta(hours=-3))
            agora = datetime.now(tz_brasilia)
            data_atual = agora.strftime("%d/%m/%Y")
            hora_atual = agora.strftime("%H:%M:%S")
            
            # Log para debug
            print(f"Webhook - Cidade: {request.cidade}, Estado: {request.estado}")
            
            # Usar estatísticas passadas como parâmetro OU buscar via fallback
            stats = request.corridas_stats
            if not stats:
                # Fallback: buscar do Supabase se não foi passado
                fallback_stats = buscar_corridas_stats_fallback(request.cidade)
                if fallback_stats:
                    total_corridas = fallback_stats.get('total', 0)
                    canceladas = fallback_stats.get('canceladas', 0)
                    pendentes = fallback_stats.get('pendentes', 0)
                    finalizadas = fallback_stats.get('finalizadas', 0)
                    aceitas = fallback_stats.get('aceitas', 0)
                    em_espera = fallback_stats.get('em_espera', 0)
                    nao_atendidas = fallback_stats.get('nao_atendidas', 0)
                else:
                    total_corridas = canceladas = pendentes = finalizadas = aceitas = em_espera = nao_atendidas = 0
            else:
                total_corridas = stats.total
                canceladas = stats.canceladas
                pendentes = stats.pendentes
                finalizadas = stats.finalizadas
                aceitas = stats.aceitas
                em_espera = stats.em_espera
                nao_atendidas = stats.nao_atendidas
            
            mensagem = f"""CIDADE: {request.cidade}
ESTADO: {request.estado}
DINAMICA ALTERADA PARA: {request.multiplicador}
DIA DA ATUALIZACAO: {data_atual}
HORA DA ATUALIZACAO: {hora_atual}

Status atual: {hora_atual}

🚨 Corridas solicitadas (últimos 15 min): {total_corridas}
🚨 Canceladas: {canceladas}
🚨 Pendentes: {pendentes}
🚨 Não Atendidas: {nao_atendidas}
✅ Finalizadas: {finalizadas}
✅ Aceitas: {aceitas}
✅ Em Espera: {em_espera}"""
            
            # Adicionar OBS de teste apenas se is_test=True
            if request.is_test:
                mensagem += "\n\nOBS: ENVIADO COMO TESTE"
            
            webhook_response = requests.post(
                webhook_url,
                json={"message": mensagem},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            print(f"Webhook n8n enviado: {webhook_response.status_code}")
        except Exception as webhook_error:
            print(f"Erro ao enviar webhook n8n: {webhook_error}")
        
        # 9. ATIVAR/DESATIVAR A DINÂMICA - Voltar para lista, buscar área e clicar no toggle do card
        driver.get("https://cloud.taximachine.com.br/tarifaCategoria/dinamica")
        time.sleep(1.5)

        for _ in range(5):
            acoes = dismiss_onboarding(driver)
            if acoes in ("nenhum", "") or str(acoes).startswith("dismiss_erro"):
                break
            time.sleep(0.4)

        # Clicar na aba Manuais
        driver.execute_script("""
            var alvo = null;
            document.querySelectorAll('button, a, span, div').forEach(function(el) {
                if (!alvo && (el.innerText || '').trim() === 'Manuais') alvo = el;
            });
            if (alvo) alvo.click();
        """)
        time.sleep(0.8)

        # Buscar a área novamente
        driver.execute_script("""
            var areaBusca = arguments[0];
            var inp = document.querySelector('input[placeholder*="Buscar"]');
            if (!inp) return;
            var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            inp.focus();
            setter.call(inp, areaBusca);
            inp.dispatchEvent(new Event('input', { bubbles: true }));
            inp.dispatchEvent(new Event('change', { bubbles: true }));
        """, area_busca)
        print(f"Buscou '{area_busca}' para ajustar toggle")
        time.sleep(1)

        # Ler estado do toggle (input.checkbox dentro de label.switch) do card alvo e clicar se necessário
        toggle_result = driver.execute_script("""
            var area = (arguments[0] || '').toLowerCase();
            var deveDesativar = arguments[1];
            var cards = document.querySelectorAll('.box-fator');
            var alvo = null;
            for (var i = 0; i < cards.length; i++) {
                if ((cards[i].innerText || '').toLowerCase().indexOf(area) !== -1) { alvo = cards[i]; break; }
            }
            if (!alvo && cards.length === 1) alvo = cards[0];
            if (!alvo) return 'card_nao_encontrado';

            var chk = alvo.querySelector('input[type="checkbox"]');
            var lbl = alvo.querySelector('label.switch') || (chk ? chk.closest('label') : null);
            if (!chk || !lbl) return 'toggle_nao_encontrado';

            var estaAtivo = chk.checked === true;
            if (deveDesativar) {
                if (estaAtivo) { lbl.click(); return 'toggle_desativado'; }
                return 'toggle_ja_inativo';
            } else {
                if (!estaAtivo) { lbl.click(); return 'toggle_ativado'; }
                return 'toggle_ja_ativo';
            }
        """, area_busca, deve_desativar)

        print(f"Toggle resultado: {toggle_result} (deve_desativar={deve_desativar})")
        time.sleep(2)
        
        # Screenshot final
        screenshot_path = os.path.join(screenshots_dir, f"dinamica_sucesso_{int(time.time())}.png")
        driver.save_screenshot(screenshot_path)
        
        # MODO POOL: Manter driver no pool (não fechar)
        # Driver será fechado automaticamente após 5 min de inatividade
        release_driver(request.email)
        
        with executions_lock:
            active_executions -= 1
        
        return DinamicaResponse(
            success=True,
            message=f"Dinâmica atualizada com sucesso! Multiplicador: {request.multiplicador}x",
            multiplicador_aplicado=request.multiplicador,
            screenshot_path=screenshot_path
        )
        
    except Exception as e:
        screenshot_path = None
        # Em caso de erro, forçar fechamento do driver
        if driver:
            try:
                screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
                os.makedirs(screenshots_dir, exist_ok=True)
                screenshot_path = os.path.join(screenshots_dir, f"erro_geral_{int(time.time())}.png")
                driver.save_screenshot(screenshot_path)
            except:
                pass
        # Forçar fechamento do driver em caso de erro
        force_close_driver(request.email)
        
        with executions_lock:
            active_executions -= 1
        gc.collect()
        
        return DinamicaResponse(
            success=False,
            message=f"Erro geral: {str(e)} | FORM_DEBUG: {form_debug}",
            screenshot_path=screenshot_path
        )

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    print(f"Iniciando servidor na porta {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
