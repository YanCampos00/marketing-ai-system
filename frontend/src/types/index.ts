export interface Client {
  id: string;
  nome_exibicao: string;
  contexto_cliente_prompt: string;
  planilha_id_ou_nome: string;
  google_sheet_tab_name?: string;
  meta_sheet_tab_name?: string;
}

export interface AnalysisRequest {
  client_id: string;
  mes_analise: string; // Formato YYYY-MM-DD
  metricas_selecionadas: string[];
}