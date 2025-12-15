<script setup lang="ts">
interface InfoItem {
  label: string
  value: string | number
}

interface Props {
  title?: string
  items: InfoItem[]
}

const props = defineProps<Props>()
</script>

<template>
  <div class="bg-bg-tertiary rounded-lg p-4">
    <p v-if="title" class="text-text-secondary text-sm mb-2">{{ title }}</p>
    <div class="grid grid-cols-3 gap-4">
      <div v-for="item in items" :key="item.label">
        <p class="text-text-tertiary text-xs uppercase tracking-wide">{{ item.label }}</p>
        <p class="text-text-primary font-semibold mt-1">{{ item.value }}</p>
      </div>
    </div>
  </div>
</template>
