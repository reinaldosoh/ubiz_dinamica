interface TaximachineWebhook {
  id: string
  tipo: string
  responsavel: string
  url: string
}

interface TaximachineApiResponse {
  success: boolean
  response?: {
    webhooks: TaximachineWebhook[]
    quantidade_webhooks: number
  }
}

interface DeleteWebhookResponse {
  success: boolean
  message?: string
  error?: string
}

export const useTaximachineWebhook = () => {
  /**
   * Lista todos os webhooks cadastrados no TaxiMachine para uma cidade
   */
  const listarWebhooks = async (
    cidadeId: string,
    apiKey: string,
    authBase64: string
  ): Promise<TaximachineWebhook[]> => {
    try {
      const response = await fetch('https://api.taximachine.com.br/api/integracao/listarWebhook', {
        method: 'GET',
        headers: {
          'User-Agent': 'ua-ubizcar',
          'api-key': apiKey,
          'Authorization': `Basic ${authBase64}`
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data: TaximachineApiResponse[] = await response.json()
      
      if (data && data[0]?.success && data[0].response?.webhooks) {
        return data[0].response.webhooks
      }

      return []
    } catch (error) {
      console.error('Erro ao listar webhooks:', error)
      throw error
    }
  }

  /**
   * Deleta um webhook específico no TaxiMachine
   */
  const deletarWebhook = async (
    webhookId: string,
    apiKey: string,
    authBase64: string
  ): Promise<boolean> => {
    try {
      const response = await fetch(
        `https://api.taximachine.com.br/api/integracao/deletarWebhook/${webhookId}`,
        {
          method: 'DELETE',
          headers: {
            'User-Agent': 'ua-ubizcar',
            'api-key': apiKey,
            'Authorization': `Basic ${authBase64}`
          }
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data: DeleteWebhookResponse = await response.json()
      return data.success
    } catch (error) {
      console.error('Erro ao deletar webhook:', error)
      throw error
    }
  }

  /**
   * Encontra e deleta webhooks do tipo "status" antes de recadastrar
   */
  const limparWebhooksStatus = async (
    cidadeId: string,
    apiKey: string,
    authBase64: string
  ): Promise<{ deletados: number; erros: string[] }> => {
    const resultado = {
      deletados: 0,
      erros: [] as string[]
    }

    try {
      // Listar todos os webhooks
      const webhooks = await listarWebhooks(cidadeId, apiKey, authBase64)
      
      // Filtrar apenas os do tipo "status"
      const webhooksStatus = webhooks.filter(w => w.tipo === 'status')

      // Deletar cada um
      for (const webhook of webhooksStatus) {
        try {
          const sucesso = await deletarWebhook(webhook.id, apiKey, authBase64)
          if (sucesso) {
            resultado.deletados++
          } else {
            resultado.erros.push(`Falha ao deletar webhook ${webhook.id}`)
          }
        } catch (error) {
          resultado.erros.push(`Erro ao deletar webhook ${webhook.id}: ${error}`)
        }
      }

      return resultado
    } catch (error) {
      resultado.erros.push(`Erro ao listar webhooks: ${error}`)
      return resultado
    }
  }

  /**
   * Cadastra um novo webhook no TaxiMachine
   */
  const cadastrarWebhook = async (
    url: string,
    apiKey: string,
    authBase64: string
  ): Promise<{ success: boolean; webhookId?: string; error?: string }> => {
    try {
      const response = await fetch('https://api.taximachine.com.br/api/integracao/cadastrarWebhook', {
        method: 'POST',
        headers: {
          'User-Agent': 'ua-ubizcar',
          'api-key': apiKey,
          'Authorization': `Basic ${authBase64}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tipo: 'status',
          responsavel: 'solicitante',
          url: url
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      return {
        success: data.success || false,
        webhookId: data.webhook_id,
        error: data.error
      }
    } catch (error) {
      return {
        success: false,
        error: `${error}`
      }
    }
  }

  /**
   * Fluxo completo: limpa webhooks antigos e cadastra novo
   */
  const recadastrarWebhook = async (
    cidadeId: string,
    url: string,
    apiKey: string,
    authBase64: string
  ): Promise<{
    success: boolean
    webhookId?: string
    deletados: number
    erros: string[]
  }> => {
    // 1. Limpar webhooks status existentes
    const limpeza = await limparWebhooksStatus(cidadeId, apiKey, authBase64)

    // 2. Cadastrar novo webhook
    const cadastro = await cadastrarWebhook(url, apiKey, authBase64)

    return {
      success: cadastro.success,
      webhookId: cadastro.webhookId,
      deletados: limpeza.deletados,
      erros: [...limpeza.erros, ...(cadastro.error ? [cadastro.error] : [])]
    }
  }

  return {
    listarWebhooks,
    deletarWebhook,
    limparWebhooksStatus,
    cadastrarWebhook,
    recadastrarWebhook
  }
}
