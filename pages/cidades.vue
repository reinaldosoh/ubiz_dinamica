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
  Activity,
  Pencil,
  Search,
  X
} from 'lucide-vue-next'
import { useAlert } from '~/composables/useAlert'
import { useTaximachineWebhook } from '~/composables/useTaximachineWebhook'

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
  taximachine_email: string | null
  taximachine_password: string | null
  webhook_id: string | null
  webhook_url: string | null
  webhook_ativo: boolean
  config_dinamica: ConfigDinamica | null
  created_at: string
  updated_at: string
  // Campos de automação
  automation_email: string | null
  automation_password: string | null
  automation_url: string | null
  automation_multiplicador_minimo: number | null
  automation_ativo: boolean
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
    { min: 30, max: 34, nivel: 2, multiplicador: 1.7, descricao: '+++ crítico' },
    { min: 25, max: 29, nivel: 2, multiplicador: 1.8, descricao: 'Colapso' },
    { min: 0, max: 24, nivel: 2, multiplicador: 1.8, descricao: 'Colapso extremo' }
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
  taximachine_email: '',
  taximachine_password: '',
  // Automação
  automation_email: '',
  automation_password: '',
  automation_url: 'https://ubiz-dinamica.onrender.com',
  automation_multiplicador_minimo: 1.1,
  automation_ativo: false
})
const showPassword = ref(false)
const showAutomationPassword = ref(false)

// Computed para gerar Base64 automaticamente
const generatedBase64 = computed(() => {
  if (credenciaisForm.value.taximachine_email && credenciaisForm.value.taximachine_password) {
    return btoa(`${credenciaisForm.value.taximachine_email}:${credenciaisForm.value.taximachine_password}`)
  }
  return selectedCidade.value?.taximachine_auth_base64 || ''
})

// Copiar Base64 para clipboard
async function copiarBase64() {
  if (generatedBase64.value) {
    await navigator.clipboard.writeText(generatedBase64.value)
    alert.success('Base64 copiado!')
  }
}

// Modal editar cidade
const showEditModal = ref(false)
const editCidadeForm = ref({
  nome: '',
  estado: 'MG'
})

// Filtro de cidades
const filtroNome = ref('')
const filtroEstado = ref('')

// Cidades filtradas
const cidadesFiltradas = computed(() => {
  return cidades.value.filter(cidade => {
    const matchNome = !filtroNome.value || 
      cidade.nome.toLowerCase().includes(filtroNome.value.toLowerCase())
    const matchEstado = !filtroEstado.value || 
      cidade.estado === filtroEstado.value
    return matchNome && matchEstado
  })
})

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

// Abrir modal de edição de cidade
function abrirEditarCidade(cidade: Cidade) {
  selectedCidade.value = cidade
  editCidadeForm.value = {
    nome: cidade.nome,
    estado: cidade.estado
  }
  showEditModal.value = true
}

// Salvar edição de cidade
async function salvarEdicaoCidade() {
  if (!selectedCidade.value || !editCidadeForm.value.nome.trim()) return

  actionLoading.value = 'editar-cidade'
  try {
    const { error } = await supabase
      .from('cidades')
      .update({
        nome: editCidadeForm.value.nome.trim(),
        estado: editCidadeForm.value.estado,
        updated_at: new Date().toISOString()
      })
      .eq('id', selectedCidade.value.id)

    if (error) throw error

    // Atualizar cidade na lista
    const idx = cidades.value.findIndex(c => c.id === selectedCidade.value!.id)
    if (idx !== -1) {
      cidades.value[idx].nome = editCidadeForm.value.nome.trim()
      cidades.value[idx].estado = editCidadeForm.value.estado
    }

    showEditModal.value = false
    alert.success('Cidade atualizada com sucesso!')
  } catch (e) {
    console.error('Erro ao atualizar cidade:', e)
    alert.error('Erro ao atualizar cidade')
  } finally {
    actionLoading.value = null
  }
}

// Abrir modal de credenciais
function abrirCredenciais(cidade: Cidade) {
  selectedCidade.value = cidade
  credenciaisForm.value = {
    api_key: cidade.taximachine_api_key || '',
    taximachine_email: cidade.taximachine_email || '',
    taximachine_password: cidade.taximachine_password || '',
    automation_email: cidade.automation_email || '',
    automation_password: cidade.automation_password || '',
    automation_url: cidade.automation_url || 'https://ubiz-dinamica.onrender.com',
    automation_multiplicador_minimo: cidade.automation_multiplicador_minimo || 1.1,
    automation_ativo: cidade.automation_ativo || false
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
    // Gerar Base64 se email e senha foram fornecidos
    if (credenciaisForm.value.taximachine_email && credenciaisForm.value.taximachine_password) {
      authBase64 = btoa(`${credenciaisForm.value.taximachine_email}:${credenciaisForm.value.taximachine_password}`)
    }

    const { error } = await supabase
      .from('cidades')
      .update({
        taximachine_api_key: credenciaisForm.value.api_key || null,
        taximachine_email: credenciaisForm.value.taximachine_email || null,
        taximachine_password: credenciaisForm.value.taximachine_password || null,
        taximachine_auth_base64: authBase64,
        // Campos de automação
        automation_email: credenciaisForm.value.automation_email || null,
        automation_password: credenciaisForm.value.automation_password || null,
        automation_url: credenciaisForm.value.automation_url || null,
        automation_multiplicador_minimo: credenciaisForm.value.automation_multiplicador_minimo || 1.1,
        automation_ativo: credenciaisForm.value.automation_ativo,
        updated_at: new Date().toISOString()
      })
      .eq('id', selectedCidade.value.id)

    if (error) throw error

    // Atualizar localmente
    const cidade = cidades.value.find(c => c.id === selectedCidade.value?.id)
    if (cidade) {
      cidade.taximachine_api_key = credenciaisForm.value.api_key || null
      cidade.taximachine_email = credenciaisForm.value.taximachine_email || null
      cidade.taximachine_password = credenciaisForm.value.taximachine_password || null
      cidade.taximachine_auth_base64 = authBase64
      cidade.automation_email = credenciaisForm.value.automation_email || null
      cidade.automation_password = credenciaisForm.value.automation_password || null
      cidade.automation_url = credenciaisForm.value.automation_url || null
      cidade.automation_multiplicador_minimo = credenciaisForm.value.automation_multiplicador_minimo
      cidade.automation_ativo = credenciaisForm.value.automation_ativo
    }

    showCredentialsModal.value = false
    alert.success('Credenciais salvas com sucesso!')
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
    // Validar credenciais
    if (!cidade.taximachine_api_key || !cidade.taximachine_auth_base64) {
      alert.warning('Configure as credenciais TaxiMachine primeiro')
      showWebhooksModal.value = false
      abrirCredenciais(cidade)
      return
    }

    const webhookManager = useTaximachineWebhook()
    const webhooks = await webhookManager.listarWebhooks(
      cidade.id,
      cidade.taximachine_api_key,
      cidade.taximachine_auth_base64
    )
    
    webhooksList.value = webhooks
  } catch (e) {
    console.error('Erro ao listar webhooks:', e)
    alert.error(`Erro ao listar webhooks: ${e}`)
  } finally {
    loadingWebhooks.value = false
  }
}

// Cadastrar webhook
async function cadastrarWebhook(cidade: Cidade) {
  actionLoading.value = `webhook-${cidade.id}`
  
  try {
    // Validar credenciais
    if (!cidade.taximachine_api_key || !cidade.taximachine_auth_base64) {
      alert.warning('Configure as credenciais TaxiMachine primeiro')
      abrirCredenciais(cidade)
      return
    }

    const webhookManager = useTaximachineWebhook()
    const webhookUrl = `${config.public.supabaseUrl}/functions/v1/webhook-cidade/${cidade.id}`

    // Usar o fluxo completo: limpar webhooks antigos e cadastrar novo
    const resultado = await webhookManager.recadastrarWebhook(
      cidade.id,
      webhookUrl,
      cidade.taximachine_api_key,
      cidade.taximachine_auth_base64
    )

    if (resultado.success) {
      let mensagem = `Webhook cadastrado com sucesso!\nURL: ${webhookUrl}`
      if (resultado.deletados > 0) {
        mensagem += `\n\n${resultado.deletados} webhook(s) antigo(s) removido(s)`
      }
      alert.success(mensagem, 'Webhook Cadastrado')
      
      // Atualizar cidade localmente
      const c = cidades.value.find(c => c.id === cidade.id)
      if (c) {
        c.webhook_url = webhookUrl
        c.webhook_ativo = true
        c.webhook_id = resultado.webhookId || null
      }

      // Atualizar no banco
      await supabase
        .from('cidades')
        .update({
          webhook_url: webhookUrl,
          webhook_ativo: true,
          webhook_id: resultado.webhookId || null,
          updated_at: new Date().toISOString()
        })
        .eq('id', cidade.id)
    } else {
      const erros = resultado.erros.join('\n')
      alert.error(`Falha ao cadastrar webhook${erros ? ':\n' + erros : ''}`)
    }
  } catch (e) {
    console.error('Erro ao cadastrar webhook:', e)
    alert.error(`Erro ao cadastrar webhook: ${e}`)
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

  // Validar credenciais
  if (!selectedCidade.value.taximachine_api_key || !selectedCidade.value.taximachine_auth_base64) {
    alert.warning('Configure as credenciais TaxiMachine primeiro')
    return
  }

  loadingWebhooks.value = true
  
  try {
    const webhookManager = useTaximachineWebhook()
    const sucesso = await webhookManager.deletarWebhook(
      webhookId,
      selectedCidade.value.taximachine_api_key,
      selectedCidade.value.taximachine_auth_base64
    )
    
    if (sucesso) {
      webhooksList.value = webhooksList.value.filter(w => w.id !== webhookId)
      alert.success('Webhook deletado com sucesso!')
      
      // Atualizar cidade
      const cidade = cidades.value.find(c => c.id === selectedCidade.value?.id)
      if (cidade) {
        // Se era o webhook de status, atualizar flags
        const webhook = webhooksList.value.find(w => w.id === webhookId)
        if (webhook?.tipo === 'status') {
          cidade.webhook_ativo = false
          cidade.webhook_id = null
          
          // Atualizar no banco
          await supabase
            .from('cidades')
            .update({
              webhook_ativo: false,
              webhook_id: null,
              updated_at: new Date().toISOString()
            })
            .eq('id', cidade.id)
        }
      }
    } else {
      alert.error('Falha ao deletar webhook')
    }
  } catch (e) {
    console.error('Erro ao deletar webhook:', e)
    alert.error(`Erro ao deletar webhook: ${e}`)
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
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <h2 class="card-title">Cidades Cadastradas</h2>
          
          <!-- Filtros -->
          <div class="flex flex-col sm:flex-row gap-2">
            <div class="relative w-full sm:w-48">
              <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary" />
              <input 
                v-model="filtroNome"
                type="text"
                placeholder="Buscar cidade..."
                class="w-full bg-bg-tertiary border border-border-secondary rounded-lg pl-9 pr-8 py-2 text-sm text-text-primary focus:outline-none focus:border-primary"
              />
              <button 
                v-if="filtroNome"
                @click="filtroNome = ''"
                class="absolute right-2 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text-primary"
              >
                <X class="w-4 h-4" />
              </button>
            </div>
            
            <div class="w-full sm:w-48">
              <SearchableSelect
                v-model="filtroEstado"
                :options="[{ value: '', label: 'Todos UFs' }, ...estadosOptions]"
                placeholder="Todos UFs"
                search-placeholder="Buscar UF..."
              />
            </div>
          </div>
        </div>

        <!-- Contador de resultados -->
        <p v-if="filtroNome || filtroEstado" class="text-text-tertiary text-sm mb-4">
          {{ cidadesFiltradas.length }} cidade(s) encontrada(s)
        </p>

        <div v-if="cidades.length === 0" class="text-center py-12">
          <MapPin class="w-12 h-12 text-text-tertiary mx-auto mb-4" />
          <p class="text-text-secondary">Nenhuma cidade cadastrada</p>
          <button class="btn-primary mt-4" @click="showModal = true">
            <Plus class="w-4 h-4 mr-2" />
            Adicionar Cidade
          </button>
        </div>

        <div v-else-if="cidadesFiltradas.length === 0" class="text-center py-12">
          <Search class="w-12 h-12 text-text-tertiary mx-auto mb-4" />
          <p class="text-text-secondary">Nenhuma cidade encontrada com os filtros aplicados</p>
          <button 
            class="btn-secondary mt-4" 
            @click="filtroNome = ''; filtroEstado = ''"
          >
            Limpar Filtros
          </button>
        </div>

        <div v-else class="space-y-4">
          <div 
            v-for="cidade in cidadesFiltradas" 
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
                  class="p-2 rounded-lg text-blue-400 hover:bg-blue-400/10 transition-colors"
                  @click="abrirEditarCidade(cidade)"
                  title="Editar cidade"
                >
                  <Pencil class="w-5 h-5" />
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

    <!-- Modal Editar Cidade -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-bg-secondary rounded-xl p-6 w-full max-w-md border border-border-secondary">
        <h3 class="text-xl font-semibold text-text-primary mb-4">Editar Cidade</h3>
        
        <form @submit.prevent="salvarEdicaoCidade" class="space-y-4">
          <div>
            <label class="block text-text-secondary text-sm mb-2">Nome da Cidade</label>
            <input 
              v-model="editCidadeForm.nome"
              type="text"
              class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
              placeholder="Ex: Belo Horizonte"
              required
            />
          </div>

          <div>
            <label class="block text-text-secondary text-sm mb-2">Estado</label>
            <SearchableSelect
              v-model="editCidadeForm.estado"
              :options="estadosOptions"
              placeholder="Selecionar estado"
              search-placeholder="Buscar estado..."
            />
          </div>

          <div class="flex gap-3 pt-4">
            <button 
              type="button"
              class="btn-secondary flex-1"
              @click="showEditModal = false"
            >
              Cancelar
            </button>
            <button 
              type="submit"
              class="btn-primary flex-1 flex items-center justify-center gap-2"
              :disabled="actionLoading === 'editar-cidade'"
            >
              <Loader2 v-if="actionLoading === 'editar-cidade'" class="w-4 h-4 animate-spin" />
              Salvar Alterações
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Credenciais -->
    <div v-if="showCredentialsModal" class="fixed inset-0 bg-black/50 flex items-start justify-center z-50 p-4 overflow-y-auto">
      <div class="bg-bg-secondary rounded-xl p-6 w-full max-w-md border border-border-secondary my-4">
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
            <p class="text-text-tertiary text-xs mb-3">Credenciais de autenticação da API TaxiMachine:</p>
            
            <div class="space-y-3">
              <div>
                <label class="block text-text-secondary text-sm mb-2">Email (usuário API)</label>
                <input 
                  v-model="credenciaisForm.taximachine_email"
                  type="email"
                  class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
                  placeholder="seu@email.com"
                />
              </div>

              <div>
                <label class="block text-text-secondary text-sm mb-2">Senha (API)</label>
                <div class="relative">
                  <input 
                    v-model="credenciaisForm.taximachine_password"
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

          <!-- Base64 gerado -->
          <div v-if="generatedBase64" class="bg-bg-tertiary rounded-lg p-3">
            <div class="flex items-center justify-between mb-2">
              <p class="text-text-secondary text-sm font-medium">Base64 (Auth Header)</p>
              <button 
                type="button"
                @click="copiarBase64"
                class="text-primary hover:text-primary/80 text-sm flex items-center gap-1"
              >
                <Copy class="w-3 h-3" />
                Copiar
              </button>
            </div>
            <code class="block bg-bg-primary px-3 py-2 rounded text-text-tertiary text-xs break-all">
              {{ generatedBase64 }}
            </code>
          </div>

          <!-- Seção Automação TaxiMachine -->
          <div class="border-t border-border-secondary pt-4 mt-4">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-text-primary font-medium">Automação TaxiMachine</h4>
              <label class="flex items-center gap-2 cursor-pointer">
                <input 
                  type="checkbox" 
                  v-model="credenciaisForm.automation_ativo"
                  class="w-4 h-4 rounded border-border-secondary bg-bg-tertiary text-primary focus:ring-primary"
                />
                <span class="text-sm text-text-secondary">Ativar automação</span>
              </label>
            </div>
            
            <p class="text-text-tertiary text-xs mb-3">
              Configure as credenciais para atualização automática da dinâmica no TaxiMachine Cloud.
            </p>
            
            <div class="space-y-3">
              <div>
                <label class="block text-text-secondary text-sm mb-2">Email (login TaxiMachine)</label>
                <input 
                  v-model="credenciaisForm.automation_email"
                  type="email"
                  class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
                  placeholder="email@taximachine.com"
                />
              </div>

              <div>
                <label class="block text-text-secondary text-sm mb-2">Senha (login TaxiMachine)</label>
                <div class="relative">
                  <input 
                    v-model="credenciaisForm.automation_password"
                    :type="showAutomationPassword ? 'text' : 'password'"
                    class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 pr-10 text-text-primary focus:outline-none focus:border-primary"
                    placeholder="Senha do TaxiMachine"
                  />
                  <button 
                    type="button"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text-primary"
                    @click="showAutomationPassword = !showAutomationPassword"
                  >
                    <component :is="showAutomationPassword ? EyeOff : Eye" class="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div>
                <label class="block text-text-secondary text-sm mb-2">Multiplicador Mínimo</label>
                <input 
                  :value="credenciaisForm.automation_multiplicador_minimo"
                  @input="(e: Event) => { 
                    const val = (e.target as HTMLInputElement).value.replace(',', '.');
                    const num = parseFloat(val);
                    if (!isNaN(num)) credenciaisForm.automation_multiplicador_minimo = num;
                  }"
                  type="text"
                  inputmode="decimal"
                  pattern="[0-9]*[.,]?[0-9]*"
                  class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
                  placeholder="1.1"
                />
                <p class="text-text-tertiary text-xs mt-1">Valor mínimo aceito pelo TaxiMachine (ex: 1.1)</p>
              </div>

              <div>
                <label class="block text-text-secondary text-sm mb-2">URL da API de Automação</label>
                <input 
                  v-model="credenciaisForm.automation_url"
                  type="url"
                  class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
                  placeholder="https://ubiz-dinamica.onrender.com"
                />
              </div>
            </div>

            <div v-if="credenciaisForm.automation_ativo && credenciaisForm.automation_email" class="bg-green-400/10 rounded-lg p-3 mt-3">
              <p class="text-green-400 text-sm flex items-center gap-2">
                <CheckCircle class="w-4 h-4" />
                Automação configurada para {{ credenciaisForm.automation_email }}
              </p>
            </div>
          </div>

          <div class="flex gap-3 pt-4 sticky bottom-0 bg-bg-secondary pb-2">
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
