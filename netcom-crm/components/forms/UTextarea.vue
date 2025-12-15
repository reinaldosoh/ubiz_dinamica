<script setup lang="ts">
interface Props {
  modelValue?: string
  label?: string
  placeholder?: string
  rows?: number
  error?: string
  disabled?: boolean
  required?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  rows: 4,
  disabled: false,
  required: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const handleInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="input-group">
    <label v-if="label" class="input-label">
      {{ label }}
      <span v-if="required" class="text-status-error">*</span>
    </label>
    <textarea
      :value="modelValue"
      :placeholder="placeholder"
      :rows="rows"
      :disabled="disabled"
      :class="['input resize-none', { 'input-error': error }]"
      @input="handleInput"
    />
    <p v-if="error" class="input-error-message">{{ error }}</p>
  </div>
</template>
