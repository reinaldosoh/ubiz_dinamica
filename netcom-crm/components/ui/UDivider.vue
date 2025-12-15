<script setup lang="ts">
interface Props {
  vertical?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  vertical: false,
})
</script>

<template>
  <div :class="vertical ? 'divider-vertical' : 'divider'" />
</template>
