import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, GET, DELETE, OPTIONS',
};

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const url = new URL(req.url);
    const action = url.searchParams.get('action');
    const cidadeId = url.searchParams.get('cidade_id');
    const webhookId = url.searchParams.get('webhook_id');

    if (!action || !cidadeId) {
      return new Response(
        JSON.stringify({ error: 'Parâmetros action e cidade_id são obrigatórios' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    const { data: cidade, error: cidadeError } = await supabase
      .from('cidades')
      .select('id, nome, taximachine_api_key, taximachine_auth_base64')
      .eq('id', cidadeId)
      .single();

    if (cidadeError || !cidade) {
      return new Response(
        JSON.stringify({ error: 'Cidade não encontrada' }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    if (!cidade.taximachine_api_key || !cidade.taximachine_auth_base64) {
      return new Response(
        JSON.stringify({ 
          error: 'Credenciais TaxiMachine não configuradas',
          needs_credentials: true 
        }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const headers = {
      'User-Agent': 'ua-ubizcar',
      'api-key': cidade.taximachine_api_key,
      'Authorization': `Basic ${cidade.taximachine_auth_base64}`,
      'Content-Type': 'application/json'
    };

    let response;
    let result;

    switch (action) {
      case 'listar':
        response = await fetch('https://api.taximachine.com.br/api/integracao/listarWebhook', {
          method: 'GET',
          headers
        });
        result = await response.json();
        
        return new Response(
          JSON.stringify({
            success: true,
            data: result,
            cidade: cidade.nome
          }),
          { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );

      case 'deletar':
        if (!webhookId) {
          return new Response(
            JSON.stringify({ error: 'webhook_id é obrigatório para deletar' }),
            { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
          );
        }

        response = await fetch(
          `https://api.taximachine.com.br/api/integracao/deletarWebhook/${webhookId}`,
          {
            method: 'DELETE',
            headers
          }
        );
        result = await response.json();

        return new Response(
          JSON.stringify({
            success: result.success || false,
            message: result.message,
            cidade: cidade.nome
          }),
          { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );

      case 'cadastrar':
        const webhookUrl = `${supabaseUrl}/functions/v1/webhook-cidade/${cidade.id}`;
        
        response = await fetch('https://api.taximachine.com.br/api/integracao/cadastrarWebhook', {
          method: 'POST',
          headers,
          body: JSON.stringify({
            tipo: 'status',
            responsavel: 'solicitante',
            url: webhookUrl
          })
        });
        result = await response.json();

        if (result.success) {
          await supabase
            .from('cidades')
            .update({
              webhook_url: webhookUrl,
              webhook_ativo: true,
              webhook_id: result.webhook_id || null,
              updated_at: new Date().toISOString()
            })
            .eq('id', cidade.id);
        }

        return new Response(
          JSON.stringify({
            success: result.success || false,
            webhook_url: webhookUrl,
            webhook_id: result.webhook_id,
            error: result.error,
            cidade: cidade.nome
          }),
          { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );

      default:
        return new Response(
          JSON.stringify({ error: `Ação '${action}' não suportada` }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
    }

  } catch (err) {
    console.error('Erro no webhook manager:', err);
    return new Response(
      JSON.stringify({ 
        success: false, 
        error: err.message || 'Erro interno do servidor' 
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
