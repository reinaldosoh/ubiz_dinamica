<script setup lang="ts">
interface Props {
  modelValue?: string | number
  label?: string
  placeholder?: string
  error?: string
  disabled?: boolean
  required?: boolean
  showMaxButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'R$',
  disabled: false,
  required: false,
  showMaxButton: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'max-click': []
}>()

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const handleMaxClick = () => {
  emit('max-click')
}
</script>

<template>
  <div class="input-group">
    <label v-if="label" class="input-label">
      {{ label }}
      <span v-if="required" class="text-status-error">*</span>
    </label>
    <div class="flex gap-2">
      <input
        type="text"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :class="['input flex-1', { 'input-error': error }]"
        @input="handleInput"
      />
      <button
        v-if="showMaxButton"
        type="button"
        class="px-4 py-3 bg-bg-tertiary border border-border-primary rounded-lg text-text-primary font-medium hover:bg-bg-secondary transition-colors"
        @click="handleMaxClick"
      >
        Max.
      </button>
    </div>
    <p v-if="error" class="input-error-message">{{ error }}</p>
  </div>
</template>
