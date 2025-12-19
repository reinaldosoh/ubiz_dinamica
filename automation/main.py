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

app = FastAPI(title="TaxiMachine Automation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MODO PARALELO: Cada requisição cria seu próprio driver (sem fila)
# Isso pode usar mais memória, mas elimina o delay

# Contador de execuções ativas (apenas para monitoramento)
active_executions = 0
executions_lock = threading.Lock()

class LoginCredentials(BaseModel):
    email: str = "reinaldo@painel.com.br"
    password: str = "Reinaldo@ubizcar10"
    headless: bool = True

class LoginResponse(BaseModel):
    success: bool
    message: str
    screenshot_path: Optional[str] = None

class DinamicaRequest(BaseModel):
    multiplicador: float
    headless: bool = False
    email: str = "reinaldo@painel.com.br"
    password: str = "Reinaldo@ubizcar10"
    cidade: str = "Não informada"
    estado: str = "Não informado"
    is_test: bool = False  # Se True, adiciona "OBS: ENVIADO COMO TESTE" no webhook

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
    MODO PARALELO: Cada requisição cria seu próprio driver Chrome
    Realiza login, navega até Tarifas Dinâmicas, edita ***Geral manual e salva
    """
    global active_executions
    
    # Incrementar contador de execuções ativas
    with executions_lock:
        active_executions += 1
    
    print(f"=== INICIANDO AUTOMAÇÃO (Execuções ativas: {active_executions}) ===")
    print(f"Email recebido: {request.email}")
    print(f"Multiplicador: {request.multiplicador}")
    print(f"Headless: {request.headless}")
    
    driver = None
    try:
        # Criar driver próprio para esta requisição
        driver = create_driver(headless=request.headless)
        wait = WebDriverWait(driver, 20)
        screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # 1. LOGIN - Sempre faz login (cada requisição tem seu próprio driver)
        driver.get("https://cloud.taximachine.com.br/site/login")
        time.sleep(2)
        
        # Verificar se realmente precisa logar (pode já estar logado)
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
                    
                    time.sleep(2)
                    
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
        time.sleep(2)
        
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
        time.sleep(0.5)
        
        # Pressionar ESC uma vez
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.2)
        
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
        time.sleep(1)
        
        # 4. ENCONTRAR "***Geral manual" E CLICAR NOS 3 PONTOS
        # Baseado no screenshot: o card tem texto "***Geral manual" e "Motoristas livres"
        # O ícone de 3 pontos (⋮) está no canto superior direito do card
        
        # Primeiro, encontrar o card e clicar nos 3 pontos
        click_result = driver.execute_script("""
            // Procurar por elementos que contenham "Geral manual"
            var elements = document.querySelectorAll('*');
            var targetCard = null;
            
            for (var i = 0; i < elements.length; i++) {
                var el = elements[i];
                var text = el.innerText || '';
                
                // Encontrar o card específico
                if (text.includes('Geral manual') && text.includes('Motoristas') && !text.includes('Dinâmicas')) {
                    var rect = el.getBoundingClientRect();
                    // Card tem tamanho específico (baseado no screenshot ~180x120)
                    if (rect.width > 100 && rect.width < 250 && rect.height > 80 && rect.height < 200) {
                        targetCard = el;
                        break;
                    }
                }
            }
            
            if (!targetCard) {
                return 'card_not_found';
            }
            
            // Encontrar o botão de 3 pontos - procurar por SVG ou botão no canto direito
            var cardRect = targetCard.getBoundingClientRect();
            var allClickables = targetCard.querySelectorAll('button, svg, [role="button"]');
            
            for (var j = 0; j < allClickables.length; j++) {
                var btn = allClickables[j];
                var btnRect = btn.getBoundingClientRect();
                
                // O botão de 3 pontos está no canto superior direito
                // Verificar se está na parte direita do card
                if (btnRect.left > cardRect.left + cardRect.width * 0.6) {
                    var clickTarget = btn.closest('button') || btn;
                    clickTarget.click();
                    return 'clicked: ' + clickTarget.tagName;
                }
            }
            
            // Fallback: procurar por ícone de menu (3 pontos verticais)
            var svgs = targetCard.querySelectorAll('svg');
            if (svgs.length > 0) {
                var lastSvg = svgs[svgs.length - 1];
                var parent = lastSvg.closest('button') || lastSvg.parentElement;
                parent.click();
                return 'clicked_svg_parent';
            }
            
            return 'button_not_found';
        """)
        
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
        
        time.sleep(1.5)  # Aguardar página de edição carregar
        
        # 5. ALTERAR O FATOR MULTIPLICADOR
        # Usar Selenium para encontrar o input e simular digitação real
        
        # Encontrar o segundo input visível (multiplicador)
        mult_input = driver.execute_script("""
            var inputs = document.querySelectorAll('input');
            var visibleInputs = [];
            for (var i = 0; i < inputs.length; i++) {
                var inp = inputs[i];
                var rect = inp.getBoundingClientRect();
                var type = inp.type || 'text';
                if (rect.width > 0 && rect.height > 0 && type !== 'hidden' && type !== 'checkbox' && type !== 'radio') {
                    visibleInputs.push(inp);
                }
            }
            // Retornar o segundo input (multiplicador)
            return visibleInputs.length >= 2 ? visibleInputs[1] : (visibleInputs[0] || null);
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
        
        time.sleep(2)
        
        # 7. ATIVAR A DINÂMICA - Clicar no toggle APENAS se não estiver ativo
        # Baseado no screenshot: o toggle está no header do card, ao lado do valor "1.2x"
        
        # Primeiro, navegar de volta para a lista de dinâmicas (caso ainda esteja na tela de edição)
        driver.get("https://cloud.taximachine.com.br/tarifaCategoria/dinamica")
        time.sleep(3)  # Aumentado para dar tempo de carregar no Render
        
        # Clicar na aba Manuais
        driver.execute_script("""
            document.querySelectorAll('button, a, span, div').forEach(function(el) {
                if (el.innerText && el.innerText.trim() === 'Manuais') {
                    el.click();
                }
            });
        """)
        time.sleep(2)  # Aumentado para Render
        
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
        
        # Encontrar e clicar no toggle do card "Geral manual"
        # O toggle está ao lado do texto "Dinâmica" dentro do card
        
        # Estratégia mais robusta: buscar em toda a página por toggles/switches
        toggle_result = driver.execute_script("""
            console.log('=== BUSCANDO TOGGLE GERAL MANUAL (ESTRATÉGIA ROBUSTA) ===');
            
            // Estratégia 0: Buscar TODOS os switches/toggles na página primeiro
            var allSwitches = document.querySelectorAll('[class*="switch"], [class*="Switch"], [role="switch"], input[type="checkbox"]');
            console.log('Total de switches na página:', allSwitches.length);
            
            // Procurar o card "Geral manual" com critérios mais flexíveis
            var allDivs = document.querySelectorAll('div');
            var targetCard = null;
            
            for (var i = 0; i < allDivs.length; i++) {
                var div = allDivs[i];
                var text = div.innerText || '';
                var rect = div.getBoundingClientRect();
                
                // Card deve conter "Geral manual" - critérios de tamanho mais flexíveis
                if (text.includes('Geral manual') && 
                    rect.width > 80 && rect.width < 400 && 
                    rect.height > 50 && rect.height < 300) {
                    targetCard = div;
                    console.log('Card Geral manual encontrado:', rect.width, 'x', rect.height);
                    break;
                }
            }
            
            if (!targetCard) {
                // Fallback: procurar apenas pelo texto "Geral manual"
                var allElements = document.querySelectorAll('*');
                for (var i = 0; i < allElements.length; i++) {
                    var el = allElements[i];
                    if ((el.innerText || '').includes('Geral manual')) {
                        // Subir na árvore DOM para encontrar o card pai
                        var parent = el;
                        for (var j = 0; j < 5; j++) {
                            parent = parent.parentElement;
                            if (!parent) break;
                            var rect = parent.getBoundingClientRect();
                            if (rect.width > 100 && rect.height > 80) {
                                targetCard = parent;
                                console.log('Card encontrado via fallback:', rect.width, 'x', rect.height);
                                break;
                            }
                        }
                        if (targetCard) break;
                    }
                }
            }
            
            if (!targetCard) {
                return 'card_geral_manual_not_found';
            }
            
            // Estratégia 1: Procurar por classe que contenha switch/toggle dentro do card
            var switchElements = targetCard.querySelectorAll('[class*="switch"], [class*="Switch"], [class*="toggle"], [class*="Toggle"]');
            console.log('Elementos switch/toggle no card:', switchElements.length);
            
            for (var j = 0; j < switchElements.length; j++) {
                var sw = switchElements[j];
                var rect = sw.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    sw.click();
                    console.log('Clicou em switch:', sw.className);
                    return 'clicked_switch_class: ' + sw.className;
                }
            }
            
            // Estratégia 2: Procurar input checkbox
            var checkboxes = targetCard.querySelectorAll('input[type="checkbox"]');
            console.log('Checkboxes encontrados:', checkboxes.length);
            
            for (var k = 0; k < checkboxes.length; k++) {
                var cb = checkboxes[k];
                cb.click();
                console.log('Clicou em checkbox');
                return 'clicked_checkbox';
            }
            
            // Estratégia 3: Procurar elemento com role="switch"
            var roleSwitches = targetCard.querySelectorAll('[role="switch"]');
            if (roleSwitches.length > 0) {
                roleSwitches[0].click();
                return 'clicked_role_switch';
            }
            
            // Estratégia 4: Procurar botão dentro do card que possa ser o toggle
            var buttons = targetCard.querySelectorAll('button');
            console.log('Botões no card:', buttons.length);
            for (var b = 0; b < buttons.length; b++) {
                var btn = buttons[b];
                var rect = btn.getBoundingClientRect();
                // Toggle geralmente é pequeno
                if (rect.width < 80 && rect.height < 40) {
                    btn.click();
                    console.log('Clicou em botão pequeno:', rect.width, 'x', rect.height);
                    return 'clicked_small_button';
                }
            }
            
            // Estratégia 5: Procurar por elemento pequeno e arredondado
            var allCardElements = targetCard.querySelectorAll('*');
            for (var n = 0; n < allCardElements.length; n++) {
                var el = allCardElements[n];
                var rect = el.getBoundingClientRect();
                var style = window.getComputedStyle(el);
                var borderRadius = style.borderRadius;
                var bgColor = style.backgroundColor;
                
                // Elemento pequeno e arredondado com cor de fundo
                if (rect.width >= 15 && rect.width <= 60 && 
                    rect.height >= 10 && rect.height <= 35 &&
                    bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent') {
                    el.click();
                    console.log('Clicou em elemento arredondado colorido:', el.tagName, rect.width, 'x', rect.height, bgColor);
                    return 'clicked_colored_element';
                }
            }
            
            // Estratégia 6: Clicar no primeiro elemento clicável após "Dinâmica"
            var dinamicaFound = false;
            for (var m = 0; m < allCardElements.length; m++) {
                var el = allCardElements[m];
                var text = (el.innerText || '').trim();
                
                if (text === 'Dinâmica' || text.includes('Dinâmica')) {
                    dinamicaFound = true;
                    continue;
                }
                
                if (dinamicaFound) {
                    var rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0 && rect.width < 100) {
                        el.click();
                        console.log('Clicou após Dinâmica:', el.tagName);
                        return 'clicked_after_dinamica';
                    }
                }
            }
            
            return 'toggle_not_found';
        """)
        
        print(f"Toggle resultado: {toggle_result}")
        time.sleep(2)  # Aumentado para Render
        
        # Screenshot final
        screenshot_path = os.path.join(screenshots_dir, f"dinamica_sucesso_{int(time.time())}.png")
        driver.save_screenshot(screenshot_path)
        
        # 8. ENVIAR NOTIFICAÇÃO PARA WEBHOOK N8N
        try:
            webhook_url = "https://n8n-webhook.api.soureino.com/webhook/1e765e17-4e6d-4b12-a2ac-533c0d981c62"
            
            # Usar timezone de Brasília (UTC-3)
            tz_brasilia = timezone(timedelta(hours=-3))
            agora = datetime.now(tz_brasilia)
            data_atual = agora.strftime("%d/%m/%Y")
            hora_atual = agora.strftime("%H:%M:%S")
            
            # Log para debug
            print(f"Webhook - Cidade: {request.cidade}, Estado: {request.estado}")
            
            mensagem = f"""CIDADE: {request.cidade}
ESTADO: {request.estado}
DINAMICA ALTERADA PARA: {request.multiplicador}
DIA DA ATUALIZACAO: {data_atual}
HORA DA ATUALIZACAO: {hora_atual}"""
            
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
        
        # MODO PARALELO: Fechar driver após uso e decrementar contador
        if driver:
            try:
                driver.quit()
            except:
                pass
        with executions_lock:
            active_executions -= 1
        gc.collect()  # Forçar coleta de lixo para liberar memória
        
        return DinamicaResponse(
            success=True,
            message=f"Dinâmica atualizada com sucesso! Multiplicador: {request.multiplicador}x",
            multiplicador_aplicado=request.multiplicador,
            screenshot_path=screenshot_path
        )
        
    except Exception as e:
        screenshot_path = None
        if driver:
            try:
                screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
                os.makedirs(screenshots_dir, exist_ok=True)
                screenshot_path = os.path.join(screenshots_dir, f"erro_geral_{int(time.time())}.png")
                driver.save_screenshot(screenshot_path)
            except:
                pass
            try:
                driver.quit()
            except:
                pass
        
        # Decrementar contador em caso de erro
        with executions_lock:
            active_executions -= 1
        gc.collect()  # Forçar coleta de lixo para liberar memória
        
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
