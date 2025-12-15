<script setup lang="ts">
import { TrendingUp, TrendingDown } from 'lucide-vue-next'
import type { Component } from 'vue'

interface Props {
  label: string
  value: string | number
  icon?: Component
  trend?: string
  trendUp?: boolean
}

withDefaults(defineProps<Props>(), {
  trendUp: true,
})
</script>

<template>
  <div class="card p-5">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-text-secondary text-sm">{{ label }}</p>
        <p class="text-2xl font-bold text-text-primary mt-1">{{ value }}</p>
      </div>
      <div v-if="icon" class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
        <component :is="icon" class="w-5 h-5 text-primary" />
      </div>
    </div>
    <div v-if="trend" class="flex items-center gap-1 mt-3">
      <TrendingUp v-if="trendUp" class="w-4 h-4 text-status-success" />
      <TrendingDown v-else class="w-4 h-4 text-status-error" />
      <span :class="['text-sm', trendUp ? 'text-status-success' : 'text-status-error']">{{ trend }}</span>
      <span class="text-sm text-text-tertiary">vs mês anterior</span>
    </div>
  </div>
</template>
