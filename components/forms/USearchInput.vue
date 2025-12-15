<script setup lang="ts">
import { Search } from 'lucide-vue-next'

interface Props {
  modelValue?: string
  placeholder?: string
  width?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Buscar...',
  width: 'w-64',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="search-input-wrapper">
    <Search class="search-icon w-5 h-5" />
    <input
      type="text"
      :value="modelValue"
      :placeholder="placeholder"
      :class="['search-input', width]"
      @input="handleInput"
    />
  </div>
</template>
