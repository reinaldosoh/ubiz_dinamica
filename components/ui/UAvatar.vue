<script setup lang="ts">
import { User } from 'lucide-vue-next'

interface Props {
  src?: string
  alt?: string
  size?: 'sm' | 'md' | 'lg'
  fallbackIcon?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  fallbackIcon: true,
})

const sizeClasses = {
  sm: 'avatar-sm',
  md: '',
  lg: 'avatar-lg',
}

const iconSizes = {
  sm: 'w-4 h-4',
  md: 'w-5 h-5',
  lg: 'w-7 h-7',
}
</script>

<template>
  <div :class="['avatar', sizeClasses[size]]">
    <img v-if="src" :src="src" :alt="alt" />
    <User v-else-if="fallbackIcon" :class="[iconSizes[size], 'text-text-secondary']" />
    <slot v-else />
  </div>
</template>
