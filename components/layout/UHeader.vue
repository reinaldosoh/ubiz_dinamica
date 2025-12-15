<script setup lang="ts">
import { Bell, Settings, User, Search } from 'lucide-vue-next'

interface Props {
  title?: string
  subtitle?: string
}

withDefaults(defineProps<Props>(), {
  title: 'NETCOM',
  subtitle: 'CRM',
})

const searchQuery = ref('')
</script>

<template>
  <header class="bg-bg-secondary border-b border-border-secondary px-6 py-4">
    <div class="flex items-center justify-between max-w-7xl mx-auto">
      <div class="flex items-center gap-4">
        <h1 class="text-2xl font-bold text-primary">{{ title }}</h1>
        <span class="text-text-secondary">{{ subtitle }}</span>
      </div>

      <div class="flex items-center gap-4">
        <slot name="search">
          <div class="search-input-wrapper">
            <Search class="search-icon w-5 h-5" />
            <input
              v-model="searchQuery"
              type="text"
              class="search-input w-64"
              placeholder="Buscar clientes, propostas..."
            />
          </div>
        </slot>

        <slot name="actions">
          <button class="btn-icon">
            <Bell class="w-5 h-5 text-text-secondary" />
          </button>
          <button class="btn-icon">
            <Settings class="w-5 h-5 text-text-secondary" />
          </button>
        </slot>

        <slot name="avatar">
          <div class="avatar">
            <User class="w-5 h-5 text-text-secondary" />
          </div>
        </slot>
      </div>
    </div>
  </header>
</template>
