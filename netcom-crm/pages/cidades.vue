<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { 
  MapPin,
  Plus,
  Trash2,
  RefreshCw,
  Loader2,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Settings,
  Link,
  Unlink,
  Eye,
  EyeOff,
  Copy,
  ExternalLink,
  TrendingUp,
  Activity
} from 'lucide-vue-next'
import { useAlert } from '~/composables/useAlert'

// Usar cliente Supabase do plugin (singleton)
const { $supabase } = useNuxtApp()
const supabase = $supabase
const config = useRuntimeConfig()
const alert = useAlert()

interface Cidade {
  id: string
  nome: string
  estado: string
  ativo: boolean
  taximachine_api_key: string | null
  taximachine_auth_base64: string | null
  webhook_id: string | null
  webhook_url: string | null
  webhook_ativo: boolean
  config_dinamica: ConfigDinamica | null
  created_at: string
  updated_at: string
  // Dados calculados
  total_corridas?: number
  dinamica_atual?: any
}

interface NivelDinamica {
  min: number
  max: number
  nivel: number
  multiplicador: number
  descricao: string
}

interface ConfigDinamica {
  minimo_solicitacoes_diurno: number
  minimo_solicitacoes_noturno: number
  horario_diurno_inicio: number
  horario_diurno_fim: number
  janela_analise_minutos: number
  niveis: NivelDinamica[]
}

interface WebhookInfo {
  id: string
  tipo: string
  responsavel: string
  url: string
}

// Estado
const loading = ref(true)
const refreshing = ref(false)
const cidades = ref<Cidade[]>([])
const showModal = ref(false)
const showCredentialsModal = ref(false)
const showWebhooksModal = ref(false)
const showConfigDinamicaModal = ref(false)
const selectedCidade = ref<Cidade | null>(null)
const webhooksList = ref<WebhookInfo[]>([])
const loadingWebhooks = ref(false)
const actionLoading = ref<string | null>(null)

// Configuração padrão de dinâmica (igual ao hardcode original de Curvelo)
const CONFIG_DINAMICA_PADRAO: ConfigDinamica = {
  minimo_solicitacoes_diurno: 8,
  minimo_solicitacoes_noturno: 5,
  horario_diurno_inicio: 7,
  horario_diurno_fim: 20,
  janela_analise_minutos: 15,
  niveis: [
    { min: 70, max: 100, nivel: 0, multiplicador: 1.0, descricao: 'Sem dinâmica' },
    { min: 65, max: 69, nivel: 1, multiplicador: 1.1, descricao: 'Leve aperto' },
    { min: 60, max: 64, nivel: 1, multiplicador: 1.2, descricao: 'Apertando' },
    { min: 55, max: 59, nivel: 1, multiplicador: 1.3, descricao: 'Forte' },
    { min: 50, max: 54, nivel: 1, multiplicador: 1.4, descricao: 'Crítico leve' },
    { min: 45, max: 49, nivel: 1, multiplicador: 1.5, descricao: 'Crítico' },
    { min: 40, max: 44, nivel: 2, multiplicador: 1.6, descricao: '+ crítico' },
    { min: 35, max: 39, nivel: 2, multiplicador: 1.7, descricao: '++ crítico' },
    { min: 30, max: 34, nivel: 2, multiplicador: 1.8, descricao: '+++ crítico' },
    { min: 25, max: 29, nivel: 2, multiplicador: 2.0, descricao: 'Colapso' },
    { min: 0, max: 24, nivel: 2, multiplicador: 2.5, descricao: 'Colapso extremo' }
  ]
}

// Form config dinâmica
const configDinamicaForm = ref<ConfigDinamica>({ ...CONFIG_DINAMICA_PADRAO })

// Form nova cidade
const novaCidade = ref({
  nome: '',
  estado: 'MG'
})

// Form credenciais
const credenciaisForm = ref({
  api_key: '',
  usuario: '',
  senha: ''
})
const showPassword = ref(false)

// Estados brasileiros
const estados = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
]

// Opções de estados para SearchableSelect
const estadosOptions = estados.map(uf => ({ value: uf, label: uf }))

// Buscar cidades com dados agregados
async function fetchCidades() {
  try {
    const { data, error } = await supabase
      .from('cidades')
      .select('*')
      .order('nome')

    if (error) throw error

    // Primeiro, carregar cidades sem dados agregados para mostrar rapidamente
    cidades.value = (data || []).map(cidade => ({
      ...cidade,
      total_corridas: 0,
      dinamica_atual: null
    }))
    
    loading.value = false

    // Depois, buscar dados agregados em background (sem bloquear UI)
    for (const cidade of cidades.value) {
      try {
        // Total de corridas (buscar por cidade_id OU cidade_nome para compatibilidade)
        const { count } = await supabase
          .from('taximachine_webhooks')
          .select('*', { count: 'exact', head: true })
          .or(`cidade_id.eq.${cidade.id},cidade_nome.eq.${cidade.nome}`)

        // Dinâmica atual (buscar por cidade_id OU cidade_nome)
        const { data: dinamica } = await supabase
          .from('controle_dinamica')
          .select('*')
          .or(`cidade_id.eq.${cidade.id},cidade_nome.eq.${cidade.nome}`)
          .order('created_at', { ascending: false })
          .limit(1)
          .maybeSingle()

        // Atualizar cidade específica
        const idx = cidades.value.findIndex(c => c.id === cidade.id)
        if (idx !== -1) {
          cidades.value[idx].total_corridas = count || 0
          cidades.value[idx].dinamica_atual = dinamica
        }
      } catch (e) {
        console.error(`Erro ao buscar dados da cidade ${cidade.nome}:`, e)
      }
    }
  } catch (e) {
    console.error('Erro ao buscar cidades:', e)
    loading.value = false
  }
}

// Criar nova cidade
async function criarCidade() {
  if (!novaCidade.value.nome.trim()) return

  actionLoading.value = 'criar'
  try {
    // Primeiro buscar coordenadas da cidade
    let latitude = null
    let longitude = null
    
    try {
      const geoResponse = await fetch(
        `${config.public.supabaseUrl}/functions/v1/geocode-cidade`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${config.public.supabaseKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            cidade: novaCidade.value.nome.trim(),
            estado: novaCidade.value.estado
          })
        }
      )
      const geoData = await geoResponse.json()
      if (geoData.success) {
        latitude = geoData.latitude
        longitude = geoData.longitude
      }
    } catch (geoError) {
      console.warn('Não foi possível obter coordenadas:', geoError)
    }

    // Criar cidade com coordenadas
    const { data, error } = await supabase
      .from('cidades')
      .insert({
        nome: novaCidade.value.nome.trim(),
        estado: novaCidade.value.estado,
        latitude,
        longitude
      })
      .select()
      .single()

    if (error) throw error

    cidades.value.push({ ...data, total_corridas: 0 })
    showModal.value = false
    novaCidade.value = { nome: '', estado: 'MG' }
    
    if (latitude && longitude) {
      alert.success(`Cidade ${data.nome} criada com sucesso!`)
    } else {
      alert.warning(`Cidade ${data.nome} criada, mas não foi possível obter coordenadas automaticamente.`)
    }
  } catch (e) {
    console.error('Erro ao criar cidade:', e)
    alert.error('Erro ao criar cidade')
  } finally {
    actionLoading.value = null
  }
}

// Deletar cidade
async function deletarCidade(cidade: Cidade) {
  const confirmed = await alert.confirm({
    title: 'Deletar Cidade',
    message: `Tem certeza que deseja deletar ${cidade.nome}?`,
    confirmText: 'Deletar',
    cancelText: 'Cancelar'
  })
  if (!confirmed) return

  actionLoading.value = cidade.id
  try {
    const { error } = await supabase
      .from('cidades')
      .delete()
      .eq('id', cidade.id)

    if (error) throw error

    cidades.value = cidades.value.filter(c => c.id !== cidade.id)
  } catch (e) {
    console.error('Erro ao deletar cidade:', e)
    alert.error('Erro ao deletar cidade')
  } finally {
    actionLoading.value = null
  }
}

// Toggle ativo
async function toggleAtivo(cidade: Cidade) {
  actionLoading.value = cidade.id
  try {
    const { error } = await supabase
      .from('cidades')
      .update({ ativo: !cidade.ativo, updated_at: new Date().toISOString() })
      .eq('id', cidade.id)

    if (error) throw error

    cidade.ativo = !cidade.ativo
  } catch (e) {
    console.error('Erro ao atualizar cidade:', e)
  } finally {
    actionLoading.value = null
  }
}

// Abrir modal de credenciais
function abrirCredenciais(cidade: Cidade) {
  selectedCidade.value = cidade
  credenciaisForm.value = {
    api_key: cidade.taximachine_api_key || '',
    usuario: '',
    senha: ''
  }
  showCredentialsModal.value = true
}

// Abrir modal de configuração de dinâmica
function abrirConfigDinamica(cidade: Cidade) {
  selectedCidade.value = cidade
  // Usar config da cidade ou padrão
  const config = cidade.config_dinamica || CONFIG_DINAMICA_PADRAO
  configDinamicaForm.value = JSON.parse(JSON.stringify(config))
  showConfigDinamicaModal.value = true
}

// Salvar configuração de dinâmica
async function salvarConfigDinamica() {
  if (!selectedCidade.value) return

  actionLoading.value = 'config-dinamica'
  try {
    const { error } = await supabase
      .from('cidades')
      .update({ 
        config_dinamica: configDinamicaForm.value,
        updated_at: new Date().toISOString() 
      })
      .eq('id', selectedCidade.value.id)

    if (error) throw error

    // Atualizar cidade na lista
    const idx = cidades.value.findIndex(c => c.id === selectedCidade.value!.id)
    if (idx !== -1) {
      cidades.value[idx].config_dinamica = configDinamicaForm.value
    }

    showConfigDinamicaModal.value = false
    alert.success('Configuração de dinâmica salva com sucesso!')
  } catch (e) {
    console.error('Erro ao salvar configuração:', e)
    alert.error('Erro ao salvar configuração de dinâmica')
  } finally {
    actionLoading.value = null
  }
}

// Resetar para configuração padrão
function resetarConfigPadrao() {
  configDinamicaForm.value = JSON.parse(JSON.stringify(CONFIG_DINAMICA_PADRAO))
}

// Salvar credenciais
async function salvarCredenciais() {
  if (!selectedCidade.value) return

  actionLoading.value = 'credenciais'
  try {
    let authBase64 = selectedCidade.value.taximachine_auth_base64

    // Se usuário e senha foram fornecidos, gerar novo base64
    if (credenciaisForm.value.usuario && credenciaisForm.value.senha) {
      authBase64 = btoa(`${credenciaisForm.value.usuario}:${credenciaisForm.value.senha}`)
    }

    const { error } = await supabase
      .from('cidades')
      .update({
        taximachine_api_key: credenciaisForm.value.api_key || null,
        taximachine_auth_base64: authBase64,
        updated_at: new Date().toISOString()
      })
      .eq('id', selectedCidade.value.id)

    if (error) throw error

    // Atualizar localmente
    const cidade = cidades.value.find(c => c.id === selectedCidade.value?.id)
    if (cidade) {
      cidade.taximachine_api_key = credenciaisForm.value.api_key || null
      cidade.taximachine_auth_base64 = authBase64
    }

    showCredentialsModal.value = false
  } catch (e) {
    console.error('Erro ao salvar credenciais:', e)
    alert.error('Erro ao salvar credenciais')
  } finally {
    actionLoading.value = null
  }
}

// Listar webhooks da cidade
async function listarWebhooks(cidade: Cidade) {
  selectedCidade.value = cidade
  webhooksList.value = []
  showWebhooksModal.value = true
  loadingWebhooks.value = true

  try {
    const response = await fetch(
      `${config.public.supabaseUrl}/functions/v1/taximachine-api?action=listar&cidade_id=${cidade.id}`,
      {
        headers: {
          'Authorization': `Bearer ${config.public.supabaseKey}`
        }
      }
    )

    const result = await response.json()
    
    if (result.success && result.data?.[0]?.response?.webhooks) {
      webhooksList.value = result.data[0].response.webhooks
    } else if (result.needs_credentials) {
      alert.warning('Configure as credenciais TaxiMachine primeiro')
      showWebhooksModal.value = false
      abrirCredenciais(cidade)
    }
  } catch (e) {
    console.error('Erro ao listar webhooks:', e)
  } finally {
    loadingWebhooks.value = false
  }
}

// Cadastrar webhook
async function cadastrarWebhook(cidade: Cidade) {
  actionLoading.value = `webhook-${cidade.id}`
  
  try {
    const response = await fetch(
      `${config.public.supabaseUrl}/functions/v1/taximachine-api?action=cadastrar&cidade_id=${cidade.id}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${config.public.supabaseKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      }
    )

    const result = await response.json()
    
    if (result.success) {
      alert.success(`Webhook cadastrado com sucesso!\nURL: ${result.webhook_url}`, 'Webhook Cadastrado')
      // Atualizar cidade localmente
      const c = cidades.value.find(c => c.id === cidade.id)
      if (c) {
        c.webhook_url = result.webhook_url
        c.webhook_ativo = true
      }
    } else if (result.needs_credentials) {
      alert.warning('Configure as credenciais TaxiMachine primeiro')
      abrirCredenciais(cidade)
    } else {
      alert.error(`${result.error || 'Falha ao cadastrar webhook'}`)
    }
  } catch (e) {
    console.error('Erro ao cadastrar webhook:', e)
    alert.error('Erro ao cadastrar webhook')
  } finally {
    actionLoading.value = null
  }
}

// Deletar webhook
async function deletarWebhook(webhookId: string) {
  if (!selectedCidade.value) return
  const confirmed = await alert.confirm({
    title: 'Deletar Webhook',
    message: 'Tem certeza que deseja deletar este webhook?',
    confirmText: 'Deletar',
    cancelText: 'Cancelar'
  })
  if (!confirmed) return

  loadingWebhooks.value = true
  
  try {
    const response = await fetch(
      `${config.public.supabaseUrl}/functions/v1/taximachine-api?action=deletar&cidade_id=${selectedCidade.value.id}&webhook_id=${webhookId}`,
      {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${config.public.supabaseKey}`
        }
      }
    )

    const result = await response.json()
    
    if (result.success) {
      webhooksList.value = webhooksList.value.filter(w => w.id !== webhookId)
      // Atualizar cidade
      const cidade = cidades.value.find(c => c.id === selectedCidade.value?.id)
      if (cidade) {
        cidade.webhook_ativo = false
        cidade.webhook_id = null
      }
    } else {
      alert.error(`${result.error || 'Falha ao deletar webhook'}`)
    }
  } catch (e) {
    console.error('Erro ao deletar webhook:', e)
  } finally {
    loadingWebhooks.value = false
  }
}

// Copiar URL
function copiarUrl(url: string) {
  navigator.clipboard.writeText(url)
  alert.success('URL copiada!')
}

// Refresh
async function refreshData() {
  refreshing.value = true
  await fetchCidades()
  refreshing.value = false
}

// Computed
const cidadesAtivas = computed(() => cidades.value.filter(c => c.ativo).length)
const totalCorridasGeral = computed(() => cidades.value.reduce((acc, c) => acc + (c.total_corridas || 0), 0))

onMounted(() => {
  fetchCidades()
})
</script>

<template>
  <div class="min-h-screen bg-bg-primary">
    <!-- Header -->
    <header class="bg-bg-secondary border-b border-border-secondary px-6 py-4">
      <div class="flex items-center justify-between max-w-7xl mx-auto">
        <div class="flex items-center gap-4">
          <NuxtLink to="/" class="text-xl md:text-2xl font-bold text-primary hover:opacity-80">UBIZ</NuxtLink>
          <span class="text-text-secondary text-sm md:text-base">Gerenciar Cidades</span>
        </div>

        <div class="flex items-center gap-3">
          <button 
            class="btn-secondary flex items-center gap-2"
            :disabled="refreshing"
            @click="refreshData"
          >
            <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': refreshing }" />
            <span class="hidden sm:inline">Atualizar</span>
          </button>
          <button 
            class="btn-primary flex items-center gap-2"
            @click="showModal = true"
          >
            <Plus class="w-4 h-4" />
            <span class="hidden sm:inline">Nova Cidade</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center h-96">
      <Loader2 class="w-8 h-8 text-primary animate-spin" />
    </div>

    <!-- Main Content -->
    <main v-else class="max-w-7xl mx-auto px-6 py-8">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div class="card">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <MapPin class="w-6 h-6 text-primary" />
            </div>
            <div>
              <p class="text-text-tertiary text-sm">Total de Cidades</p>
              <p class="text-2xl font-bold text-text-primary">{{ cidades.length }}</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-lg bg-green-400/10 flex items-center justify-center">
              <CheckCircle class="w-6 h-6 text-green-400" />
            </div>
            <div>
              <p class="text-text-tertiary text-sm">Cidades Ativas</p>
              <p class="text-2xl font-bold text-green-400">{{ cidadesAtivas }}</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-lg bg-blue-400/10 flex items-center justify-center">
              <Activity class="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <p class="text-text-tertiary text-sm">Total de Corridas</p>
              <p class="text-2xl font-bold text-blue-400">{{ totalCorridasGeral }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Lista de Cidades -->
      <div class="card">
        <h2 class="card-title mb-6">Cidades Cadastradas</h2>

        <div v-if="cidades.length === 0" class="text-center py-12">
          <MapPin class="w-12 h-12 text-text-tertiary mx-auto mb-4" />
          <p class="text-text-secondary">Nenhuma cidade cadastrada</p>
          <button class="btn-primary mt-4" @click="showModal = true">
            <Plus class="w-4 h-4 mr-2" />
            Adicionar Cidade
          </button>
        </div>

        <div v-else class="space-y-4">
          <div 
            v-for="cidade in cidades" 
            :key="cidade.id"
            class="bg-bg-tertiary rounded-lg p-4 border border-border-secondary hover:border-primary/50 transition-colors"
          >
            <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <!-- Info da Cidade -->
              <div class="flex items-start gap-4">
                <div 
                  class="w-12 h-12 rounded-lg flex items-center justify-center"
                  :class="cidade.ativo ? 'bg-green-400/10' : 'bg-red-400/10'"
                >
                  <MapPin 
                    class="w-6 h-6" 
                    :class="cidade.ativo ? 'text-green-400' : 'text-red-400'"
                  />
                </div>
                <div>
                  <div class="flex items-center gap-2">
                    <h3 class="text-lg font-semibold text-text-primary">{{ cidade.nome }}</h3>
                    <span class="text-text-tertiary text-sm">- {{ cidade.estado }}</span>
                    <span 
                      class="px-2 py-0.5 rounded text-xs font-medium"
                      :class="cidade.ativo ? 'bg-green-400/20 text-green-400' : 'bg-red-400/20 text-red-400'"
                    >
                      {{ cidade.ativo ? 'Ativo' : 'Inativo' }}
                    </span>
                  </div>
                  
                  <!-- Métricas -->
                  <div class="flex flex-wrap items-center gap-4 mt-2 text-sm">
                    <span class="text-text-secondary">
                      <strong class="text-text-primary">{{ cidade.total_corridas || 0 }}</strong> corridas
                    </span>
                    <span v-if="cidade.dinamica_atual" class="flex items-center gap-1">
                      <TrendingUp class="w-4 h-4" :class="cidade.dinamica_atual.multiplicador > 1 ? 'text-orange-400' : 'text-green-400'" />
                      <strong :class="cidade.dinamica_atual.multiplicador > 1 ? 'text-orange-400' : 'text-green-400'">
                        {{ cidade.dinamica_atual.multiplicador?.toFixed(1) }}x
                      </strong>
                    </span>
                    <span 
                      class="flex items-center gap-1"
                      :class="cidade.webhook_ativo ? 'text-green-400' : 'text-text-tertiary'"
                    >
                      <component :is="cidade.webhook_ativo ? Link : Unlink" class="w-4 h-4" />
                      {{ cidade.webhook_ativo ? 'Webhook ativo' : 'Sem webhook' }}
                    </span>
                  </div>

                  <!-- Credenciais Status -->
                  <div class="flex items-center gap-2 mt-2">
                    <span 
                      class="text-xs px-2 py-0.5 rounded"
                      :class="cidade.taximachine_api_key ? 'bg-green-400/20 text-green-400' : 'bg-yellow-400/20 text-yellow-400'"
                    >
                      {{ cidade.taximachine_api_key ? 'API Key ✓' : 'API Key pendente' }}
                    </span>
                    <span 
                      class="text-xs px-2 py-0.5 rounded"
                      :class="cidade.taximachine_auth_base64 ? 'bg-green-400/20 text-green-400' : 'bg-yellow-400/20 text-yellow-400'"
                    >
                      {{ cidade.taximachine_auth_base64 ? 'Auth ✓' : 'Auth pendente' }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Ações -->
              <div class="flex flex-wrap items-center gap-2">
                <NuxtLink 
                  :to="`/dinamica?cidade=${cidade.id}`"
                  class="btn-secondary text-sm flex items-center gap-1"
                >
                  <Activity class="w-4 h-4" />
                  Ver Dinâmica
                </NuxtLink>

                <button 
                  class="btn-secondary text-sm flex items-center gap-1"
                  @click="abrirCredenciais(cidade)"
                >
                  <Settings class="w-4 h-4" />
                  Credenciais
                </button>

                <button 
                  class="btn-secondary text-sm flex items-center gap-1"
                  @click="abrirConfigDinamica(cidade)"
                >
                  <TrendingUp class="w-4 h-4" />
                  Config Dinâmica
                </button>

                <button 
                  class="btn-secondary text-sm flex items-center gap-1"
                  @click="listarWebhooks(cidade)"
                  :disabled="!cidade.taximachine_api_key"
                >
                  <Link class="w-4 h-4" />
                  Webhooks
                </button>

                <button 
                  v-if="!cidade.webhook_ativo"
                  class="btn-primary text-sm flex items-center gap-1"
                  @click="cadastrarWebhook(cidade)"
                  :disabled="!cidade.taximachine_api_key || actionLoading === `webhook-${cidade.id}`"
                >
                  <Loader2 v-if="actionLoading === `webhook-${cidade.id}`" class="w-4 h-4 animate-spin" />
                  <Plus v-else class="w-4 h-4" />
                  Cadastrar Webhook
                </button>

                <button 
                  class="p-2 rounded-lg hover:bg-bg-secondary transition-colors"
                  :class="cidade.ativo ? 'text-green-400' : 'text-red-400'"
                  @click="toggleAtivo(cidade)"
                  :disabled="actionLoading === cidade.id"
                  :title="cidade.ativo ? 'Desativar' : 'Ativar'"
                >
                  <Loader2 v-if="actionLoading === cidade.id" class="w-5 h-5 animate-spin" />
                  <component v-else :is="cidade.ativo ? CheckCircle : XCircle" class="w-5 h-5" />
                </button>

                <button 
                  class="p-2 rounded-lg text-red-400 hover:bg-red-400/10 transition-colors"
                  @click="deletarCidade(cidade)"
                  :disabled="actionLoading === cidade.id"
                  title="Deletar cidade"
                >
                  <Trash2 class="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Modal Nova Cidade -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-bg-secondary rounded-xl p-6 w-full max-w-md border border-border-secondary">
        <h3 class="text-xl font-semibold text-text-primary mb-4">Nova Cidade</h3>
        
        <form @submit.prevent="criarCidade" class="space-y-4">
          <div>
            <label class="block text-text-secondary text-sm mb-2">Nome da Cidade</label>
            <input 
              v-model="novaCidade.nome"
              type="text"
              class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
              placeholder="Ex: Belo Horizonte"
              required
            />
          </div>

          <div>
            <label class="block text-text-secondary text-sm mb-2">Estado</label>
            <SearchableSelect
              v-model="novaCidade.estado"
              :options="estadosOptions"
              placeholder="Selecionar estado"
              search-placeholder="Buscar estado..."
            />
          </div>

          <div class="flex gap-3 pt-4">
            <button 
              type="button"
              class="btn-secondary flex-1"
              @click="showModal = false"
            >
              Cancelar
            </button>
            <button 
              type="submit"
              class="btn-primary flex-1 flex items-center justify-center gap-2"
              :disabled="actionLoading === 'criar'"
            >
              <Loader2 v-if="actionLoading === 'criar'" class="w-4 h-4 animate-spin" />
              Criar Cidade
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Credenciais -->
    <div v-if="showCredentialsModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-bg-secondary rounded-xl p-6 w-full max-w-md border border-border-secondary">
        <h3 class="text-xl font-semibold text-text-primary mb-2">Credenciais TaxiMachine</h3>
        <p class="text-text-tertiary text-sm mb-4">{{ selectedCidade?.nome }}</p>
        
        <form @submit.prevent="salvarCredenciais" class="space-y-4">
          <div>
            <label class="block text-text-secondary text-sm mb-2">API Key</label>
            <input 
              v-model="credenciaisForm.api_key"
              type="text"
              class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
              placeholder="Sua API Key do TaxiMachine"
            />
          </div>

          <div class="border-t border-border-secondary pt-4">
            <p class="text-text-tertiary text-xs mb-3">Preencha usuário e senha para gerar a autenticação Basic:</p>
            
            <div class="space-y-3">
              <div>
                <label class="block text-text-secondary text-sm mb-2">Usuário (email)</label>
                <input 
                  v-model="credenciaisForm.usuario"
                  type="email"
                  class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
                  placeholder="seu@email.com"
                />
              </div>

              <div>
                <label class="block text-text-secondary text-sm mb-2">Senha</label>
                <div class="relative">
                  <input 
                    v-model="credenciaisForm.senha"
                    :type="showPassword ? 'text' : 'password'"
                    class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 pr-10 text-text-primary focus:outline-none focus:border-primary"
                    placeholder="Sua senha"
                  />
                  <button 
                    type="button"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text-primary"
                    @click="showPassword = !showPassword"
                  >
                    <component :is="showPassword ? EyeOff : Eye" class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="selectedCidade?.taximachine_auth_base64" class="bg-green-400/10 rounded-lg p-3">
            <p class="text-green-400 text-sm flex items-center gap-2">
              <CheckCircle class="w-4 h-4" />
              Autenticação já configurada
            </p>
          </div>

          <div class="flex gap-3 pt-4">
            <button 
              type="button"
              class="btn-secondary flex-1"
              @click="showCredentialsModal = false"
            >
              Cancelar
            </button>
            <button 
              type="submit"
              class="btn-primary flex-1 flex items-center justify-center gap-2"
              :disabled="actionLoading === 'credenciais'"
            >
              <Loader2 v-if="actionLoading === 'credenciais'" class="w-4 h-4 animate-spin" />
              Salvar
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Webhooks -->
    <div v-if="showWebhooksModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-bg-secondary rounded-xl p-6 w-full max-w-2xl border border-border-secondary">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-xl font-semibold text-text-primary">Webhooks Cadastrados</h3>
            <p class="text-text-tertiary text-sm">{{ selectedCidade?.nome }}</p>
          </div>
          <button 
            class="text-text-tertiary hover:text-text-primary"
            @click="showWebhooksModal = false"
          >
            <XCircle class="w-6 h-6" />
          </button>
        </div>

        <div v-if="loadingWebhooks" class="flex items-center justify-center py-12">
          <Loader2 class="w-8 h-8 text-primary animate-spin" />
        </div>

        <div v-else-if="webhooksList.length === 0" class="text-center py-12">
          <Link class="w-12 h-12 text-text-tertiary mx-auto mb-4" />
          <p class="text-text-secondary">Nenhum webhook cadastrado</p>
        </div>

        <div v-else class="space-y-3 max-h-96 overflow-y-auto">
          <div 
            v-for="webhook in webhooksList" 
            :key="webhook.id"
            class="bg-bg-tertiary rounded-lg p-4 border border-border-secondary"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-2">
                  <span class="text-text-primary font-medium">ID: {{ webhook.id }}</span>
                  <span class="px-2 py-0.5 rounded text-xs bg-primary/20 text-primary">{{ webhook.tipo }}</span>
                </div>
                <p class="text-text-tertiary text-sm truncate">{{ webhook.url }}</p>
                <p class="text-text-tertiary text-xs mt-1">Responsável: {{ webhook.responsavel }}</p>
              </div>
              <div class="flex items-center gap-2">
                <button 
                  class="p-2 rounded-lg text-text-tertiary hover:text-primary hover:bg-primary/10 transition-colors"
                  @click="copiarUrl(webhook.url)"
                  title="Copiar URL"
                >
                  <Copy class="w-4 h-4" />
                </button>
                <a 
                  :href="webhook.url"
                  target="_blank"
                  class="p-2 rounded-lg text-text-tertiary hover:text-primary hover:bg-primary/10 transition-colors"
                  title="Abrir URL"
                >
                  <ExternalLink class="w-4 h-4" />
                </a>
                <button 
                  class="p-2 rounded-lg text-red-400 hover:bg-red-400/10 transition-colors"
                  @click="deletarWebhook(webhook.id)"
                  title="Deletar webhook"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6 pt-4 border-t border-border-secondary">
          <button 
            class="btn-secondary"
            @click="showWebhooksModal = false"
          >
            Fechar
          </button>
          <button 
            v-if="selectedCidade"
            class="btn-primary flex items-center gap-2"
            @click="cadastrarWebhook(selectedCidade); showWebhooksModal = false"
          >
            <Plus class="w-4 h-4" />
            Cadastrar Novo
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Configuração de Dinâmica -->
    <div v-if="showConfigDinamicaModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div class="bg-bg-secondary rounded-xl p-6 w-full max-w-4xl border border-border-secondary my-8">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-semibold text-text-primary">
            Configuração de Dinâmica - {{ selectedCidade?.nome }}
          </h3>
          <button 
            class="text-text-tertiary hover:text-text-primary transition-colors"
            @click="showConfigDinamicaModal = false"
          >
            <XCircle class="w-6 h-6" />
          </button>
        </div>

        <div class="space-y-6">
          <!-- Configurações Gerais -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label class="block text-text-secondary text-sm mb-2">Mínimo Solicitações (Diurno)</label>
              <input 
                v-model.number="configDinamicaForm.minimo_solicitacoes_diurno"
                type="number"
                min="1"
                class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label class="block text-text-secondary text-sm mb-2">Mínimo Solicitações (Noturno)</label>
              <input 
                v-model.number="configDinamicaForm.minimo_solicitacoes_noturno"
                type="number"
                min="1"
                class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label class="block text-text-secondary text-sm mb-2">Janela de Análise (minutos)</label>
              <input 
                v-model.number="configDinamicaForm.janela_analise_minutos"
                type="number"
                min="5"
                max="60"
                class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label class="block text-text-secondary text-sm mb-2">Horário Diurno Início</label>
              <input 
                v-model.number="configDinamicaForm.horario_diurno_inicio"
                type="number"
                min="0"
                max="23"
                class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label class="block text-text-secondary text-sm mb-2">Horário Diurno Fim</label>
              <input 
                v-model.number="configDinamicaForm.horario_diurno_fim"
                type="number"
                min="0"
                max="23"
                class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <!-- Tabela de Níveis -->
          <div>
            <h4 class="text-lg font-medium text-text-primary mb-4">Níveis de Dinâmica</h4>
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="border-b border-border-secondary">
                    <th class="text-left py-2 px-2 text-text-secondary">Taxa Mín (%)</th>
                    <th class="text-left py-2 px-2 text-text-secondary">Taxa Máx (%)</th>
                    <th class="text-left py-2 px-2 text-text-secondary">Nível</th>
                    <th class="text-left py-2 px-2 text-text-secondary">Multiplicador</th>
                    <th class="text-left py-2 px-2 text-text-secondary">Descrição</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(nivel, index) in configDinamicaForm.niveis" :key="index" class="border-b border-border-secondary/50">
                    <td class="py-2 px-2">
                      <input 
                        v-model.number="nivel.min"
                        type="number"
                        min="0"
                        max="100"
                        class="w-16 bg-bg-tertiary border border-border-secondary rounded px-2 py-1 text-text-primary text-center"
                      />
                    </td>
                    <td class="py-2 px-2">
                      <input 
                        v-model.number="nivel.max"
                        type="number"
                        min="0"
                        max="100"
                        class="w-16 bg-bg-tertiary border border-border-secondary rounded px-2 py-1 text-text-primary text-center"
                      />
                    </td>
                    <td class="py-2 px-2">
                      <select 
                        v-model.number="nivel.nivel"
                        class="w-20 bg-bg-tertiary border border-border-secondary rounded px-2 py-1 text-text-primary"
                      >
                        <option :value="0">0</option>
                        <option :value="1">1</option>
                        <option :value="2">2</option>
                      </select>
                    </td>
                    <td class="py-2 px-2">
                      <input 
                        v-model.number="nivel.multiplicador"
                        type="number"
                        min="1"
                        max="5"
                        step="0.1"
                        class="w-20 bg-bg-tertiary border border-border-secondary rounded px-2 py-1 text-text-primary text-center"
                      />
                    </td>
                    <td class="py-2 px-2">
                      <input 
                        v-model="nivel.descricao"
                        type="text"
                        class="w-full bg-bg-tertiary border border-border-secondary rounded px-2 py-1 text-text-primary"
                      />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="flex justify-between gap-3 mt-6 pt-4 border-t border-border-secondary">
          <button 
            class="btn-secondary"
            @click="resetarConfigPadrao"
          >
            Resetar Padrão
          </button>
          <div class="flex gap-3">
            <button 
              class="btn-secondary"
              @click="showConfigDinamicaModal = false"
            >
              Cancelar
            </button>
            <button 
              class="btn-primary flex items-center gap-2"
              @click="salvarConfigDinamica"
              :disabled="actionLoading === 'config-dinamica'"
            >
              <Loader2 v-if="actionLoading === 'config-dinamica'" class="w-4 h-4 animate-spin" />
              Salvar Configuração
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
