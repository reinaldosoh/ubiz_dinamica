<script setup lang="ts">
import { 
  Car,
  TrendingUp,
  TrendingDown,
  Activity,
  Clock,
  MapPin,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Loader2,
  Sun,
  Moon,
  ChevronDown
} from 'lucide-vue-next'

// Usar cliente Supabase do plugin (singleton)
const { $supabase } = useNuxtApp()
const supabase = $supabase
const route = useRoute()

// Cidades
interface Cidade {
  id: string
  nome: string
  estado: string
  latitude: number | null
  longitude: number | null
}
const cidades = ref<Cidade[]>([])
const cidadeSelecionada = ref<Cidade | null>(null)

// Estado reativo
const loading = ref(true)
const refreshing = ref(false)
const corridasStats = ref<Record<string, number>>({})
const dinamicaAtual = ref<any>(null)
const ultimaAtualizacao = ref<Date | null>(null)

// Configuração dos status
const statusConfig: Record<string, { label: string; color: string; bgColor: string; barColor: string; icon: any }> = {
  'P': { label: 'Pendente', color: 'text-yellow-400', bgColor: 'bg-yellow-400/10', barColor: '#facc15', icon: Clock },
  'F': { label: 'Finalizada', color: 'text-green-400', bgColor: 'bg-green-400/10', barColor: '#4ade80', icon: CheckCircle },
  'C': { label: 'Cancelada', color: 'text-red-400', bgColor: 'bg-red-400/10', barColor: '#f87171', icon: XCircle },
  'N': { label: 'Não Atendida', color: 'text-orange-400', bgColor: 'bg-orange-400/10', barColor: '#fb923c', icon: AlertTriangle },
  'S': { label: 'Em Espera', color: 'text-blue-400', bgColor: 'bg-blue-400/10', barColor: '#60a5fa', icon: Loader2 },
  'A': { label: 'Aceita', color: 'text-emerald-400', bgColor: 'bg-emerald-400/10', barColor: '#34d399', icon: CheckCircle },
}

// Histórico de dinâmica
const historicoDinamica = ref<any[]>([])

// Buscar cidades
async function fetchCidades() {
  const { data, error } = await supabase
    .from('cidades')
    .select('id, nome, estado, latitude, longitude')
    .eq('ativo', true)
    .order('nome')

  if (error) {
    console.error('Erro ao buscar cidades:', error)
    return
  }

  cidades.value = data || []

  // Se tem cidade na query, selecionar
  const cidadeIdQuery = route.query.cidade as string
  if (cidadeIdQuery) {
    const cidade = cidades.value.find(c => c.id === cidadeIdQuery)
    if (cidade) cidadeSelecionada.value = cidade
  }

  // Se não tem cidade selecionada, pegar a primeira
  if (!cidadeSelecionada.value && cidades.value.length > 0) {
    cidadeSelecionada.value = cidades.value[0]
  }
}

// Função para buscar estatísticas de corridas únicas (últimos 15 minutos)
async function fetchCorridasStats() {
  // Buscar apenas corridas dos últimos 15 minutos
  const quinzeMinutosAtras = new Date(Date.now() - 15 * 60 * 1000).toISOString()
  
  // Buscar por cidade_nome (todos os webhooks de Curvelo têm cidade_nome preenchido)
  const cidadeNome = cidadeSelecionada.value?.nome || 'Curvelo'
  
  const { data, error } = await supabase
    .from('taximachine_webhooks')
    .select('request_id, status_code')
    .gte('event_datetime', quinzeMinutosAtras)
    .eq('cidade_nome', cidadeNome)
    .order('event_datetime', { ascending: false })

  if (error) {
    console.error('Erro ao buscar corridas:', error)
    return
  }

  // Agrupar por request_id e pegar o status mais recente
  const corridasUnicas = new Map<number, string>()
  for (const corrida of data || []) {
    if (!corridasUnicas.has(corrida.request_id)) {
      corridasUnicas.set(corrida.request_id, corrida.status_code)
    }
  }

  // Contar por status
  const stats: Record<string, number> = { P: 0, F: 0, C: 0, N: 0, S: 0, A: 0 }
  for (const status of corridasUnicas.values()) {
    if (stats[status] !== undefined) {
      stats[status]++
    }
  }

  corridasStats.value = stats
}

// Função para buscar dinâmica atual
async function fetchDinamicaAtual() {
  // Buscar o último registro de dinâmica (por enquanto sem filtro de cidade pois os dados antigos não têm cidade_id)
  const { data, error } = await supabase
    .from('controle_dinamica')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(1)
    .maybeSingle()

  if (error && error.code !== 'PGRST116') {
    console.error('Erro ao buscar dinâmica:', error)
    return
  }

  dinamicaAtual.value = data
}

// Função para buscar histórico de dinâmica
async function fetchHistoricoDinamica() {
  const cidadeNome = cidadeSelecionada.value?.nome || 'Curvelo'
  
  const { data, error } = await supabase
    .from('historico_dinamica')
    .select('*')
    .eq('cidade_nome', cidadeNome)
    .order('data_hora', { ascending: false })
    .limit(20)

  if (error) {
    console.error('Erro ao buscar histórico:', error)
    return
  }

  historicoDinamica.value = data || []
}

// Função para atualizar dados
async function refreshData() {
  refreshing.value = true
  await Promise.all([fetchCorridasStats(), fetchDinamicaAtual(), fetchHistoricoDinamica()])
  ultimaAtualizacao.value = new Date()
  refreshing.value = false
}

// Selecionar cidade
function selecionarCidade(cidade: Cidade) {
  cidadeSelecionada.value = cidade
  showCidadeDropdown.value = false
  refreshData()
}

// Carregar dados iniciais - SEM auto-refresh para evitar vazamento
onMounted(async () => {
  await fetchCidades()
  await refreshData()
  loading.value = false
})

// Computed
const totalCorridas = computed(() => {
  return Object.values(corridasStats.value).reduce((a, b) => a + b, 0)
})

const corridasSucesso = computed(() => {
  return (corridasStats.value['F'] || 0) + (corridasStats.value['A'] || 0)
})

const taxaSucesso = computed(() => {
  if (totalCorridas.value === 0) return 0
  return ((corridasSucesso.value / totalCorridas.value) * 100).toFixed(1)
})

const multiplicadorClass = computed(() => {
  if (!dinamicaAtual.value) return 'text-green-400'
  const mult = dinamicaAtual.value.multiplicador
  if (mult <= 1.0) return 'text-green-400'
  if (mult <= 1.3) return 'text-yellow-400'
  if (mult <= 1.5) return 'text-orange-400'
  return 'text-red-400'
})

const nivelLabel = computed(() => {
  if (!dinamicaAtual.value) return 'Sem dinâmica'
  const nivel = dinamicaAtual.value.nivel
  if (nivel === 0) return 'Normal'
  if (nivel === 1) return 'Nível 1'
  return 'Nível 2 - Crítico'
})

// Opções para o SearchableSelect de cidades
const cidadesOptions = computed(() => {
  return cidades.value.map(c => ({
    value: c.id,
    label: c.nome,
    sublabel: c.estado
  }))
})

const cidadeSelecionadaId = computed({
  get: () => cidadeSelecionada.value?.id || null,
  set: (id) => {
    const cidade = cidades.value.find(c => c.id === id)
    if (cidade) {
      cidadeSelecionada.value = cidade
      refreshData()
    }
  }
})

// Coordenadas da cidade para o mapa
const cidadeCoords = computed(() => {
  if (!cidadeSelecionada.value) return undefined
  const c = cidadeSelecionada.value
  if (!c.latitude || !c.longitude) return undefined
  return {
    lat: c.latitude,
    lng: c.longitude,
    nome: c.nome
  }
})

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('pt-BR')
}
</script>

<template>
  <div class="min-h-screen bg-bg-primary">
    <!-- Header -->
    <header class="bg-bg-secondary border-b border-border-secondary px-6 py-4">
      <div class="flex items-center justify-between max-w-7xl mx-auto">
        <div class="flex items-center gap-4">
          <NuxtLink to="/" class="text-2xl font-bold text-primary hover:opacity-80">UBIZ</NuxtLink>
          <span class="text-text-secondary">Controle de Dinâmica</span>
        </div>

        <div class="flex items-center gap-4">
          <!-- Seletor de Cidade -->
          <div class="w-56">
            <SearchableSelect
              v-model="cidadeSelecionadaId"
              :options="cidadesOptions"
              placeholder="Selecionar cidade"
              search-placeholder="Buscar cidade..."
            />
          </div>

          <button 
            class="btn-secondary flex items-center gap-2"
            :disabled="refreshing"
            @click="refreshData"
          >
            <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': refreshing }" />
            Atualizar
          </button>
          <NuxtLink to="/cidades" class="btn-secondary flex items-center gap-2">
            <MapPin class="w-4 h-4" />
            Cidades
          </NuxtLink>
        </div>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-96">
      <Loader2 class="w-8 h-8 text-primary animate-spin" />
    </div>

    <!-- Main Content -->
    <main v-else class="max-w-7xl mx-auto px-6 py-8">
      <!-- Page Title -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h2 class="text-3xl font-bold text-text-primary flex items-center gap-3">
            <MapPin class="w-8 h-8 text-primary" />
            {{ cidadeSelecionada?.nome || 'Selecione uma cidade' }}
          </h2>
          <p class="text-text-secondary mt-1">
            Monitoramento de corridas e precificação dinâmica
          </p>
        </div>
        <div v-if="ultimaAtualizacao" class="text-text-tertiary text-sm">
          Última atualização: {{ ultimaAtualizacao.toLocaleTimeString('pt-BR') }}
        </div>
      </div>

      <!-- Mapa de Cobertura -->
      <div class="card mb-8">
        <h3 class="card-title mb-4">Mapa de Cobertura</h3>
        <ClientOnly>
          <MapaPins :key="cidadeSelecionada?.id" :corridas-stats="corridasStats" :cidade="cidadeCoords" />
        </ClientOnly>
      </div>

      <!-- Dinâmica Atual Card -->
      <div class="card mb-8 border-2" :class="dinamicaAtual?.nivel === 2 ? 'border-red-500/50' : 'border-border-secondary'">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-text-secondary text-sm uppercase tracking-wide mb-2">Dinâmica Atual</h3>
            <div class="flex items-baseline gap-3">
              <span class="text-5xl font-bold" :class="multiplicadorClass">
                {{ dinamicaAtual?.multiplicador?.toFixed(1) || '1.0' }}x
              </span>
              <span class="text-text-secondary text-lg">
                {{ nivelLabel }}
              </span>
            </div>
            <p class="text-text-tertiary mt-2">
              {{ dinamicaAtual?.descricao_nivel || 'Sem dinâmica ativa' }}
            </p>
          </div>

          <div class="text-right">
            <div class="flex items-center gap-2 mb-2">
              <component 
                :is="dinamicaAtual?.horario_diurno ? Sun : Moon" 
                class="w-5 h-5"
                :class="dinamicaAtual?.horario_diurno ? 'text-yellow-400' : 'text-blue-400'"
              />
              <span class="text-text-secondary">
                {{ dinamicaAtual?.horario_diurno ? 'Horário Diurno (07-20h)' : 'Horário Noturno (20-07h)' }}
              </span>
            </div>
            <p class="text-text-tertiary text-sm">
              Mínimo: {{ dinamicaAtual?.minimo_solicitacoes || 8 }} solicitações/15min
            </p>
            <p v-if="dinamicaAtual?.quebra_padrao" class="text-red-400 text-sm mt-1 flex items-center gap-1">
              <AlertTriangle class="w-4 h-4" />
              Quebra de padrão detectada!
            </p>
          </div>
        </div>

        <!-- Métricas da última análise -->
        <div v-if="dinamicaAtual" class="grid grid-cols-4 gap-4 mt-6 pt-6 border-t border-border-secondary">
          <div>
            <p class="text-text-tertiary text-sm">Total Analisado</p>
            <p class="text-text-primary text-xl font-semibold">{{ dinamicaAtual.total_corridas }}</p>
          </div>
          <div>
            <p class="text-text-tertiary text-sm">Sucesso (F/A)</p>
            <p class="text-green-400 text-xl font-semibold">{{ dinamicaAtual.corridas_sucesso }}</p>
          </div>
          <div>
            <p class="text-text-tertiary text-sm">Falha</p>
            <p class="text-red-400 text-xl font-semibold">{{ dinamicaAtual.corridas_falha }}</p>
          </div>
          <div>
            <p class="text-text-tertiary text-sm">Taxa de Sucesso</p>
            <p class="text-xl font-semibold" :class="dinamicaAtual.percentual_sucesso >= 70 ? 'text-green-400' : dinamicaAtual.percentual_sucesso >= 50 ? 'text-yellow-400' : 'text-red-400'">
              {{ dinamicaAtual.percentual_sucesso?.toFixed(1) }}%
            </p>
          </div>
        </div>
      </div>

      <!-- Stats Cards - Corridas por Status -->
      <h3 class="text-xl font-semibold text-text-primary mb-4">Corridas Únicas por Status</h3>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        <div 
          v-for="(config, status) in statusConfig" 
          :key="status" 
          class="card"
          :class="config.bgColor"
        >
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="config.bgColor">
              <component :is="config.icon" class="w-5 h-5" :class="config.color" />
            </div>
            <div>
              <p class="text-text-tertiary text-xs">{{ config.label }}</p>
              <p class="text-2xl font-bold" :class="config.color">
                {{ corridasStats[status] || 0 }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Resumo Geral -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="card">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <Car class="w-6 h-6 text-primary" />
            </div>
            <div>
              <p class="text-text-tertiary text-sm">Total de Corridas</p>
              <p class="text-2xl font-bold text-text-primary">{{ totalCorridas }}</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-lg bg-green-400/10 flex items-center justify-center">
              <TrendingUp class="w-6 h-6 text-green-400" />
            </div>
            <div>
              <p class="text-text-tertiary text-sm">Corridas com Sucesso</p>
              <p class="text-2xl font-bold text-green-400">{{ corridasSucesso }}</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-lg flex items-center justify-center" :class="Number(taxaSucesso) >= 70 ? 'bg-green-400/10' : Number(taxaSucesso) >= 50 ? 'bg-yellow-400/10' : 'bg-red-400/10'">
              <Activity class="w-6 h-6" :class="Number(taxaSucesso) >= 70 ? 'text-green-400' : Number(taxaSucesso) >= 50 ? 'text-yellow-400' : 'text-red-400'" />
            </div>
            <div>
              <p class="text-text-tertiary text-sm">Taxa de Sucesso Geral</p>
              <p class="text-2xl font-bold" :class="Number(taxaSucesso) >= 70 ? 'text-green-400' : Number(taxaSucesso) >= 50 ? 'text-yellow-400' : 'text-red-400'">
                {{ taxaSucesso }}%
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Gráfico Visual de Barras -->
      <div class="card">
        <h3 class="card-title mb-6">Distribuição de Status (últimos 15 min)</h3>
        <div class="space-y-4">
          <div v-for="(config, status) in statusConfig" :key="status" class="flex items-center gap-4">
            <div class="w-24 text-text-secondary text-sm">{{ config.label }}</div>
            <div class="flex-1 h-8 bg-bg-tertiary rounded-lg overflow-hidden">
              <div 
                class="h-full rounded-lg transition-all duration-500"
                :style="{ 
                  width: totalCorridas > 0 ? `${((corridasStats[status] || 0) / totalCorridas) * 100}%` : '0%',
                  backgroundColor: config.barColor
                }"
              ></div>
            </div>
            <div class="w-16 text-right">
              <span class="font-semibold" :class="config.color">{{ corridasStats[status] || 0 }}</span>
              <span class="text-text-tertiary text-sm ml-1">
                ({{ totalCorridas > 0 ? (((corridasStats[status] || 0) / totalCorridas) * 100).toFixed(0) : 0 }}%)
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Histórico de Mudanças de Dinâmica -->
      <div class="card mt-8">
        <h3 class="card-title mb-4">Histórico de Mudanças de Dinâmica</h3>
        <div v-if="historicoDinamica.length === 0" class="text-center py-8 text-text-tertiary">
          Nenhuma mudança de dinâmica registrada ainda
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-border-secondary">
                <th class="text-left py-3 px-4 text-text-secondary text-sm font-medium">Data/Hora</th>
                <th class="text-left py-3 px-4 text-text-secondary text-sm font-medium">Multiplicador</th>
                <th class="text-left py-3 px-4 text-text-secondary text-sm font-medium">Nível</th>
                <th class="text-left py-3 px-4 text-text-secondary text-sm font-medium">Taxa Sucesso</th>
                <th class="text-left py-3 px-4 text-text-secondary text-sm font-medium">Corridas</th>
                <th class="text-left py-3 px-4 text-text-secondary text-sm font-medium">Horário</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in historicoDinamica" :key="item.id" class="border-b border-border-secondary hover:bg-bg-tertiary/50">
                <td class="py-3 px-4 text-text-primary text-sm">
                  {{ new Date(item.data_hora).toLocaleString('pt-BR') }}
                </td>
                <td class="py-3 px-4 font-bold" :class="item.multiplicador > 1.5 ? 'text-red-400' : item.multiplicador > 1 ? 'text-orange-400' : 'text-green-400'">
                  {{ item.multiplicador?.toFixed(1) }}x
                </td>
                <td class="py-3 px-4">
                  <span class="px-2 py-1 rounded text-xs" :class="item.nivel === 0 ? 'bg-green-400/20 text-green-400' : item.nivel === 1 ? 'bg-yellow-400/20 text-yellow-400' : 'bg-red-400/20 text-red-400'">
                    Nível {{ item.nivel }}
                  </span>
                </td>
                <td class="py-3 px-4 text-text-primary text-sm">
                  {{ item.percentual_sucesso?.toFixed(1) }}%
                </td>
                <td class="py-3 px-4 text-text-secondary text-sm">
                  {{ item.corridas_sucesso }}/{{ item.total_corridas }}
                </td>
                <td class="py-3 px-4">
                  <component :is="item.horario_diurno ? Sun : Moon" class="w-4 h-4" :class="item.horario_diurno ? 'text-yellow-400' : 'text-blue-400'" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tabela de Níveis de Dinâmica -->
      <div class="card mt-8">
        <h3 class="card-title mb-4">Tabela de Níveis de Dinâmica</h3>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-border-secondary">
                <th class="text-left py-3 px-4 text-text-secondary text-sm font-medium">Nível</th>
                <th class="text-left py-3 px-4 text-text-secondary text-sm font-medium">Taxa Sucesso</th>
                <th class="text-left py-3 px-4 text-text-secondary text-sm font-medium">Multiplicador</th>
                <th class="text-left py-3 px-4 text-text-secondary text-sm font-medium">Descrição</th>
              </tr>
            </thead>
            <tbody>
              <tr class="border-b border-border-secondary" :class="dinamicaAtual?.multiplicador === 1.0 ? 'bg-green-400/10' : ''">
                <td class="py-3 px-4 text-green-400">Normal</td>
                <td class="py-3 px-4 text-text-primary">≥ 70%</td>
                <td class="py-3 px-4 text-green-400 font-bold">1.0x</td>
                <td class="py-3 px-4 text-text-secondary">Sem dinâmica</td>
              </tr>
              <tr class="border-b border-border-secondary" :class="dinamicaAtual?.multiplicador === 1.1 ? 'bg-yellow-400/10' : ''">
                <td class="py-3 px-4 text-yellow-400">Nível 1</td>
                <td class="py-3 px-4 text-text-primary">65% - 69%</td>
                <td class="py-3 px-4 text-yellow-400 font-bold">1.1x</td>
                <td class="py-3 px-4 text-text-secondary">Leve aperto</td>
              </tr>
              <tr class="border-b border-border-secondary" :class="dinamicaAtual?.multiplicador === 1.2 ? 'bg-yellow-400/10' : ''">
                <td class="py-3 px-4 text-yellow-400">Nível 1</td>
                <td class="py-3 px-4 text-text-primary">60% - 64%</td>
                <td class="py-3 px-4 text-yellow-400 font-bold">1.2x</td>
                <td class="py-3 px-4 text-text-secondary">Apertando</td>
              </tr>
              <tr class="border-b border-border-secondary" :class="dinamicaAtual?.multiplicador === 1.3 ? 'bg-orange-400/10' : ''">
                <td class="py-3 px-4 text-orange-400">Nível 1</td>
                <td class="py-3 px-4 text-text-primary">55% - 59%</td>
                <td class="py-3 px-4 text-orange-400 font-bold">1.3x</td>
                <td class="py-3 px-4 text-text-secondary">Forte</td>
              </tr>
              <tr class="border-b border-border-secondary" :class="dinamicaAtual?.multiplicador === 1.4 ? 'bg-orange-400/10' : ''">
                <td class="py-3 px-4 text-orange-400">Nível 1</td>
                <td class="py-3 px-4 text-text-primary">50% - 54%</td>
                <td class="py-3 px-4 text-orange-400 font-bold">1.4x</td>
                <td class="py-3 px-4 text-text-secondary">Crítico leve</td>
              </tr>
              <tr class="border-b border-border-secondary" :class="dinamicaAtual?.multiplicador === 1.5 ? 'bg-orange-400/10' : ''">
                <td class="py-3 px-4 text-orange-400">Nível 1</td>
                <td class="py-3 px-4 text-text-primary">45% - 49%</td>
                <td class="py-3 px-4 text-orange-400 font-bold">1.5x</td>
                <td class="py-3 px-4 text-text-secondary">Crítico</td>
              </tr>
              <tr class="border-b border-border-secondary" :class="dinamicaAtual?.multiplicador === 1.6 ? 'bg-red-400/10' : ''">
                <td class="py-3 px-4 text-red-400">Nível 2</td>
                <td class="py-3 px-4 text-text-primary">40% - 44%</td>
                <td class="py-3 px-4 text-red-400 font-bold">1.6x</td>
                <td class="py-3 px-4 text-text-secondary">+ crítico</td>
              </tr>
              <tr class="border-b border-border-secondary" :class="dinamicaAtual?.multiplicador === 1.7 ? 'bg-red-400/10' : ''">
                <td class="py-3 px-4 text-red-400">Nível 2</td>
                <td class="py-3 px-4 text-text-primary">35% - 39%</td>
                <td class="py-3 px-4 text-red-400 font-bold">1.7x</td>
                <td class="py-3 px-4 text-text-secondary">++ crítico</td>
              </tr>
              <tr class="border-b border-border-secondary" :class="dinamicaAtual?.multiplicador === 1.8 ? 'bg-red-400/10' : ''">
                <td class="py-3 px-4 text-red-400">Nível 2</td>
                <td class="py-3 px-4 text-text-primary">30% - 34%</td>
                <td class="py-3 px-4 text-red-400 font-bold">1.8x</td>
                <td class="py-3 px-4 text-text-secondary">+++ crítico</td>
              </tr>
              <tr class="border-b border-border-secondary" :class="dinamicaAtual?.multiplicador === 2.0 ? 'bg-red-400/10' : ''">
                <td class="py-3 px-4 text-red-400">Nível 2</td>
                <td class="py-3 px-4 text-text-primary">25% - 29%</td>
                <td class="py-3 px-4 text-red-400 font-bold">2.0x</td>
                <td class="py-3 px-4 text-text-secondary">Colapso</td>
              </tr>
              <tr :class="dinamicaAtual?.multiplicador >= 2.5 ? 'bg-red-400/10' : ''">
                <td class="py-3 px-4 text-red-500">Nível 2</td>
                <td class="py-3 px-4 text-text-primary">&lt; 25%</td>
                <td class="py-3 px-4 text-red-500 font-bold">2.5x - 3.0x</td>
                <td class="py-3 px-4 text-text-secondary">Colapso extremo</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>
