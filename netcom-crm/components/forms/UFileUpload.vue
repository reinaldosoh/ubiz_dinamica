<script setup lang="ts">
import { Upload } from 'lucide-vue-next'

interface Props {
  label?: string
  placeholder?: string
  accept?: string
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Clique aqui para enviar o arquivo ou arraste-o aqui',
  accept: '*',
})

const emit = defineEmits<{
  'file-selected': [file: File]
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const fileName = ref<string>('')
const isDragging = ref(false)

const handleClick = () => {
  fileInput.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    fileName.value = target.files[0].name
    emit('file-selected', target.files[0])
  }
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    fileName.value = event.dataTransfer.files[0].name
    emit('file-selected', event.dataTransfer.files[0])
  }
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}
</script>

<template>
  <div class="input-group">
    <label v-if="label" class="input-label">{{ label }}</label>
    <div
      :class="[
        'input cursor-pointer flex items-center gap-3 transition-all',
        { 'border-primary bg-primary/5': isDragging }
      ]"
      @click="handleClick"
      @drop.prevent="handleDrop"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
    >
      <Upload class="w-5 h-5 text-text-placeholder" />
      <span :class="fileName ? 'text-text-primary' : 'text-text-placeholder'">
        {{ fileName || placeholder }}
      </span>
    </div>
    <input
      ref="fileInput"
      type="file"
      :accept="accept"
      class="hidden"
      @change="handleFileChange"
    />
    <p v-if="error" class="input-error-message">{{ error }}</p>
  </div>
</template>
