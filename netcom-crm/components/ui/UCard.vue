<script setup lang="ts">
interface Props {
  hoverable?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  hoverable: true,
  padding: 'md',
})

const paddingClasses = {
  none: 'p-0',
  sm: 'p-3',
  md: 'p-5',
  lg: 'p-8',
}
</script>

<template>
  <div 
    :class="[
      'card',
      paddingClasses[padding],
      { 'hover:border-primary hover:-translate-y-0.5': hoverable }
    ]"
  >
    <slot />
  </div>
</template>
