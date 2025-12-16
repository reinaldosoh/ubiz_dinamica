<template>
  <div class="min-h-screen bg-bg-primary">
    <!-- Header -->
    <header class="bg-bg-secondary border-b border-border-secondary">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <NuxtLink to="/cidades" class="text-text-tertiary hover:text-text-primary transition-colors">
              <ArrowLeft class="w-5 h-5" />
            </NuxtLink>
            <div>
              <h1 class="text-2xl font-bold text-text-primary">Automação TaxiMachine</h1>
              <p class="text-text-tertiary text-sm">Login automatizado via Selenium</p>
            </div>
          </div>
          <button 
            @click="checkHealth" 
            class="btn-secondary flex items-center gap-2"
          >
            <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': checkingHealth }" />
            Verificar Status
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Cards de Status -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="card">
          <div class="flex items-center gap-4">
            <div 
              class="w-12 h-12 rounded-lg flex items-center justify-center"
              :class="apiStatus === 'online' ? 'bg-green-400/10' : 'bg-red-400/10'"
            >
              <Wifi 
                class="w-6 h-6" 
                :class="apiStatus === 'online' ? 'text-green-400' : 'text-red-400'"
              />
            </div>
            <div>
              <p class="text-text-tertiary text-sm">Status da API</p>
              <p 
                class="text-xl font-bold"
                :class="apiStatus === 'online' ? 'text-green-400' : 'text-red-400'"
              >
                {{ apiStatus === 'online' ? 'Online' : 'Offline' }}
              </p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-lg bg-blue-400/10 flex items-center justify-center">
              <Monitor class="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <p class="text-text-tertiary text-sm">Servidor</p>
              <p class="text-xl font-bold text-blue-400">localhost:8000</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-lg bg-purple-400/10 flex items-center justify-center">
              <Bot class="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <p class="text-text-tertiary text-sm">Engine</p>
              <p class="text-xl font-bold text-purple-400">Selenium + Chrome</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Seletor de Cidade -->
      <div class="card mb-8">
        <h2 class="card-title mb-4">Selecionar Cidade</h2>
        
        <div v-if="loadingCidades" class="flex items-center gap-2 text-text-tertiary">
          <Loader2 class="w-4 h-4 animate-spin" />
          Carregando cidades...
        </div>
        
        <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button
            v-for="cidade in cidades"
            :key="cidade.id"
            @click="cidadeSelecionada = cidade"
            class="p-4 rounded-lg border transition-all text-left"
            :class="cidadeSelecionada?.id === cidade.id 
              ? 'bg-primary/10 border-primary text-primary' 
              : 'bg-bg-tertiary border-border-secondary hover:border-primary/50 text-text-primary'"
          >
            <div class="flex items-center gap-2 mb-1">
              <MapPin class="w-4 h-4" />
              <span class="font-medium">{{ cidade.nome }}</span>
            </div>
            <div class="flex items-center gap-2 text-xs">
              <span 
                class="px-1.5 py-0.5 rounded"
                :class="cidade.automation_ativo && cidade.automation_email 
                  ? 'bg-green-400/20 text-green-400' 
                  : 'bg-yellow-400/20 text-yellow-400'"
              >
                {{ cidade.automation_ativo && cidade.automation_email ? 'Configurada' : 'Pendente' }}
              </span>
            </div>
          </button>
        </div>

        <div v-if="cidadeSelecionada && !cidadeSelecionada.automation_email" class="mt-4 bg-yellow-400/10 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle class="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <p class="text-yellow-400 font-medium">Credenciais não configuradas</p>
            <p class="text-text-tertiary text-sm mt-1">
              Configure as credenciais de automação na página de <NuxtLink to="/cidades" class="text-primary underline">Cidades</NuxtLink>.
            </p>
          </div>
        </div>

        <div v-if="cidadeSelecionada && cidadeSelecionada.automation_email" class="mt-4 bg-bg-tertiary rounded-lg p-4">
          <p class="text-text-tertiary text-sm">
            <strong class="text-text-primary">Email:</strong> {{ cidadeSelecionada.automation_email }}
          </p>
          <p class="text-text-tertiary text-sm mt-1">
            <strong class="text-text-primary">API:</strong> {{ cidadeSelecionada.automation_url || 'localhost:8000' }}
          </p>
        </div>
      </div>

      <!-- Atualizar Dinâmica -->
      <div class="card mb-8">
        <h2 class="card-title mb-6">Atualizar Dinâmica TaxiMachine</h2>
        
        <div class="bg-bg-tertiary rounded-lg p-6 border border-border-secondary mb-6">
          <div class="flex flex-col md:flex-row md:items-end gap-4">
            <div class="flex-1">
              <label class="block text-text-secondary text-sm mb-2">Fator Multiplicador</label>
              <div class="relative">
                <input 
                  v-model.number="multiplicador"
                  type="number"
                  step="0.1"
                  min="1"
                  max="5"
                  class="w-full bg-bg-primary border border-border-secondary rounded-lg px-4 py-3 text-text-primary text-xl font-bold focus:outline-none focus:border-primary"
                  placeholder="1.3"
                />
                <span class="absolute right-4 top-1/2 -translate-y-1/2 text-text-tertiary text-xl font-bold">x</span>
              </div>
              <p class="text-text-tertiary text-xs mt-2">Valor entre 1.0 e 5.0 (ex: 1.3 = 30% de aumento)</p>
            </div>
            
            <div class="flex gap-3">
              <button 
                @click="executarDinamica(true)"
                :disabled="loading || apiStatus === 'offline' || !multiplicador"
                class="btn-secondary flex items-center gap-2 whitespace-nowrap"
              >
                <Loader2 v-if="loading && loadingMode === 'dinamica-headless'" class="w-4 h-4 animate-spin" />
                <EyeOff v-else class="w-4 h-4" />
                Headless
              </button>
              
              <button 
                @click="executarDinamica(false)"
                :disabled="loading || apiStatus === 'offline' || !multiplicador"
                class="btn-primary flex items-center gap-2 whitespace-nowrap"
              >
                <Loader2 v-if="loading && loadingMode === 'dinamica-visual'" class="w-4 h-4 animate-spin" />
                <Play v-else class="w-4 h-4" />
                Executar Visual
              </button>
            </div>
          </div>
        </div>

        <div class="text-text-tertiary text-sm">
          <p class="font-medium text-text-secondary mb-2">O que essa automação faz:</p>
          <ol class="list-decimal list-inside space-y-1">
            <li>Faz login no TaxiMachine Cloud</li>
            <li>Navega para Configurações → Tarifas dinâmicas</li>
            <li>Seleciona a aba "Manuais"</li>
            <li>Encontra a dinâmica "***Geral manual"</li>
            <li>Edita o fator multiplicador com o valor informado</li>
            <li>Salva as alterações</li>
          </ol>
        </div>
      </div>

      <!-- Ações de Login (Teste) -->
      <div class="card mb-8">
        <h2 class="card-title mb-6">Testar Login</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button 
            @click="executeLogin('headless')"
            :disabled="loading || apiStatus === 'offline'"
            class="bg-bg-tertiary border border-border-secondary rounded-lg p-6 hover:border-primary/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-left"
          >
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 rounded-lg bg-blue-400/10 flex items-center justify-center flex-shrink-0">
                <Loader2 v-if="loading && loadingMode === 'headless'" class="w-6 h-6 text-blue-400 animate-spin" />
                <EyeOff v-else class="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-text-primary mb-1">Login Headless</h3>
                <p class="text-text-tertiary text-sm">Executa em segundo plano, sem abrir navegador visível.</p>
              </div>
            </div>
          </button>

          <button 
            @click="executeLogin('visual')"
            :disabled="loading || apiStatus === 'offline'"
            class="bg-bg-tertiary border border-border-secondary rounded-lg p-6 hover:border-primary/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-left"
          >
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 rounded-lg bg-green-400/10 flex items-center justify-center flex-shrink-0">
                <Loader2 v-if="loading && loadingMode === 'visual'" class="w-6 h-6 text-green-400 animate-spin" />
                <Eye v-else class="w-6 h-6 text-green-400" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-text-primary mb-1">Login Visual</h3>
                <p class="text-text-tertiary text-sm">Abre o navegador Chrome para acompanhar.</p>
              </div>
            </div>
          </button>
        </div>

        <div v-if="apiStatus === 'offline'" class="mt-4 bg-yellow-400/10 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle class="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <p class="text-yellow-400 font-medium">API Offline</p>
            <p class="text-text-tertiary text-sm mt-1">
              Inicie o servidor Python com: <code class="bg-bg-tertiary px-2 py-0.5 rounded text-text-primary">python3 automation/main.py</code>
            </p>
          </div>
        </div>
      </div>

      <!-- Resultado -->
      <div v-if="result" class="card">
        <h2 class="card-title mb-4">Resultado da Execução</h2>
        
        <div 
          class="rounded-lg p-4 mb-4 flex items-start gap-3"
          :class="result.success ? 'bg-green-400/10' : 'bg-red-400/10'"
        >
          <CheckCircle v-if="result.success" class="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
          <XCircle v-else class="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p 
              class="font-medium"
              :class="result.success ? 'text-green-400' : 'text-red-400'"
            >
              {{ result.success ? 'Login realizado com sucesso!' : 'Falha no login' }}
            </p>
            <p class="text-text-secondary text-sm mt-1">{{ result.message }}</p>
          </div>
        </div>
        
        <div v-if="result.screenshot_path" class="bg-bg-tertiary rounded-lg p-4">
          <p class="text-text-tertiary text-sm mb-2">Screenshot salvo em:</p>
          <code class="block bg-bg-primary px-3 py-2 rounded text-text-primary text-xs break-all">
            {{ result.screenshot_path }}
          </code>
        </div>
      </div>

      <!-- Erro -->
      <div v-if="error" class="card border-red-400/50">
        <div class="flex items-start gap-3">
          <XCircle class="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p class="text-red-400 font-medium">Erro na execução</p>
            <p class="text-text-secondary text-sm mt-1">{{ error }}</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { 
  ArrowLeft, 
  RefreshCw, 
  Wifi, 
  Monitor, 
  Bot, 
  Eye, 
  EyeOff, 
  Loader2, 
  CheckCircle, 
  XCircle,
  AlertTriangle,
  Play,
  MapPin
} from 'lucide-vue-next'

const { $supabase } = useNuxtApp()
const supabase = $supabase
const { loginTest, loginVisual, healthCheck, atualizarDinamica } = useAutomation()

interface Cidade {
  id: string
  nome: string
  automation_email: string | null
  automation_password: string | null
  automation_url: string | null
  automation_ativo: boolean
}

const cidades = ref<Cidade[]>([])
const cidadeSelecionada = ref<Cidade | null>(null)
const loadingCidades = ref(true)

const apiStatus = ref<'online' | 'offline'>('offline')
const loading = ref(false)
const loadingMode = ref<'headless' | 'visual' | 'dinamica-headless' | 'dinamica-visual' | null>(null)
const checkingHealth = ref(false)
const result = ref<{ success: boolean; message: string; screenshot_path: string | null; multiplicador_aplicado?: number | null } | null>(null)
const error = ref<string | null>(null)
const multiplicador = ref<number>(1.3)

// Buscar cidades com automação configurada
async function fetchCidades() {
  loadingCidades.value = true
  try {
    const { data, error: err } = await supabase
      .from('cidades')
      .select('id, nome, automation_email, automation_password, automation_url, automation_ativo')
      .order('nome')
    
    if (err) throw err
    cidades.value = data || []
    
    // Selecionar primeira cidade com automação ativa
    const cidadeAtiva = cidades.value.find(c => c.automation_ativo && c.automation_email)
    if (cidadeAtiva) {
      cidadeSelecionada.value = cidadeAtiva
    } else if (cidades.value.length > 0) {
      cidadeSelecionada.value = cidades.value[0]
    }
  } catch (e) {
    console.error('Erro ao buscar cidades:', e)
  } finally {
    loadingCidades.value = false
  }
}

// URL da API baseada na cidade selecionada
const apiUrl = computed(() => {
  return cidadeSelecionada.value?.automation_url || 'http://localhost:8000'
})

const checkHealth = async () => {
  checkingHealth.value = true
  try {
    await healthCheck()
    apiStatus.value = 'online'
  } catch (e) {
    apiStatus.value = 'offline'
  } finally {
    checkingHealth.value = false
  }
}

const executeLogin = async (mode: 'headless' | 'visual') => {
  loading.value = true
  loadingMode.value = mode
  error.value = null
  result.value = null
  
  try {
    if (mode === 'headless') {
      result.value = await loginTest()
    } else {
      result.value = await loginVisual()
    }
  } catch (e: any) {
    error.value = e.message || 'Erro ao conectar com a API de automação. Verifique se o servidor Python está rodando.'
  } finally {
    loading.value = false
    loadingMode.value = null
  }
}

const executarDinamica = async (headless: boolean) => {
  if (!multiplicador.value) return
  if (!cidadeSelecionada.value) {
    error.value = 'Selecione uma cidade primeiro'
    return
  }
  
  loading.value = true
  loadingMode.value = headless ? 'dinamica-headless' : 'dinamica-visual'
  error.value = null
  result.value = null
  
  try {
    result.value = await atualizarDinamica({
      multiplicador: multiplicador.value,
      headless,
      email: cidadeSelecionada.value.automation_email || undefined,
      password: cidadeSelecionada.value.automation_password || undefined,
      apiUrl: apiUrl.value
    })
  } catch (e: any) {
    error.value = e.message || 'Erro ao executar automação de dinâmica. Verifique se o servidor Python está rodando.'
  } finally {
    loading.value = false
    loadingMode.value = null
  }
}

onMounted(() => {
  fetchCidades()
  checkHealth()
})
</script>
