<script setup lang="ts">
import type { Component } from 'vue'

interface Props {
  title: string
  subtitle?: string
  icon: Component
  iconColor?: 'primary' | 'warning' | 'success' | 'error'
}

withDefaults(defineProps<Props>(), {
  iconColor: 'primary',
})

const colorClasses = {
  primary: 'bg-primary/10 text-primary',
  warning: 'bg-status-enviada/10 text-status-enviada',
  success: 'bg-status-success/10 text-status-success',
  error: 'bg-status-error/10 text-status-error',
}
</script>

<template>
  <div class="card p-5 cursor-pointer hover:border-primary">
    <div class="flex items-center gap-4">
      <div :class="['w-12 h-12 rounded-lg flex items-center justify-center', colorClasses[iconColor]]">
        <component :is="icon" class="w-6 h-6" />
      </div>
      <div>
        <h4 class="text-text-primary font-semibold">{{ title }}</h4>
        <p v-if="subtitle" class="text-text-secondary text-sm">{{ subtitle }}</p>
      </div>
    </div>
  </div>
</template>
