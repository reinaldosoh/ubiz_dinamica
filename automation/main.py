from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        "mode": "parallel"
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
        
        # FECHAR MODAL - Baseado no print 6.png
        # O X está no canto superior direito do modal branco
        def fechar_modal():
            # Encontrar coordenadas do X e clicar
            coords = driver.execute_script("""
                // Procurar o modal pelo conteúdo
                var elements = document.querySelectorAll('*');
                for (var i = 0; i < elements.length; i++) {
                    var el = elements[i];
                    var text = el.innerText || '';
                    // Encontrar o container do modal
                    if (text.includes('Dinâmica automática') && text.includes('Explorar')) {
                        var rect = el.getBoundingClientRect();
                        // O X está aproximadamente no canto superior direito
                        // Baseado no print: modal tem ~400px de largura, X está a ~20px da borda direita e ~20px do topo
                        return {
                            x: rect.right - 25,
                            y: rect.top + 25,
                            found: true
                        };
                    }
                }
                return { found: false };
            """)
            
            if coords and coords.get('found'):
                # Clicar nas coordenadas do X
                ActionChains(driver).move_by_offset(coords['x'], coords['y']).click().perform()
                ActionChains(driver).move_by_offset(-coords['x'], -coords['y']).perform()
                return True
            return False
        
        # Tentar fechar via JavaScript direto - FORÇAR REMOÇÃO
        driver.execute_script("""
            // Remover TODOS os elementos que parecem ser modais/overlays
            var toRemove = [];
            document.querySelectorAll('*').forEach(function(el) {
                var style = window.getComputedStyle(el);
                var text = el.innerText || '';
                // Se tem position fixed/absolute e está visível, pode ser modal
                if ((style.position === 'fixed' || style.position === 'absolute') && 
                    style.display !== 'none' && 
                    text.includes('Dinâmica automática')) {
                    toRemove.push(el);
                }
            });
            toRemove.forEach(function(el) { el.remove(); });
            
            // Remover backdrops
            document.querySelectorAll('[class*="backdrop"], [class*="overlay"], [class*="modal"]').forEach(function(el) {
                el.remove();
            });
        """)
        time.sleep(0.2)  # OTIMIZADO: 0.5s -> 0.2s
        
        # Pressionar ESC uma vez
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.1)  # OTIMIZADO: 0.2s -> 0.1s
        
        # 3. CLICAR NA ABA "MANUAIS" via JavaScript (RÁPIDO)
        driver.execute_script("""
            var clicked = false;
            document.querySelectorAll('button, a, span, div').forEach(function(el) {
                if (!clicked && el.innerText && el.innerText.trim() === 'Manuais') {
                    el.click();
                    clicked = true;
                }
            });
        """)
        time.sleep(0.5)  # OTIMIZADO: 1s -> 0.5s
        
        # 3.5. DIGITAR termo de busca no campo para filtrar o card correto
        search_result = driver.execute_script("""
            var areaBusca = arguments[0];
            // Encontrar o campo de busca (input com placeholder de busca ou ícone de lupa)
            var searchInput = null;
            var inputs = document.querySelectorAll('input');
            
            for (var i = 0; i < inputs.length; i++) {
                var inp = inputs[i];
                var rect = inp.getBoundingClientRect();
                var placeholder = (inp.placeholder || '').toLowerCase();
                var type = inp.type || 'text';
                
                // Ignorar inputs invisíveis
                if (rect.width <= 0 || rect.height <= 0) continue;
                if (type === 'hidden' || type === 'checkbox' || type === 'radio' || type === 'number') continue;
                
                // Campo de busca geralmente tem placeholder ou está no topo
                if (placeholder.includes('busca') || placeholder.includes('pesquis') || 
                    placeholder.includes('search') || placeholder.includes('filtro') ||
                    rect.top < 400) {
                    searchInput = inp;
                    break;
                }
            }
            
            if (searchInput) {
                searchInput.focus();
                searchInput.value = areaBusca;
                
                var inputEvent = new Event('input', { bubbles: true });
                searchInput.dispatchEvent(inputEvent);
                var changeEvent = new Event('change', { bubbles: true });
                searchInput.dispatchEvent(changeEvent);
                
                return 'busca_preenchida';
            }
            return 'campo_busca_nao_encontrado';
        """, area_busca)
        print(f"Campo de busca: {search_result}")
        time.sleep(0.5)  # OTIMIZADO: 1s -> 0.5s
        
        # 4. ENCONTRAR CARD DE DINÂMICA E CLICAR NOS 3 PONTOS
        # Agora o card "***Geral Manual" deve estar visível após a busca
        
        click_result = driver.execute_script("""
            var areaBusca = (arguments[0] || '').toLowerCase();
            var elements = document.querySelectorAll('*');
            var targetCard = null;
            
            var possibleTexts = ['manual'];
            if (areaBusca) possibleTexts.unshift(areaBusca + ' manual', areaBusca);
            
            for (var i = 0; i < elements.length; i++) {
                var el = elements[i];
                var text = el.innerText || '';
                var rect = el.getBoundingClientRect();
                
                // Card deve ter tamanho razoável e estar visível
                if (rect.width < 100 || rect.width > 400 || rect.height < 50 || rect.height > 300) continue;
                if (rect.top < 0 || rect.left < 0) continue;
                
                // Verificar se contém algum dos textos possíveis
                for (var j = 0; j < possibleTexts.length; j++) {
                    if (text.includes(possibleTexts[j]) && !text.includes('Dinâmicas automáticas')) {
                        targetCard = el;
                        console.log('Card encontrado com texto:', possibleTexts[j]);
                        break;
                    }
                }
                if (targetCard) break;
            }
            
            // Estratégia 2: Se não encontrou, procurar o primeiro card visível na aba Manuais
            if (!targetCard) {
                var cards = document.querySelectorAll('[class*="card"], [class*="Card"]');
                for (var k = 0; k < cards.length; k++) {
                    var card = cards[k];
                    var rect = card.getBoundingClientRect();
                    if (rect.width > 100 && rect.width < 400 && rect.height > 50 && rect.height < 300) {
                        if (rect.top > 100 && rect.left > 0) {
                            targetCard = card;
                            console.log('Card encontrado via classe card');
                            break;
                        }
                    }
                }
            }
            
            if (!targetCard) {
                return 'card_not_found';
            }
            
            // Encontrar o botão de 3 pontos (menu)
            var cardRect = targetCard.getBoundingClientRect();
            var allClickables = targetCard.querySelectorAll('button, svg, [role="button"]');
            
            for (var m = 0; m < allClickables.length; m++) {
                var btn = allClickables[m];
                var btnRect = btn.getBoundingClientRect();
                
                // O botão de 3 pontos está no canto superior direito
                if (btnRect.left > cardRect.left + cardRect.width * 0.5) {
                    var clickTarget = btn.closest('button') || btn;
                    clickTarget.click();
                    return 'clicked: ' + clickTarget.tagName;
                }
            }
            
            // Fallback: clicar no último SVG do card (geralmente é o menu)
            var svgs = targetCard.querySelectorAll('svg');
            if (svgs.length > 0) {
                var lastSvg = svgs[svgs.length - 1];
                var parent = lastSvg.closest('button') || lastSvg.parentElement;
                if (parent) {
                    parent.click();
                    return 'clicked_svg_parent';
                }
            }
            
            return 'button_not_found';
        """, area_busca)
        
        print(f"Resultado clique menu: {click_result}")
        time.sleep(0.3)
        
        # Clicar em "Editar" - usar elemento encontrado pelo Selenium e clicar com JavaScript
        try:
            # Encontrar todos os elementos com texto "Editar"
            editar_elements = driver.find_elements(By.XPATH, "//*[normalize-space(text())='Editar']")
            
            clicked = False
            for el in editar_elements:
                try:
                    if el.is_displayed() and el.size['width'] > 0:
                        # Usar JavaScript para forçar o clique
                        driver.execute_script("arguments[0].click();", el)
                        clicked = True
                        print(f"Clicou em Editar via JS: {el.tag_name}")
                        break
                except:
                    continue
            
            if not clicked:
                # Tentar encontrar link <a> com href contendo "edit"
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    if "Editar" in link.text:
                        driver.execute_script("arguments[0].click();", link)
                        print("Clicou em link Editar")
                        break
        except Exception as e:
            print(f"Erro ao clicar em Editar: {e}")
        
        time.sleep(0.8)  # OTIMIZADO: 1.5s -> 0.8s
        
        # 5. Preencher NOME DA ÁREA (obrigatório no formulário de edição TM)
        nome_area_result = driver.execute_script("""
            var areaNome = arguments[0];
            var inputs = document.querySelectorAll('input, textarea');

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

            function preencher(inp, valor) {
                inp.focus();
                inp.value = valor;
                inp.dispatchEvent(new Event('input', { bubbles: true }));
                inp.dispatchEvent(new Event('change', { bubbles: true }));
            }

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
                    (label.includes('nome') && (label.includes('área') || label.includes('area'))) ||
                    (placeholder.includes('nome') && (placeholder.includes('área') || placeholder.includes('area'))) ||
                    (name.includes('nome') && (name.includes('area') || name.includes('área')));

                if (pareceNomeArea) {
                    preencher(inp, areaNome);
                    return 'nome_area_label:' + areaNome;
                }
            }

            // Fallback: primeiro input text visível (geralmente é o nome da área)
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
                preencher(visibleText[0], areaNome);
                return 'nome_area_primeiro_text:' + areaNome;
            }
            return 'nome_area_nao_encontrado';
        """, area_busca)
        print(f"Nome área formulário: {nome_area_result}")
        time.sleep(0.3)

        # 6. ALTERAR O FATOR MULTIPLICADOR
        # Usar Selenium para encontrar o input e simular digitação real
        
        # Encontrar o input do multiplicador (tipo number ou com valor numérico decimal)
        mult_input = driver.execute_script("""
            var inputs = document.querySelectorAll('input');
            var multiplicadorInput = null;
            
            for (var i = 0; i < inputs.length; i++) {
                var inp = inputs[i];
                var rect = inp.getBoundingClientRect();
                var type = inp.type || 'text';
                var value = inp.value || '';
                var placeholder = inp.placeholder || '';
                var name = inp.name || '';
                
                // Ignorar inputs invisíveis ou especiais
                if (rect.width <= 0 || rect.height <= 0) continue;
                if (type === 'hidden' || type === 'checkbox' || type === 'radio') continue;
                if (type === 'text' || type === 'search') continue;
                
                // Estratégia 1: Input do tipo number
                if (type === 'number') {
                    multiplicadorInput = inp;
                    console.log('Encontrou input type=number');
                    break;
                }
                
                // Estratégia 2: Valor parece ser um multiplicador (1.0 a 3.0)
                var numValue = parseFloat(value);
                if (!isNaN(numValue) && numValue >= 1.0 && numValue <= 3.0 && value.includes('.')) {
                    multiplicadorInput = inp;
                    console.log('Encontrou input com valor multiplicador:', value);
                    break;
                }
                
                // Estratégia 3: Placeholder ou name contém "multiplicador" ou "fator"
                var lowerPlaceholder = placeholder.toLowerCase();
                var lowerName = name.toLowerCase();
                if (lowerPlaceholder.includes('multiplicador') || lowerPlaceholder.includes('fator') ||
                    lowerName.includes('multiplicador') || lowerName.includes('fator')) {
                    multiplicadorInput = inp;
                    console.log('Encontrou input por placeholder/name');
                    break;
                }
            }
            
            // Fallback: pegar o segundo input visível que não seja o nome
            if (!multiplicadorInput) {
                var visibleInputs = [];
                for (var j = 0; j < inputs.length; j++) {
                    var inp2 = inputs[j];
                    var rect2 = inp2.getBoundingClientRect();
                    var type2 = inp2.type || 'text';
                    if (rect2.width > 0 && rect2.height > 0 && type2 !== 'hidden' && type2 !== 'checkbox' && type2 !== 'radio') {
                        visibleInputs.push(inp2);
                    }
                }
                // O segundo input geralmente é o multiplicador
                if (visibleInputs.length >= 2) {
                    multiplicadorInput = visibleInputs[1];
                    console.log('Usando fallback: segundo input visível');
                }
            }
            
            return multiplicadorInput;
        """)
        
        if mult_input:
            # Limpar o campo usando JavaScript e preencher
            driver.execute_script("""
                var input = arguments[0];
                var value = arguments[1];
                input.focus();
                input.select();
                // Limpar usando execCommand
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
            """, mult_input, str(request.multiplicador))
            time.sleep(0.1)
            
            # Digitar o novo valor usando send_keys
            mult_input.send_keys(str(request.multiplicador))
            
            # Disparar eventos para frameworks reativos
            driver.execute_script("""
                var input = arguments[0];
                var value = arguments[1];
                
                // Criar e disparar InputEvent (mais compatível com React/Vue)
                var inputEvent = new InputEvent('input', {
                    bubbles: true,
                    cancelable: true,
                    inputType: 'insertText',
                    data: value
                });
                input.dispatchEvent(inputEvent);
                
                // Disparar change event
                var changeEvent = new Event('change', { bubbles: true });
                input.dispatchEvent(changeEvent);
                
                // Blur para finalizar
                input.blur();
            """, mult_input, str(request.multiplicador))
            
            print(f"Preencheu multiplicador: {request.multiplicador}")
        else:
            print("Não encontrou campo de multiplicador")
        
        time.sleep(0.5)
        
        # 5.5. VERIFICAR TOGGLE NA TELA DE EDIÇÃO
        # Se multiplicador for 1.0 ou 1.1 -> DESATIVAR toggle
        # Caso contrário -> ATIVAR toggle
        deve_desativar = request.multiplicador <= 1.1
        
        toggle_ativado = driver.execute_script("""
            var deveDesativar = arguments[0];
            // Procurar toggle/switch na tela de edição
            var switches = document.querySelectorAll('[role="switch"], [data-state], input[type="checkbox"]');
            console.log('Switches encontrados na tela de edição:', switches.length);
            console.log('Deve desativar (mult <= 1.1):', deveDesativar);
            
            for (var i = 0; i < switches.length; i++) {
                var sw = switches[i];
                var rect = sw.getBoundingClientRect();
                if (rect.width <= 0 || rect.height <= 0) continue;
                
                var ariaChecked = sw.getAttribute('aria-checked');
                var dataState = sw.getAttribute('data-state');
                var isChecked = sw.checked;
                var estaAtivo = ariaChecked === 'true' || dataState === 'checked' || dataState === 'on' || isChecked === true;
                
                console.log('Toggle edição - aria-checked:', ariaChecked, 'data-state:', dataState, 'checked:', isChecked, 'estaAtivo:', estaAtivo);
                
                if (deveDesativar) {
                    // MULTIPLICADOR 1.0 ou 1.1: Queremos DESATIVAR
                    if (estaAtivo) {
                        console.log('Toggle na edição ATIVO - CLICANDO PARA DESATIVAR (mult <= 1.1)');
                        sw.click();
                        return 'desativado';
                    } else {
                        console.log('Toggle na edição JÁ ESTÁ INATIVO - NÃO CLICAR');
                        return 'ja_inativo';
                    }
                } else {
                    // MULTIPLICADOR > 1.1: Queremos ATIVAR
                    if (estaAtivo) {
                        console.log('Toggle na edição JÁ ESTÁ ATIVO - NÃO CLICAR');
                        return 'ja_ativo';
                    } else {
                        console.log('Toggle na edição INATIVO - CLICANDO PARA ATIVAR');
                        sw.click();
                        return 'ativado';
                    }
                }
            }
            return 'nao_encontrado';
        """, deve_desativar)
        print(f"Toggle na edição: {toggle_ativado} (deve_desativar={deve_desativar})")
        
        time.sleep(0.3)
        
        # 6. SALVAR ALTERAÇÕES - Encontrar e clicar no botão
        try:
            salvar_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Salvar')]")
            driver.execute_script("arguments[0].click();", salvar_btn)
            print("Clicou em Salvar")
        except:
            # Fallback via JavaScript
            driver.execute_script("""
                document.querySelectorAll('button').forEach(function(btn) {
                    if (btn.innerText && btn.innerText.includes('Salvar')) {
                        btn.click();
                    }
                });
            """)
        
        time.sleep(1)  # OTIMIZADO: 2s -> 1s
        
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
        
        # 8. ATIVAR A DINÂMICA - Voltar para lista, buscar ***Geral e ativar toggle
        
        # Navegar de volta para a lista de dinâmicas
        driver.get("https://cloud.taximachine.com.br/tarifaCategoria/dinamica")
        time.sleep(1.5)  # OTIMIZADO: 3s -> 1.5s
        
        # Clicar na aba Manuais
        driver.execute_script("""
            document.querySelectorAll('button, a, span, div').forEach(function(el) {
                if (el.innerText && el.innerText.trim() === 'Manuais') {
                    el.click();
                }
            });
        """)
        time.sleep(0.5)  # OTIMIZADO: 1s -> 0.5s
        
        # Buscar termo de área novamente para encontrar o card
        driver.execute_script("""
            var areaBusca = arguments[0];
            var inputs = document.querySelectorAll('input');
            for (var i = 0; i < inputs.length; i++) {
                var inp = inputs[i];
                var rect = inp.getBoundingClientRect();
                var type = inp.type || 'text';
                if (rect.width > 0 && rect.height > 0 && type !== 'hidden' && type !== 'checkbox' && type !== 'radio' && type !== 'number') {
                    inp.focus();
                    inp.value = areaBusca;
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                    break;
                }
            }
        """, area_busca)
        print(f"Buscou '{area_busca}' para ativar toggle")
        time.sleep(1)  # OTIMIZADO: 2s -> 1s
        
        # FECHAR MODAL SE ESTIVER ABERTO (modal "Dinâmica automática")
        driver.execute_script("""
            // Fechar qualquer modal aberto
            var closeButtons = document.querySelectorAll('button[aria-label="Close"], .close, [data-dismiss="modal"], button');
            for (var i = 0; i < closeButtons.length; i++) {
                var btn = closeButtons[i];
                var text = btn.innerText || '';
                var ariaLabel = btn.getAttribute('aria-label') || '';
                
                // Procurar X de fechar ou botão com ×
                if (text === '×' || text === 'x' || text === 'X' || ariaLabel.toLowerCase().includes('close')) {
                    btn.click();
                    console.log('Modal fechado');
                    break;
                }
            }
            
            // Também tentar clicar fora do modal
            var modals = document.querySelectorAll('.modal-backdrop, .modal');
            modals.forEach(function(m) {
                if (m.classList.contains('modal-backdrop')) {
                    m.click();
                }
            });
        """)
        time.sleep(0.5)
        
        # Encontrar e verificar o toggle do card ***Geral Manual
        # Se multiplicador <= 1.1 -> DESATIVAR toggle
        # Caso contrário -> ATIVAR toggle
        
        toggle_result = driver.execute_script("""
            var deveDesativar = arguments[0];
            console.log('=== VERIFICANDO TOGGLE ***GERAL MANUAL ===');
            console.log('Deve desativar (mult <= 1.1):', deveDesativar);
            
            // Procurar por elementos com role="switch" ou data-state (padrão comum de toggles)
            var switches = document.querySelectorAll('[role="switch"], [data-state], input[type="checkbox"]');
            console.log('Switches encontrados:', switches.length);
            
            for (var i = 0; i < switches.length; i++) {
                var sw = switches[i];
                var rect = sw.getBoundingClientRect();
                
                // Ignorar elementos invisíveis
                if (rect.width <= 0 || rect.height <= 0) continue;
                if (rect.top < 300) continue; // Ignorar elementos no topo (header)
                
                var ariaChecked = sw.getAttribute('aria-checked');
                var dataState = sw.getAttribute('data-state');
                var isChecked = sw.checked;
                var estaAtivo = ariaChecked === 'true' || dataState === 'checked' || dataState === 'on' || isChecked === true;
                
                console.log('Switch encontrado - aria-checked:', ariaChecked, 'data-state:', dataState, 'checked:', isChecked, 'estaAtivo:', estaAtivo);
                
                if (deveDesativar) {
                    // MULTIPLICADOR 1.0 ou 1.1: Queremos DESATIVAR
                    if (estaAtivo) {
                        console.log('>>> TOGGLE ATIVO - CLICANDO PARA DESATIVAR (mult <= 1.1)');
                        sw.click();
                        return 'toggle_desativado';
                    } else {
                        console.log('>>> TOGGLE JÁ ESTÁ INATIVO - NÃO CLICAR');
                        return 'toggle_ja_inativo';
                    }
                } else {
                    // MULTIPLICADOR > 1.1: Queremos ATIVAR
                    if (estaAtivo) {
                        console.log('>>> TOGGLE JÁ ESTÁ ATIVO - NÃO CLICAR');
                        return 'toggle_ja_ativo';
                    } else {
                        console.log('>>> TOGGLE INATIVO - CLICANDO PARA ATIVAR');
                        sw.click();
                        return 'toggle_ativado';
                    }
                }
            }
            
            // Fallback: Procurar por elementos visuais que parecem toggles
            var allElements = document.querySelectorAll('button, div, span');
            
            for (var j = 0; j < allElements.length; j++) {
                var el = allElements[j];
                var rect = el.getBoundingClientRect();
                var style = window.getComputedStyle(el);
                var bgColor = style.backgroundColor;
                var borderRadius = style.borderRadius;
                
                // Toggle típico: largura 30-50px, altura 15-30px, borda arredondada
                if (rect.width >= 30 && rect.width <= 60 && 
                    rect.height >= 15 && rect.height <= 35 &&
                    rect.top > 300 &&
                    borderRadius && parseInt(borderRadius) >= 8) {
                    
                    // Verificar cor de fundo para determinar estado
                    var rgbMatch = bgColor.match(/rgb[a]?\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)/);
                    if (rgbMatch) {
                        var r = parseInt(rgbMatch[1]);
                        var g = parseInt(rgbMatch[2]);
                        var b = parseInt(rgbMatch[3]);
                        
                        console.log('Toggle visual encontrado - RGB:', r, g, b);
                        
                        // VERDE ou AZUL = ATIVO
                        var corAtiva = (g > 100 && g > r) || (b > 100 && b > r && b > g);
                        // CINZA = INATIVO
                        var maxDiff = Math.max(Math.abs(r-g), Math.abs(g-b), Math.abs(r-b));
                        var corInativa = maxDiff < 40 && r < 200;
                        
                        if (deveDesativar) {
                            // MULTIPLICADOR 1.0 ou 1.1: Queremos DESATIVAR
                            if (corAtiva) {
                                console.log('>>> TOGGLE COLORIDO (ativo) - CLICANDO PARA DESATIVAR (mult <= 1.1)');
                                el.click();
                                return 'toggle_desativado';
                            } else if (corInativa) {
                                console.log('>>> TOGGLE CINZA (inativo) - JÁ ESTÁ DESATIVADO');
                                return 'toggle_ja_inativo_cor';
                            }
                        } else {
                            // MULTIPLICADOR > 1.1: Queremos ATIVAR
                            if (corAtiva) {
                                console.log('>>> TOGGLE COLORIDO (ativo) - NÃO CLICAR');
                                return 'toggle_ja_ativo_cor';
                            } else if (corInativa) {
                                console.log('>>> TOGGLE CINZA (inativo) - CLICANDO PARA ATIVAR');
                                el.click();
                                return 'toggle_ativado';
                            }
                        }
                    }
                }
            }
            
            console.log('Nenhum toggle encontrado ou não foi possível determinar estado');
            return 'toggle_nao_encontrado_ou_indeterminado';
        """, deve_desativar)
        
        print(f"Toggle resultado: {toggle_result} (deve_desativar={deve_desativar})")
        time.sleep(2)  # Aumentado para Render
        
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
            message=f"Erro geral: {str(e)}",
            screenshot_path=screenshot_path
        )

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    print(f"Iniciando servidor na porta {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
