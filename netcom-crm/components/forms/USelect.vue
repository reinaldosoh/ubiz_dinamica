<script setup lang="ts">
interface Option {
  value: string | number
  label: string
}

interface Props {
  modelValue?: string | number
  label?: string
  placeholder?: string
  options: Option[]
  error?: string
  disabled?: boolean
  required?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  required: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
}>()

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="input-group">
    <label v-if="label" class="input-label">
      {{ label }}
      <span v-if="required" class="text-status-error">*</span>
    </label>
    <select
      :value="modelValue"
      :disabled="disabled"
      :class="['select', { 'input-error': error }]"
      @change="handleChange"
    >
      <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
    <p v-if="error" class="input-error-message">{{ error }}</p>
  </div>
</template>
