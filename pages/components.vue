<script setup lang="ts">
import { 
  Settings, 
  FileText, 
  Check, 
  Clock,
  Calendar,
  Mail,
  Phone,
  Users,
  BarChart3,
  TrendingUp,
  Search,
  ChevronRight,
  X
} from 'lucide-vue-next'

// Estados
const activeTab = ref('tab1')
const showModal = ref(false)
const showSuccessModal = ref(false)
const currentStep = ref(1)

// Dados de exemplo
const tabs = [
  { id: 'tab1', label: 'Todos', count: 156 },
  { id: 'tab2', label: 'Pendentes', count: 23 },
  { id: 'tab3', label: 'Aprovados', count: 89 },
]

const steps = [
  { id: 1, title: 'Etapa 1', description: 'Informações básicas', icon: Settings },
  { id: 2, title: 'Etapa 2', description: 'Tarefas a fazer', icon: FileText },
  { id: 3, title: 'Etapa 3', description: 'Prazos', icon: Clock },
  { id: 4, title: 'Etapa 4', description: 'Revisão', icon: Check },
]

const infoItems = [
  { label: 'CPF', value: '123.456.789-10' },
  { label: 'Carteira', value: 'R$10.000' },
  { label: 'Limite', value: 'R$1.000,00' },
]

// Form states
const inputValue = ref('')
const textareaValue = ref('')
const selectValue = ref('')
const checkboxValue = ref(false)
const searchValue = ref('')
</script>

<template>
  <div class="min-h-screen bg-bg-primary p-8">
    <div class="max-w-6xl mx-auto">
      <h1 class="text-3xl font-bold text-text-primary mb-2">Componentes do Design System</h1>
      <p class="text-text-secondary mb-8">Biblioteca de componentes globais do NETCOM CRM</p>

      <!-- Buttons -->
      <section class="mb-12">
        <h2 class="text-xl font-semibold text-text-primary mb-4">Botões</h2>
        <div class="card p-5">
          <div class="flex flex-wrap gap-4">
            <button class="btn-primary">Primary</button>
            <button class="btn-secondary">Secondary</button>
            <button class="btn-primary px-4 py-2 text-sm">Small</button>
            <button class="btn-primary px-8 py-4 text-lg">Large</button>
            <button class="btn-primary opacity-50 cursor-not-allowed">Disabled</button>
            <button class="btn-icon"><Settings class="w-5 h-5 text-text-secondary" /></button>
          </div>
        </div>
      </section>

      <!-- Badges -->
      <section class="mb-12">
        <h2 class="text-xl font-semibold text-text-primary mb-4">Badges</h2>
        <div class="card p-5">
          <div class="flex flex-wrap gap-4">
            <span class="badge badge-success">Aprovado</span>
            <span class="badge badge-enviada">Enviada</span>
            <span class="badge badge-error">Rejeitado</span>
            <span class="badge badge-neutral">Neutro</span>
          </div>
        </div>
      </section>

      <!-- Avatars -->
      <section class="mb-12">
        <h2 class="text-xl font-semibold text-text-primary mb-4">Avatars</h2>
        <div class="card p-5">
          <div class="flex items-center gap-4">
            <div class="avatar avatar-sm"><Users class="w-4 h-4 text-text-secondary" /></div>
            <div class="avatar"><Users class="w-5 h-5 text-text-secondary" /></div>
            <div class="avatar avatar-lg"><Users class="w-7 h-7 text-text-secondary" /></div>
          </div>
        </div>
      </section>

      <!-- Tabs -->
      <section class="mb-12">
        <h2 class="text-xl font-semibold text-text-primary mb-4">Tabs</h2>
        <div class="card p-5">
          <div class="tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              class="tab"
              :class="{ active: activeTab === tab.id }"
              @click="activeTab = tab.id"
            >
              {{ tab.label }}
              <span class="tab-badge">{{ tab.count }}</span>
            </button>
          </div>
          <p class="text-text-secondary mt-4">Tab selecionada: {{ activeTab }}</p>
        </div>
      </section>

      <!-- Form Inputs -->
      <section class="mb-12">
        <h2 class="text-xl font-semibold text-text-primary mb-4">Formulários</h2>
        <div class="card p-5">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Input -->
            <div class="input-group">
              <label class="input-label">Input de Texto</label>
              <input v-model="inputValue" type="text" class="input" placeholder="Digite algo..." />
            </div>

            <!-- Select -->
            <div class="input-group">
              <label class="input-label">Select</label>
              <select v-model="selectValue" class="select">
                <option value="" disabled>Selecione...</option>
                <option value="1">Opção 1</option>
                <option value="2">Opção 2</option>
                <option value="3">Opção 3</option>
              </select>
            </div>

            <!-- Textarea -->
            <div class="input-group">
              <label class="input-label">Textarea</label>
              <textarea v-model="textareaValue" class="input resize-none" rows="3" placeholder="Descrição..."></textarea>
            </div>

            <!-- Search -->
            <div class="input-group">
              <label class="input-label">Busca</label>
              <div class="search-input-wrapper">
                <Search class="search-icon w-5 h-5" />
                <input v-model="searchValue" type="text" class="search-input w-full" placeholder="Buscar..." />
              </div>
            </div>

            <!-- Checkbox -->
            <div class="input-group">
              <label class="checkbox-wrapper">
                <input v-model="checkboxValue" type="checkbox" class="checkbox" />
                <span class="checkbox-label">Aceito os termos</span>
              </label>
            </div>
          </div>
        </div>
      </section>

      <!-- Steps -->
      <section class="mb-12">
        <h2 class="text-xl font-semibold text-text-primary mb-4">Steps</h2>
        <div class="card p-5">
          <div class="steps-container">
            <div
              v-for="step in steps"
              :key="step.id"
              class="step cursor-pointer"
              :class="{ active: currentStep === step.id }"
              @click="currentStep = step.id"
            >
              <div class="step-icon">
                <component :is="step.icon" class="w-5 h-5" />
              </div>
              <div class="step-content">
                <div class="step-title">{{ step.title }}</div>
                <div class="step-description">{{ step.description }}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Info Card -->
      <section class="mb-12">
        <h2 class="text-xl font-semibold text-text-primary mb-4">Info Card</h2>
        <div class="card p-5">
          <div class="bg-bg-tertiary rounded-lg p-4">
            <p class="text-text-secondary text-sm mb-2">Colaborador José Carlos Junior</p>
            <div class="grid grid-cols-3 gap-4">
              <div v-for="item in infoItems" :key="item.label">
                <p class="text-text-tertiary text-xs uppercase tracking-wide">{{ item.label }}</p>
                <p class="text-text-primary font-semibold mt-1">{{ item.value }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Stat Cards -->
      <section class="mb-12">
        <h2 class="text-xl font-semibold text-text-primary mb-4">Stat Cards</h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="card p-5">
            <div class="flex items-start justify-between">
              <div>
                <p class="text-text-secondary text-sm">Total de Clientes</p>
                <p class="text-2xl font-bold text-text-primary mt-1">1.248</p>
              </div>
              <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <Users class="w-5 h-5 text-primary" />
              </div>
            </div>
            <div class="flex items-center gap-1 mt-3">
              <TrendingUp class="w-4 h-4 text-status-success" />
              <span class="text-sm text-status-success">+12%</span>
              <span class="text-sm text-text-tertiary">vs mês anterior</span>
            </div>
          </div>

          <div class="card p-5">
            <div class="flex items-start justify-between">
              <div>
                <p class="text-text-secondary text-sm">Propostas</p>
                <p class="text-2xl font-bold text-text-primary mt-1">86</p>
              </div>
              <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <FileText class="w-5 h-5 text-primary" />
              </div>
            </div>
            <div class="flex items-center gap-1 mt-3">
              <TrendingUp class="w-4 h-4 text-status-success" />
              <span class="text-sm text-status-success">+8%</span>
              <span class="text-sm text-text-tertiary">vs mês anterior</span>
            </div>
          </div>

          <div class="card p-5">
            <div class="flex items-start justify-between">
              <div>
                <p class="text-text-secondary text-sm">Taxa de Conversão</p>
                <p class="text-2xl font-bold text-text-primary mt-1">34%</p>
              </div>
              <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <BarChart3 class="w-5 h-5 text-primary" />
              </div>
            </div>
            <div class="flex items-center gap-1 mt-3">
              <TrendingUp class="w-4 h-4 text-status-success" />
              <span class="text-sm text-status-success">+5%</span>
              <span class="text-sm text-text-tertiary">vs mês anterior</span>
            </div>
          </div>

          <div class="card p-5">
            <div class="flex items-start justify-between">
              <div>
                <p class="text-text-secondary text-sm">Receita</p>
                <p class="text-2xl font-bold text-text-primary mt-1">R$ 156K</p>
              </div>
              <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <TrendingUp class="w-5 h-5 text-primary" />
              </div>
            </div>
            <div class="flex items-center gap-1 mt-3">
              <TrendingUp class="w-4 h-4 text-status-success" />
              <span class="text-sm text-status-success">+18%</span>
              <span class="text-sm text-text-tertiary">vs mês anterior</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Quick Actions -->
      <section class="mb-12">
        <h2 class="text-xl font-semibold text-text-primary mb-4">Quick Actions</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="card p-5 cursor-pointer hover:border-primary">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Calendar class="w-6 h-6 text-primary" />
              </div>
              <div>
                <h4 class="text-text-primary font-semibold">Agendar Reunião</h4>
                <p class="text-text-secondary text-sm">5 reuniões hoje</p>
              </div>
            </div>
          </div>

          <div class="card p-5 cursor-pointer hover:border-primary">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-lg bg-status-enviada/10 flex items-center justify-center">
                <Mail class="w-6 h-6 text-status-enviada" />
              </div>
              <div>
                <h4 class="text-text-primary font-semibold">Enviar E-mail</h4>
                <p class="text-text-secondary text-sm">12 pendentes</p>
              </div>
            </div>
          </div>

          <div class="card p-5 cursor-pointer hover:border-primary">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-lg bg-status-success/10 flex items-center justify-center">
                <Phone class="w-6 h-6 text-status-success" />
              </div>
              <div>
                <h4 class="text-text-primary font-semibold">Fazer Ligação</h4>
                <p class="text-text-secondary text-sm">3 follow-ups</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Modals -->
      <section class="mb-12">
        <h2 class="text-xl font-semibold text-text-primary mb-4">Modais</h2>
        <div class="card p-5">
          <div class="flex gap-4">
            <button class="btn-primary" @click="showModal = true">Abrir Modal</button>
            <button class="btn-secondary" @click="showSuccessModal = true">Modal de Sucesso</button>
          </div>
        </div>
      </section>

      <!-- Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
            <div class="modal max-w-lg">
              <div class="modal-header">
                <h2 class="modal-title">Adicionar campanha</h2>
                <button class="modal-close" @click="showModal = false">
                  <X class="w-5 h-5" />
                </button>
              </div>

              <div class="modal-body">
                <div class="input-group">
                  <label class="input-label">Capa</label>
                  <div class="input cursor-pointer flex items-center gap-3">
                    <span class="text-text-placeholder">Clique aqui para enviar o arquivo ou arraste-o aqui</span>
                  </div>
                </div>

                <div class="input-group">
                  <label class="input-label">Nome</label>
                  <input type="text" class="input" placeholder="Festa Junina Nexi!" />
                </div>

                <div class="input-group">
                  <label class="input-label">Descrição</label>
                  <textarea class="input resize-none" rows="3" placeholder="Venha no ritmo da festa junina..."></textarea>
                </div>

                <div class="input-group">
                  <label class="input-label">Link</label>
                  <input type="text" class="input" placeholder="Digite" />
                </div>

                <div class="input-group">
                  <label class="input-label">Status da campanha</label>
                  <select class="select">
                    <option value="ativo">Ativo</option>
                    <option value="inativo">Inativo</option>
                  </select>
                </div>
              </div>

              <div class="modal-footer">
                <button class="btn-secondary" @click="showModal = false">Cancelar</button>
                <button class="btn-primary" @click="showModal = false; showSuccessModal = true">Criar campanha</button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Success Modal -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showSuccessModal" class="modal-overlay" @click.self="showSuccessModal = false">
            <div class="modal max-w-sm text-center">
              <!-- Success Icon -->
              <div class="relative w-24 h-24 mx-auto mb-6">
                <svg class="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
                  <polygon 
                    points="50,2 61,38 98,38 68,59 79,95 50,74 21,95 32,59 2,38 39,38" 
                    fill="var(--primary-green)"
                    class="drop-shadow-lg"
                  />
                </svg>
                <div class="absolute inset-0 flex items-center justify-center">
                  <Check class="w-10 h-10 text-white" stroke-width="3" />
                </div>
              </div>

              <h2 class="text-xl font-bold text-text-primary mb-4">Solicitação realizada com sucesso!</h2>
              <p class="text-text-secondary mb-6">
                A solicitação passará por aprovação e assim que confirmada, a quantia definida irá para uma conta com CPF do colaborador.
              </p>

              <button class="btn-primary w-full" @click="showSuccessModal = false">Fechar</button>
            </div>
          </div>
        </Transition>
      </Teleport>
    </div>
  </div>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
