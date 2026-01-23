<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { 
  Webhook,
  Plus,
  Trash2,
  RefreshCw,
  Loader2,
  CheckCircle,
  XCircle,
  Settings,
  Link,
  Eye,
  EyeOff,
  Copy,
  ExternalLink,
  Activity,
  Pencil,
  Search,
  X,
  Send,
  Clock,
  AlertTriangle,
  Filter
} from 'lucide-vue-next'
import { useAlert } from '~/composables/useAlert'

const { $supabase } = useNuxtApp()
const supabase = $supabase
const config = useRuntimeConfig()
const alert = useAlert()

interface Cidade {
  id: string
  nome: string
}

interface WebhookDestination {
  id: string
  cidade_id: string | null
  cidade_ids: string[]
  nome: string
  url: string
  headers: Record<string, string>
  ativo: boolean
  eventos_filtro: string[]
  retry_count: number
  timeout_ms: number
  created_at: string
  updated_at: string
  cidades?: Cidade
}

interface DeliveryLog {
  id: string
  destination_id: string
  webhook_id: string
  cidade_id: string
  url: string
  method: string
  request_headers: Record<string, string>
  request_body: any
  response_status: number | null
  response_body: string | null
  success: boolean
  error_message: string | null
  attempt_number: number
  duration_ms: number | null
  created_at: string
  webhook_destinations?: { nome: string; url: string }
  cidades?: { nome: string }
}

// Estado
const loading = ref(true)
const refreshing = ref(false)
const destinations = ref<WebhookDestination[]>([])
const logs = ref<DeliveryLog[]>([])
const cidades = ref<Cidade[]>([])
const showModal = ref(false)
const showLogsModal = ref(false)
const selectedDestination = ref<WebhookDestination | null>(null)
const actionLoading = ref<string | null>(null)
const activeTab = ref<'destinations' | 'logs'>('destinations')

// Filtros de logs
const logFilters = ref({
  destination_id: '',
  cidade_id: '',
  success: '',
  limit: 50
})

// Form
const form = ref({
  id: '',
  nome: '',
  url: '',
  cidade_ids: [] as string[],
  headers: '{}',
  ativo: true,
  eventos_filtro: ['P', 'F', 'C', 'N', 'S', 'A'],
  retry_count: 3,
  timeout_ms: 5000
})

const eventosDisponiveis = [
  { code: 'P', label: 'Pending (Pendente)' },
  { code: 'F', label: 'Finished/Failed' },
  { code: 'C', label: 'Cancelled (Cancelada)' },
  { code: 'N', label: 'No driver (Sem motorista)' },
  { code: 'S', label: 'Success (Sucesso)' },
  { code: 'A', label: 'Accepted (Aceita)' }
]

// Options para SearchableSelect
const cidadesOptions = computed(() => {
  return cidades.value.map(c => ({ value: c.id, label: c.nome }))
})

// Toggle cidade no array
function toggleCidade(cidadeId: string) {
  const idx = form.value.cidade_ids.indexOf(cidadeId)
  if (idx >= 0) {
    form.value.cidade_ids.splice(idx, 1)
  } else {
    form.value.cidade_ids.push(cidadeId)
  }
}

// Obter nomes das cidades selecionadas
function getCidadesNomes(cidadeIds: string[]): string {
  if (!cidadeIds || cidadeIds.length === 0) return 'Global'
  return cidadeIds
    .map(id => cidades.value.find(c => c.id === id)?.nome)
    .filter(Boolean)
    .join(', ')
}

const destinationsOptions = computed(() => {
  return [
    { value: '', label: 'Todos destinos' },
    ...destinations.value.map(d => ({ value: d.id, label: d.nome }))
  ]
})

// Stats
const stats = computed(() => {
  const total = logs.value.length
  const success = logs.value.filter(l => l.success).length
  const failed = total - success
  const rate = total > 0 ? ((success / total) * 100).toFixed(1) : '0'
  return { total, success, failed, rate }
})

// Carregar dados
async function loadData() {
  loading.value = true
  try {
    const [destResult, cidadesResult] = await Promise.all([
      supabase
        .from('webhook_destinations')
        .select('*, cidades(id, nome)')
        .order('created_at', { ascending: false }),
      supabase
        .from('cidades')
        .select('id, nome')
        .eq('ativo', true)
        .order('nome')
    ])

    if (destResult.data) destinations.value = destResult.data
    if (cidadesResult.data) cidades.value = cidadesResult.data

    await loadLogs()
  } catch (err) {
    console.error('Erro ao carregar dados:', err)
    alert.error('Erro ao carregar dados')
  } finally {
    loading.value = false
  }
}

async function loadLogs() {
  try {
    let query = supabase
      .from('webhook_delivery_logs')
      .select('*, webhook_destinations(nome, url), cidades(nome)')
      .order('created_at', { ascending: false })
      .limit(logFilters.value.limit)

    if (logFilters.value.destination_id) {
      query = query.eq('destination_id', logFilters.value.destination_id)
    }
    if (logFilters.value.cidade_id) {
      query = query.eq('cidade_id', logFilters.value.cidade_id)
    }
    if (logFilters.value.success !== '') {
      query = query.eq('success', logFilters.value.success === 'true')
    }

    const { data } = await query
    if (data) logs.value = data
  } catch (err) {
    console.error('Erro ao carregar logs:', err)
  }
}

async function refresh() {
  refreshing.value = true
  await loadData()
  refreshing.value = false
}

// Modal
function openModal(dest?: WebhookDestination) {
  if (dest) {
    selectedDestination.value = dest
    form.value = {
      id: dest.id,
      nome: dest.nome,
      url: dest.url,
      cidade_ids: dest.cidade_ids || (dest.cidade_id ? [dest.cidade_id] : []),
      headers: JSON.stringify(dest.headers || {}, null, 2),
      ativo: dest.ativo,
      eventos_filtro: dest.eventos_filtro || ['P', 'F', 'C', 'N', 'S', 'A'],
      retry_count: dest.retry_count || 3,
      timeout_ms: dest.timeout_ms || 5000
    }
  } else {
    selectedDestination.value = null
    form.value = {
      id: '',
      nome: '',
      url: '',
      cidade_ids: [],
      headers: '{}',
      ativo: true,
      eventos_filtro: ['P', 'F', 'C', 'N', 'S', 'A'],
      retry_count: 3,
      timeout_ms: 5000
    }
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedDestination.value = null
}

// Salvar
async function saveDestination() {
  if (!form.value.nome || !form.value.url) {
    alert.error('Nome e URL são obrigatórios')
    return
  }

  let headers = {}
  try {
    headers = JSON.parse(form.value.headers)
  } catch {
    alert.error('Headers inválidos (deve ser JSON válido)')
    return
  }

  actionLoading.value = 'save'
  try {
    const data = {
      nome: form.value.nome,
      url: form.value.url,
      cidade_ids: form.value.cidade_ids.length > 0 ? form.value.cidade_ids : [],
      headers,
      ativo: form.value.ativo,
      eventos_filtro: form.value.eventos_filtro,
      retry_count: form.value.retry_count,
      timeout_ms: form.value.timeout_ms
    }

    if (form.value.id) {
      const { error } = await supabase
        .from('webhook_destinations')
        .update({ ...data, updated_at: new Date().toISOString() })
        .eq('id', form.value.id)

      if (error) throw error
      alert.success('Destino atualizado com sucesso')
    } else {
      const { error } = await supabase
        .from('webhook_destinations')
        .insert(data)

      if (error) throw error
      alert.success('Destino criado com sucesso')
    }

    closeModal()
    await loadData()
  } catch (err: any) {
    alert.error(err.message || 'Erro ao salvar')
  } finally {
    actionLoading.value = null
  }
}

// Deletar
async function deleteDestination(dest: WebhookDestination) {
  const confirmed = await alert.confirm({
    title: 'Excluir Destino',
    message: `Tem certeza que deseja excluir "${dest.nome}"? Os logs de envio serão mantidos.`
  })

  if (!confirmed) return

  actionLoading.value = dest.id
  try {
    const { error } = await supabase
      .from('webhook_destinations')
      .delete()
      .eq('id', dest.id)

    if (error) throw error
    alert.success('Destino excluído')
    await loadData()
  } catch (err: any) {
    alert.error(err.message || 'Erro ao excluir')
  } finally {
    actionLoading.value = null
  }
}

// Toggle ativo
async function toggleAtivo(dest: WebhookDestination) {
  actionLoading.value = dest.id
  try {
    const { error } = await supabase
      .from('webhook_destinations')
      .update({ ativo: !dest.ativo, updated_at: new Date().toISOString() })
      .eq('id', dest.id)

    if (error) throw error
    dest.ativo = !dest.ativo
  } catch (err: any) {
    alert.error(err.message || 'Erro ao atualizar')
  } finally {
    actionLoading.value = null
  }
}

// Copiar URL
function copyUrl(url: string) {
  navigator.clipboard.writeText(url)
  alert.success('URL copiada!')
}

// Ver logs de um destino
function viewLogs(dest: WebhookDestination) {
  logFilters.value.destination_id = dest.id
  activeTab.value = 'logs'
  loadLogs()
}

// Formatar data
function formatDate(date: string) {
  return new Date(date).toLocaleString('pt-BR')
}

// Toggle evento
function toggleEvento(code: string) {
  const idx = form.value.eventos_filtro.indexOf(code)
  if (idx >= 0) {
    form.value.eventos_filtro.splice(idx, 1)
  } else {
    form.value.eventos_filtro.push(code)
  }
}

onMounted(loadData)
</script>

<template>
  <div class="min-h-screen bg-bg-primary text-text-primary p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <Webhook class="w-8 h-8 text-primary" />
        <div>
          <h1 class="text-2xl font-bold">Webhooks</h1>
          <p class="text-text-secondary text-sm">Gerencie destinos de webhooks por cidade</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="refresh"
          :disabled="refreshing"
          class="flex items-center gap-2 px-4 py-2 bg-bg-secondary hover:bg-bg-tertiary rounded-lg transition-colors border border-border-secondary"
        >
          <RefreshCw :class="['w-4 h-4', refreshing && 'animate-spin']" />
          Atualizar
        </button>
        <button
          @click="openModal()"
          class="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-dark rounded-lg transition-colors"
        >
          <Plus class="w-4 h-4" />
          Novo Destino
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-4 gap-4 mb-6">
      <div class="bg-bg-secondary rounded-xl p-4 border border-border-secondary">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-primary/20 rounded-lg">
            <Link class="w-5 h-5 text-primary" />
          </div>
          <div>
            <p class="text-text-secondary text-sm">Destinos</p>
            <p class="text-2xl font-bold">{{ destinations.length }}</p>
          </div>
        </div>
      </div>
      <div class="bg-bg-secondary rounded-xl p-4 border border-border-secondary">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-blue-500/20 rounded-lg">
            <Send class="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <p class="text-text-secondary text-sm">Envios</p>
            <p class="text-2xl font-bold">{{ stats.total }}</p>
          </div>
        </div>
      </div>
      <div class="bg-bg-secondary rounded-xl p-4 border border-border-secondary">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-green-500/20 rounded-lg">
            <CheckCircle class="w-5 h-5 text-green-400" />
          </div>
          <div>
            <p class="text-text-secondary text-sm">Sucesso</p>
            <p class="text-2xl font-bold">{{ stats.success }}</p>
          </div>
        </div>
      </div>
      <div class="bg-bg-secondary rounded-xl p-4 border border-border-secondary">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-yellow-500/20 rounded-lg">
            <Activity class="w-5 h-5 text-yellow-400" />
          </div>
          <div>
            <p class="text-text-secondary text-sm">Taxa Sucesso</p>
            <p class="text-2xl font-bold">{{ stats.rate }}%</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-2 mb-6">
      <button
        @click="activeTab = 'destinations'"
        :class="[
          'px-4 py-2 rounded-lg transition-colors',
          activeTab === 'destinations' ? 'bg-primary text-white' : 'bg-bg-secondary text-text-secondary hover:bg-bg-tertiary border border-border-secondary'
        ]"
      >
        <Link class="w-4 h-4 inline mr-2" />
        Destinos
      </button>
      <button
        @click="activeTab = 'logs'; loadLogs()"
        :class="[
          'px-4 py-2 rounded-lg transition-colors',
          activeTab === 'logs' ? 'bg-primary text-white' : 'bg-bg-secondary text-text-secondary hover:bg-bg-tertiary border border-border-secondary'
        ]"
      >
        <Activity class="w-4 h-4 inline mr-2" />
        Logs de Envio
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 animate-spin text-primary" />
    </div>

    <!-- Destinos -->
    <div v-else-if="activeTab === 'destinations'" class="space-y-4">
      <div v-if="destinations.length === 0" class="text-center py-20 text-text-tertiary">
        <Webhook class="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>Nenhum destino de webhook cadastrado</p>
        <button @click="openModal()" class="mt-4 text-primary hover:text-primary-light">
          Criar primeiro destino
        </button>
      </div>

      <div
        v-for="dest in destinations"
        :key="dest.id"
        class="bg-bg-secondary rounded-xl p-4 border border-border-secondary hover:border-border-primary transition-colors"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold">{{ dest.nome }}</h3>
              <span
                :class="[
                  'px-2 py-0.5 rounded text-xs font-medium',
                  dest.ativo ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                ]"
              >
                {{ dest.ativo ? 'Ativo' : 'Inativo' }}
              </span>
              <template v-if="dest.cidade_ids && dest.cidade_ids.length > 0">
                <span 
                  v-for="cidId in dest.cidade_ids.slice(0, 3)" 
                  :key="cidId"
                  class="px-2 py-0.5 rounded text-xs bg-blue-500/20 text-blue-400"
                >
                  {{ cidades.find(c => c.id === cidId)?.nome || 'Cidade' }}
                </span>
                <span v-if="dest.cidade_ids.length > 3" class="px-2 py-0.5 rounded text-xs bg-blue-500/20 text-blue-400">
                  +{{ dest.cidade_ids.length - 3 }}
                </span>
              </template>
              <span v-else-if="dest.cidades" class="px-2 py-0.5 rounded text-xs bg-blue-500/20 text-blue-400">
                {{ dest.cidades.nome }}
              </span>
              <span v-else class="px-2 py-0.5 rounded text-xs bg-bg-tertiary text-text-tertiary">
                Global
              </span>
            </div>

            <div class="flex items-center gap-2 text-text-secondary text-sm mb-3">
              <code class="bg-bg-tertiary px-2 py-1 rounded text-xs">{{ dest.url }}</code>
              <button @click="copyUrl(dest.url)" class="hover:text-white">
                <Copy class="w-4 h-4" />
              </button>
            </div>

            <div class="flex flex-wrap gap-1 mb-2">
              <span
                v-for="evt in dest.eventos_filtro"
                :key="evt"
                class="px-2 py-0.5 rounded text-xs bg-primary/20 text-primary"
              >
                {{ evt }}
              </span>
            </div>

            <div class="text-xs text-text-tertiary">
              Retry: {{ dest.retry_count }}x | Timeout: {{ dest.timeout_ms }}ms | Criado: {{ formatDate(dest.created_at) }}
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button
              @click="viewLogs(dest)"
              class="p-2 hover:bg-bg-tertiary rounded-lg transition-colors"
              title="Ver logs"
            >
              <Activity class="w-4 h-4 text-blue-400" />
            </button>
            <button
              @click="toggleAtivo(dest)"
              :disabled="actionLoading === dest.id"
              class="p-2 hover:bg-bg-tertiary rounded-lg transition-colors"
              :title="dest.ativo ? 'Desativar' : 'Ativar'"
            >
              <Eye v-if="dest.ativo" class="w-4 h-4 text-green-400" />
              <EyeOff v-else class="w-4 h-4 text-text-tertiary" />
            </button>
            <button
              @click="openModal(dest)"
              class="p-2 hover:bg-bg-tertiary rounded-lg transition-colors"
              title="Editar"
            >
              <Pencil class="w-4 h-4 text-yellow-400" />
            </button>
            <button
              @click="deleteDestination(dest)"
              :disabled="actionLoading === dest.id"
              class="p-2 hover:bg-bg-tertiary rounded-lg transition-colors"
              title="Excluir"
            >
              <Trash2 class="w-4 h-4 text-red-400" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Logs -->
    <div v-else-if="activeTab === 'logs'" class="space-y-4">
      <!-- Filtros -->
      <div class="bg-bg-secondary rounded-xl p-4 border border-border-secondary">
        <div class="flex items-center gap-4 flex-wrap">
          <div class="flex items-center gap-2">
            <Filter class="w-4 h-4 text-text-tertiary" />
            <span class="text-sm text-text-secondary">Filtros:</span>
          </div>
          <div class="w-48">
            <SearchableSelect
              v-model="logFilters.destination_id"
              :options="destinationsOptions"
              placeholder="Todos destinos"
              search-placeholder="Buscar destino..."
              clearable
              @update:model-value="loadLogs()"
            />
          </div>
          <div class="w-48">
            <SearchableSelect
              v-model="logFilters.cidade_id"
              :options="cidadesOptions"
              placeholder="Todas cidades"
              search-placeholder="Buscar cidade..."
              clearable
              @update:model-value="loadLogs()"
            />
          </div>
          <select
            v-model="logFilters.success"
            @change="loadLogs()"
            class="bg-bg-tertiary border border-border-secondary rounded-lg px-3 py-1.5 text-sm text-text-primary"
          >
            <option value="">Todos status</option>
            <option value="true">Sucesso</option>
            <option value="false">Falha</option>
          </select>
          <button
            @click="logFilters = { destination_id: '', cidade_id: '', success: '', limit: 50 }; loadLogs()"
            class="text-sm text-primary hover:text-primary-light"
          >
            Limpar filtros
          </button>
        </div>
      </div>

      <div v-if="logs.length === 0" class="text-center py-20 text-text-tertiary">
        <Activity class="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>Nenhum log de envio encontrado</p>
      </div>

      <div class="space-y-2">
        <div
          v-for="log in logs"
          :key="log.id"
          :class="[
            'bg-bg-secondary rounded-lg p-3 border transition-colors',
            log.success ? 'border-status-success/30' : 'border-status-error/30'
          ]"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <CheckCircle v-if="log.success" class="w-5 h-5 text-green-400" />
              <XCircle v-else class="w-5 h-5 text-red-400" />
              <div>
                <div class="flex items-center gap-2">
                  <span class="font-medium">{{ log.webhook_destinations?.nome || 'Destino removido' }}</span>
                  <span v-if="log.cidades" class="text-xs text-text-tertiary">{{ log.cidades.nome }}</span>
                </div>
                <code class="text-xs text-text-tertiary">{{ log.url }}</code>
              </div>
            </div>
            <div class="text-right text-sm">
              <div class="flex items-center gap-2">
                <span v-if="log.response_status" :class="log.success ? 'text-green-400' : 'text-red-400'">
                  HTTP {{ log.response_status }}
                </span>
                <span v-if="log.duration_ms" class="text-text-secondary">
                  {{ log.duration_ms }}ms
                </span>
                <span class="text-text-tertiary">
                  #{{ log.attempt_number }}
                </span>
              </div>
              <div class="text-xs text-text-tertiary">{{ formatDate(log.created_at) }}</div>
            </div>
          </div>
          <div v-if="log.error_message" class="mt-2 text-xs text-red-400 bg-red-500/10 px-2 py-1 rounded">
            {{ log.error_message }}
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <Teleport to="body">
      <div
        v-if="showModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="closeModal"
      >
        <div class="bg-bg-secondary rounded-xl w-full max-w-lg border border-border-secondary flex flex-col" style="max-height: calc(100vh - 2rem);">
          <div class="p-6 border-b border-border-secondary">
            <div class="flex items-center justify-between">
              <h2 class="text-xl font-bold">
                {{ form.id ? 'Editar Destino' : 'Novo Destino' }}
              </h2>
              <button @click="closeModal" class="p-2 hover:bg-bg-tertiary rounded-lg">
                <X class="w-5 h-5" />
              </button>
            </div>
          </div>

          <div class="p-6 space-y-4 overflow-y-auto flex-1">
            <div>
              <label class="block text-text-secondary text-sm mb-2">Nome *</label>
              <input
                v-model="form.nome"
                type="text"
                placeholder="Ex: Meu Sistema"
                class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label class="block text-text-secondary text-sm mb-2">URL *</label>
              <input
                v-model="form.url"
                type="url"
                placeholder="https://exemplo.com/webhook"
                class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label class="block text-text-secondary text-sm mb-2">Cidades (deixe vazio para global)</label>
              <div class="bg-bg-tertiary border border-border-secondary rounded-lg p-3 max-h-48 overflow-y-auto">
                <div v-if="cidades.length === 0" class="text-text-tertiary text-sm">
                  Nenhuma cidade cadastrada
                </div>
                <div v-else class="space-y-2">
                  <label 
                    v-for="cidade in cidades" 
                    :key="cidade.id"
                    class="flex items-center gap-2 cursor-pointer hover:bg-bg-secondary p-1 rounded transition-colors"
                  >
                    <input
                      type="checkbox"
                      :checked="form.cidade_ids.includes(cidade.id)"
                      @change="toggleCidade(cidade.id)"
                      class="w-4 h-4 rounded border-border-secondary bg-bg-primary text-primary focus:ring-primary"
                    />
                    <span class="text-text-primary text-sm">{{ cidade.nome }}</span>
                  </label>
                </div>
              </div>
              <p class="text-xs text-text-tertiary mt-1">
                {{ form.cidade_ids.length === 0 ? 'Global (todas as cidades)' : `${form.cidade_ids.length} cidade(s) selecionada(s)` }}
              </p>
            </div>

            <div>
              <label class="block text-text-secondary text-sm mb-2">Eventos</label>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="evt in eventosDisponiveis"
                  :key="evt.code"
                  @click="toggleEvento(evt.code)"
                  :class="[
                    'px-3 py-1.5 rounded-lg text-sm transition-colors',
                    form.eventos_filtro.includes(evt.code)
                      ? 'bg-primary text-white'
                      : 'bg-bg-tertiary text-text-secondary hover:bg-bg-secondary border border-border-secondary'
                  ]"
                >
                  {{ evt.code }}
                </button>
              </div>
              <p class="text-xs text-text-tertiary mt-1">Selecione quais eventos disparam o envio</p>
            </div>

            <div>
              <label class="block text-text-secondary text-sm mb-2">Headers (JSON)</label>
              <textarea
                v-model="form.headers"
                rows="3"
                placeholder='{"Authorization": "Bearer token"}'
                class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary font-mono text-sm"
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-text-secondary text-sm mb-2">Retry</label>
                <input
                  v-model.number="form.retry_count"
                  type="number"
                  min="1"
                  max="10"
                  class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label class="block text-text-secondary text-sm mb-2">Timeout (ms)</label>
                <input
                  v-model.number="form.timeout_ms"
                  type="number"
                  min="1000"
                  max="30000"
                  step="1000"
                  class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <div class="flex items-center gap-3">
              <input
                v-model="form.ativo"
                type="checkbox"
                id="ativo"
                class="w-4 h-4 rounded border-border-secondary bg-bg-tertiary text-primary focus:ring-primary"
              />
              <label for="ativo" class="text-sm text-text-secondary">Ativo</label>
            </div>
          </div>

          <div class="p-6 border-t border-border-secondary flex justify-end gap-3">
            <button
              @click="closeModal"
              class="px-4 py-2 bg-bg-tertiary hover:bg-bg-primary rounded-lg transition-colors border border-border-secondary"
            >
              Cancelar
            </button>
            <button
              @click="saveDestination"
              :disabled="actionLoading === 'save'"
              class="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-dark rounded-lg transition-colors disabled:opacity-50"
            >
              <Loader2 v-if="actionLoading === 'save'" class="w-4 h-4 animate-spin" />
              Salvar
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
