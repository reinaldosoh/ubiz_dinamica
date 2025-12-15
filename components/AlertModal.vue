<script setup lang="ts">
import { ref, watch } from 'vue'
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-vue-next'

type AlertType = 'success' | 'error' | 'warning' | 'info'

interface AlertModalProps {
  show: boolean
  type?: AlertType
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  showCancel?: boolean
}

const props = withDefaults(defineProps<AlertModalProps>(), {
  type: 'info',
  title: '',
  confirmText: 'OK',
  cancelText: 'Cancelar',
  showCancel: false
})

const emit = defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
  (e: 'close'): void
}>()

const icons = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info
}

const colors = {
  success: {
    icon: 'text-green-400',
    bg: 'bg-green-400/10',
    border: 'border-green-400/30'
  },
  error: {
    icon: 'text-red-400',
    bg: 'bg-red-400/10',
    border: 'border-red-400/30'
  },
  warning: {
    icon: 'text-yellow-400',
    bg: 'bg-yellow-400/10',
    border: 'border-yellow-400/30'
  },
  info: {
    icon: 'text-blue-400',
    bg: 'bg-blue-400/10',
    border: 'border-blue-400/30'
  }
}

function handleConfirm() {
  emit('confirm')
  emit('close')
}

function handleCancel() {
  emit('cancel')
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="show" 
        class="fixed inset-0 bg-black/60 flex items-center justify-center z-[100] p-4"
        @click.self="handleCancel"
      >
        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div 
            v-if="show"
            class="bg-bg-secondary rounded-xl p-6 w-full max-w-md border shadow-2xl"
            :class="colors[type].border"
          >
            <div class="flex items-start gap-4">
              <div 
                class="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
                :class="colors[type].bg"
              >
                <component 
                  :is="icons[type]" 
                  class="w-6 h-6"
                  :class="colors[type].icon"
                />
              </div>
              
              <div class="flex-1 min-w-0">
                <h3 v-if="title" class="text-lg font-semibold text-text-primary mb-1">
                  {{ title }}
                </h3>
                <p class="text-text-secondary whitespace-pre-wrap">{{ message }}</p>
              </div>

              <button 
                class="text-text-tertiary hover:text-text-primary transition-colors p-1 -mt-1 -mr-1"
                @click="handleCancel"
              >
                <X class="w-5 h-5" />
              </button>
            </div>

            <div class="flex justify-end gap-3 mt-6">
              <button 
                v-if="showCancel"
                class="btn-secondary"
                @click="handleCancel"
              >
                {{ cancelText }}
              </button>
              <button 
                class="btn-primary"
                @click="handleConfirm"
              >
                {{ confirmText }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>
