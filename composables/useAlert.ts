import { ref } from 'vue'

type AlertType = 'success' | 'error' | 'warning' | 'info'

interface AlertState {
  show: boolean
  type: AlertType
  title: string
  message: string
  confirmText: string
  cancelText: string
  showCancel: boolean
  onConfirm?: () => void
  onCancel?: () => void
}

const alertState = ref<AlertState>({
  show: false,
  type: 'info',
  title: '',
  message: '',
  confirmText: 'OK',
  cancelText: 'Cancelar',
  showCancel: false
})

export function useAlert() {
  function showAlert(options: {
    type?: AlertType
    title?: string
    message: string
    confirmText?: string
    cancelText?: string
    showCancel?: boolean
    onConfirm?: () => void
    onCancel?: () => void
  }) {
    alertState.value = {
      show: true,
      type: options.type || 'info',
      title: options.title || '',
      message: options.message,
      confirmText: options.confirmText || 'OK',
      cancelText: options.cancelText || 'Cancelar',
      showCancel: options.showCancel || false,
      onConfirm: options.onConfirm,
      onCancel: options.onCancel
    }
  }

  function success(message: string, title?: string) {
    showAlert({ type: 'success', title, message })
  }

  function error(message: string, title?: string) {
    showAlert({ type: 'error', title: title || 'Erro', message })
  }

  function warning(message: string, title?: string) {
    showAlert({ type: 'warning', title: title || 'Atenção', message })
  }

  function info(message: string, title?: string) {
    showAlert({ type: 'info', title, message })
  }

  function confirm(options: {
    title?: string
    message: string
    confirmText?: string
    cancelText?: string
    onConfirm?: () => void
    onCancel?: () => void
  }): Promise<boolean> {
    return new Promise((resolve) => {
      showAlert({
        type: 'warning',
        title: options.title || 'Confirmar',
        message: options.message,
        confirmText: options.confirmText || 'Confirmar',
        cancelText: options.cancelText || 'Cancelar',
        showCancel: true,
        onConfirm: () => {
          options.onConfirm?.()
          resolve(true)
        },
        onCancel: () => {
          options.onCancel?.()
          resolve(false)
        }
      })
    })
  }

  function closeAlert() {
    alertState.value.show = false
  }

  function handleConfirm() {
    alertState.value.onConfirm?.()
    closeAlert()
  }

  function handleCancel() {
    alertState.value.onCancel?.()
    closeAlert()
  }

  return {
    alertState,
    showAlert,
    success,
    error,
    warning,
    info,
    confirm,
    closeAlert,
    handleConfirm,
    handleCancel
  }
}
