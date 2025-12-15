<script setup lang="ts">
interface Column {
  key: string
  label: string
  align?: 'left' | 'center' | 'right'
  width?: string
}

interface Props {
  columns: Column[]
  data: Record<string, any>[]
  hoverable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  hoverable: true,
})

const emit = defineEmits<{
  'row-click': [row: Record<string, any>, index: number]
}>()

const alignClasses = {
  left: 'text-left',
  center: 'text-center',
  right: 'text-right',
}
</script>

<template>
  <div class="overflow-x-auto">
    <table class="w-full">
      <thead>
        <tr class="border-b border-border-secondary">
          <th
            v-for="column in columns"
            :key="column.key"
            :class="[
              'py-3 px-4 text-text-secondary text-sm font-medium',
              alignClasses[column.align || 'left']
            ]"
            :style="column.width ? { width: column.width } : {}"
          >
            {{ column.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, index) in data"
          :key="index"
          :class="[
            'border-b border-border-secondary transition-colors',
            { 'hover:bg-bg-tertiary/50 cursor-pointer': hoverable }
          ]"
          @click="emit('row-click', row, index)"
        >
          <td
            v-for="column in columns"
            :key="column.key"
            :class="['py-4 px-4', alignClasses[column.align || 'left']]"
          >
            <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
              {{ row[column.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
