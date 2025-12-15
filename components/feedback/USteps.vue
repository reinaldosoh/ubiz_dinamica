<script setup lang="ts">
import type { Component } from 'vue'

interface Step {
  id: number | string
  title: string
  description?: string
  icon?: Component
}

interface Props {
  steps: Step[]
  currentStep: number | string
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  clickable: false,
})

const emit = defineEmits<{
  'step-click': [stepId: number | string]
}>()

const handleStepClick = (stepId: number | string) => {
  if (props.clickable) {
    emit('step-click', stepId)
  }
}
</script>

<template>
  <div class="steps-container">
    <div
      v-for="step in steps"
      :key="step.id"
      class="step"
      :class="{ 
        active: currentStep === step.id,
        'cursor-pointer': clickable
      }"
      @click="handleStepClick(step.id)"
    >
      <div class="step-icon">
        <component v-if="step.icon" :is="step.icon" class="w-5 h-5" />
        <span v-else class="text-sm font-semibold">{{ step.id }}</span>
      </div>
      <div class="step-content">
        <div class="step-title">{{ step.title }}</div>
        <div v-if="step.description" class="step-description">{{ step.description }}</div>
      </div>
    </div>
  </div>
</template>
