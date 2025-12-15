<script setup lang="ts">
interface Props {
  variant?: 'enviada' | 'success' | 'error' | 'neutral' | 'warning'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'neutral',
})

const variantClasses = {
  enviada: 'badge-enviada',
  success: 'badge-success',
  error: 'badge-error',
  neutral: 'badge-neutral',
  warning: 'badge-enviada',
}
</script>

<template>
  <span :class="['badge', variantClasses[variant]]">
    <slot />
  </span>
</template>
