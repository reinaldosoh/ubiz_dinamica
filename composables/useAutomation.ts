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

interface CorridasStats {
  total: number
  pendentes: number
  finalizadas: number
  canceladas: number
  nao_atendidas: number
  aceitas: number
  em_espera: number
}

interface DinamicaRequest {
  multiplicador: number
  headless?: boolean
  email?: string
  password?: string
  apiUrl?: string
  cidade?: string
  estado?: string
  corridas_stats?: CorridasStats
}

interface DinamicaResponse {
  success: boolean
  message: string
  multiplicador_aplicado: number | null
  screenshot_path: string | null
}

export const useAutomation = () => {
  const DEFAULT_API_URL = 'http://localhost:8000'

  const login = async (credentials?: LoginCredentials, apiUrl?: string): Promise<LoginResponse> => {
    const baseUrl = apiUrl || DEFAULT_API_URL
    const response = await $fetch<LoginResponse>(`${baseUrl}/login`, {
      method: 'POST',
      body: credentials || {}
    })
    return response
  }

  const loginTest = async (apiUrl?: string): Promise<LoginResponse> => {
    const baseUrl = apiUrl || DEFAULT_API_URL
    const response = await $fetch<LoginResponse>(`${baseUrl}/login/test`, {
      method: 'POST'
    })
    return response
  }

  const loginVisual = async (apiUrl?: string): Promise<LoginResponse> => {
    const baseUrl = apiUrl || DEFAULT_API_URL
    const response = await $fetch<LoginResponse>(`${baseUrl}/login/visual`, {
      method: 'POST'
    })
    return response
  }

  const healthCheck = async (apiUrl?: string): Promise<{ status: string }> => {
    const baseUrl = apiUrl || DEFAULT_API_URL
    const response = await $fetch<{ status: string }>(`${baseUrl}/health`)
    return response
  }

  const atualizarDinamica = async (request: DinamicaRequest): Promise<DinamicaResponse> => {
    const baseUrl = request.apiUrl || DEFAULT_API_URL
    const { apiUrl, ...body } = request
    const response = await $fetch<DinamicaResponse>(`${baseUrl}/dinamica/atualizar`, {
      method: 'POST',
      body
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
