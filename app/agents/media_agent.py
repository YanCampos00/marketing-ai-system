from app.agents.base_agent import BaseAgent
from app.utils.prompt_loader import load_prompt
from app.core.gsheet_connector import GoogleSheetConnector
import pandas as pd

class MediaAgent(BaseAgent):
    """
    Agente especializado em analisar dados de mídia paga (Google Ads, Meta Ads).
    """
    def __init__(self, llm_service):
        super().__init__(llm_service)
        self.gsheet_connector = GoogleSheetConnector()

    def run(self, data_source: str, client_name: str, client_config: dict, mes_analise: str, metricas: list):
        """
        Executa a análise de dados de mídia.

        Args:
            data_source (str): A fonte dos dados ('google_ads' ou 'meta_ads').
            client_name (str): O nome de exibição do cliente.
            client_config (dict): A configuração completa do cliente do banco de dados.
            mes_analise (str): O mês da análise no formato 'AAAA-MM-DD'.
            metricas (list): Lista de métricas selecionadas pelo usuário.

        Returns:
            str: O relatório de análise gerado pelo LLM.
        """
        # Determina qual aba da planilha usar com base na fonte de dados
        if data_source == 'google_ads':
            sheet_tab_name = client_config.get('google_sheet_tab_name')
        elif data_source == 'meta_ads':
            sheet_tab_name = client_config.get('meta_sheet_tab_name')
        else:
            return f"Fonte de dados desconhecida: {data_source}"

        if not sheet_tab_name:
            return f"Aba da planilha para '{data_source}' não configurada para o cliente '{client_name}'."

        # Carregar dados da planilha
        spreadsheet_name = client_config.get("planilha_id_ou_nome")
        data = self.gsheet_connector.get_data_from_sheet(spreadsheet_name, sheet_tab_name)
        
        if not data:
            return f"Não foram encontrados dados para o cliente '{client_name}' na planilha '{spreadsheet_name}' na aba '{sheet_tab_name}'."

        df = pd.DataFrame(data[1:], columns=data[0])

        # TODO: Adicionar a lógica de filtragem por mês (mes_analise) e cálculo de métricas (metricas)
        # Esta é uma simplificação. A lógica completa de cálculo de período e métricas precisa ser portada aqui.

        # Carregar o prompt específico para a análise
        prompt_template = load_prompt('media_analysis')
        
        # Formatar o prompt com os dados
        prompt = prompt_template.format(
            data_source=data_source.replace('_', ' ').title(),
            client_name=client_name,
            data=df.to_string() # Simplificado: enviando o DataFrame inteiro como string
        )

        # Gerar o relatório usando o LLM
        report = self.llm_service.generate_text(prompt)
        return report