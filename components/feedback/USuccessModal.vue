<script setup lang="ts">
import { Check } from 'lucide-vue-next'

interface Props {
  modelValue: boolean
  title?: string
  message?: string
  buttonText?: string
}

withDefaults(defineProps<Props>(), {
  title: 'Solicitação realizada com sucesso!',
  message: 'A solicitação passará por aprovação e assim que confirmada, a quantia definida irá para uma conta com CPF do colaborador.',
  buttonText: 'Fechar',
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const close = () => {
  emit('update:modelValue', false)
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="modal-overlay" @click.self="close">
        <div class="modal max-w-sm text-center">
          <!-- Success Icon with badge style -->
          <div class="relative w-24 h-24 mx-auto mb-6">
            <!-- Outer decorative ring -->
            <svg class="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
              <polygon 
                points="50,2 61,38 98,38 68,59 79,95 50,74 21,95 32,59 2,38 39,38" 
                fill="var(--primary-green)"
                class="drop-shadow-lg"
              />
            </svg>
            <!-- Check icon -->
            <div class="absolute inset-0 flex items-center justify-center">
              <Check class="w-10 h-10 text-white" stroke-width="3" />
            </div>
          </div>

          <h2 class="text-xl font-bold text-text-primary mb-4">{{ title }}</h2>
          <p class="text-text-secondary mb-6">{{ message }}</p>

          <button class="btn-primary w-full" @click="close">
            {{ buttonText }}
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
