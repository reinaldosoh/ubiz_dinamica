<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ChevronDown, Search, X, Check } from 'lucide-vue-next'

interface Option {
  value: string | number
  label: string
  sublabel?: string
}

const props = defineProps<{
  modelValue: string | number | null
  options: Option[]
  placeholder?: string
  searchPlaceholder?: string
  disabled?: boolean
  clearable?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number | null): void
}>()

const isOpen = ref(false)
const searchQuery = ref('')
const dropdownRef = ref<HTMLDivElement>()
const inputRef = ref<HTMLInputElement>()

const filteredOptions = computed(() => {
  if (!searchQuery.value) return props.options
  const query = searchQuery.value.toLowerCase()
  return props.options.filter(opt => 
    opt.label.toLowerCase().includes(query) ||
    (opt.sublabel && opt.sublabel.toLowerCase().includes(query))
  )
})

const selectedOption = computed(() => {
  return props.options.find(opt => opt.value === props.modelValue)
})

function toggleDropdown() {
  if (props.disabled) return
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    searchQuery.value = ''
    setTimeout(() => inputRef.value?.focus(), 50)
  }
}

function selectOption(option: Option) {
  emit('update:modelValue', option.value)
  isOpen.value = false
  searchQuery.value = ''
}

function clearSelection() {
  emit('update:modelValue', null)
}

function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="dropdownRef" class="relative">
    <button
      type="button"
      class="w-full bg-bg-tertiary border border-border-secondary rounded-lg px-4 py-2 text-left flex items-center justify-between gap-2 transition-colors"
      :class="[
        disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-primary/50 cursor-pointer',
        isOpen ? 'border-primary' : ''
      ]"
      @click="toggleDropdown"
      :disabled="disabled"
    >
      <span :class="selectedOption ? 'text-text-primary' : 'text-text-tertiary'">
        {{ selectedOption?.label || placeholder || 'Selecione...' }}
      </span>
      <div class="flex items-center gap-1">
        <button
          v-if="clearable && selectedOption"
          type="button"
          class="p-1 hover:bg-bg-secondary rounded transition-colors"
          @click.stop="clearSelection"
        >
          <X class="w-4 h-4 text-text-tertiary" />
        </button>
        <ChevronDown 
          class="w-4 h-4 text-text-tertiary transition-transform" 
          :class="{ 'rotate-180': isOpen }"
        />
      </div>
    </button>

    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div
        v-if="isOpen"
        class="absolute z-50 w-full mt-1 bg-bg-secondary border border-border-secondary rounded-lg shadow-xl overflow-hidden"
      >
        <div class="p-2 border-b border-border-secondary">
          <div class="relative">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-tertiary" />
            <input
              ref="inputRef"
              v-model="searchQuery"
              type="text"
              class="w-full bg-bg-tertiary border border-border-secondary rounded-lg pl-9 pr-4 py-2 text-text-primary text-sm focus:outline-none focus:border-primary"
              :placeholder="searchPlaceholder || 'Pesquisar...'"
              @click.stop
            />
          </div>
        </div>

        <div class="max-h-60 overflow-y-auto">
          <div
            v-if="filteredOptions.length === 0"
            class="px-4 py-3 text-text-tertiary text-sm text-center"
          >
            Nenhum resultado encontrado
          </div>
          <button
            v-for="option in filteredOptions"
            :key="option.value"
            type="button"
            class="w-full px-4 py-2 text-left hover:bg-bg-tertiary transition-colors flex items-center justify-between gap-2"
            :class="option.value === modelValue ? 'bg-primary/10' : ''"
            @click="selectOption(option)"
          >
            <div>
              <div class="text-text-primary text-sm">{{ option.label }}</div>
              <div v-if="option.sublabel" class="text-text-tertiary text-xs">{{ option.sublabel }}</div>
            </div>
            <Check 
              v-if="option.value === modelValue" 
              class="w-4 h-4 text-primary flex-shrink-0" 
            />
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>
