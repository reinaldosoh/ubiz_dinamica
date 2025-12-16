interface LoginCredentials {
  email?: string
  password?: string
  headless?: boolean
}

interface LoginResponse {
  success: boolean
  message: string
  screenshot_path: string | null
}

interface DinamicaRequest {
  multiplicador: number
  headless?: boolean
  email?: string
  password?: string
}

interface DinamicaResponse {
  success: boolean
  message: string
  multiplicador_aplicado: number | null
  screenshot_path: string | null
}

export const useAutomation = () => {
  const AUTOMATION_API_URL = 'http://localhost:8000'

  const login = async (credentials?: LoginCredentials): Promise<LoginResponse> => {
    const response = await $fetch<LoginResponse>(`${AUTOMATION_API_URL}/login`, {
      method: 'POST',
      body: credentials || {}
    })
    return response
  }

  const loginTest = async (): Promise<LoginResponse> => {
    const response = await $fetch<LoginResponse>(`${AUTOMATION_API_URL}/login/test`, {
      method: 'POST'
    })
    return response
  }

  const loginVisual = async (): Promise<LoginResponse> => {
    const response = await $fetch<LoginResponse>(`${AUTOMATION_API_URL}/login/visual`, {
      method: 'POST'
    })
    return response
  }

  const healthCheck = async (): Promise<{ status: string }> => {
    const response = await $fetch<{ status: string }>(`${AUTOMATION_API_URL}/health`)
    return response
  }

  const atualizarDinamica = async (request: DinamicaRequest): Promise<DinamicaResponse> => {
    const response = await $fetch<DinamicaResponse>(`${AUTOMATION_API_URL}/dinamica/atualizar`, {
      method: 'POST',
      body: request
    })
    return response
  }

  return {
    login,
    loginTest,
    loginVisual,
    healthCheck,
    atualizarDinamica
  }
}
