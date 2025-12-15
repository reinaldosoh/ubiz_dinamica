<script setup lang="ts">
// Redirecionar para /cidades
const router = useRouter()
router.replace('/cidades')
</script>

<template>
  <div class="min-h-screen bg-bg-primary flex items-center justify-center">
    <p class="text-text-secondary">Redirecionando...</p>
  </div>
</template>
