<script setup lang="ts">
interface Tab {
  id: string
  label: string
  count?: number
}

interface Props {
  tabs: Tab[]
  modelValue: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const selectTab = (tabId: string) => {
  emit('update:modelValue', tabId)
}
</script>

<template>
  <div class="tabs">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      class="tab"
      :class="{ active: modelValue === tab.id }"
      @click="selectTab(tab.id)"
    >
      {{ tab.label }}
      <span v-if="tab.count !== undefined" class="tab-badge">{{ tab.count }}</span>
    </button>
  </div>
</template>
