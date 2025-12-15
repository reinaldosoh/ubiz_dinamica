<script setup lang="ts">
interface Props {
  title: string
  subtitle?: string
}

const props = defineProps<Props>()
</script>

<template>
  <div class="flex items-center justify-between mb-8">
    <div>
      <h2 class="text-3xl font-bold text-text-primary">{{ title }}</h2>
      <p v-if="subtitle" class="text-text-secondary mt-1">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.actions">
      <slot name="actions" />
    </div>
  </div>
</template>
