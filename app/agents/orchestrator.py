import logging
from datetime import datetime
import pandas as pd

from app.utils.prompt_loader import load_prompt
from app.agents.media_agent import MediaAgent
from app.core.llm_service import get_llm_service
from app.utils.file_utils import save_to_file, get_report_path
from app.core.connectors.google_sheets_connector import GoogleSheetsConnector
from app.utils.data_formatters import formatar_markdown_consolidado

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Orchestrator:
    """
    Agente orquestrador que interpreta a tarefa do usuário e
    aciona o agente apropriado para executá-la.
    """
    def __init__(self, llm_service):
        self.llm_service = llm_service
        data_connector = GoogleSheetsConnector()
        self.media_agent = MediaAgent(llm_service, data_connector=data_connector)

    def executar_fluxo_analise_cliente(self, cliente_config: dict, mes_analise_atual_str: str, metricas_selecionadas: list):
        """
        Executa o fluxo de análise de mídia para um cliente específico.
        """
        client_name = cliente_config.get("nome_exibicao", "Cliente Desconhecido")

        google_results = None
        meta_results = None

        try:
            google_results = self.media_agent.run(
                data_source='google_ads',
                client_name=client_name,
                client_config=cliente_config,
                mes_analise=mes_analise_atual_str,
                metricas=metricas_selecionadas
            )
        except Exception as e:
            logger.error(f"Erro ao executar MediaAgent para Google Ads: {e}", exc_info=True)
            google_results = {"report": "Erro ao gerar relatório do Google Ads.", "kpis": {}, "comparatives": {}}

        try:
            meta_results = self.media_agent.run(
                data_source='meta_ads',
                client_name=client_name,
                client_config=cliente_config,
                mes_analise=mes_analise_atual_str,
                metricas=metricas_selecionadas
            )
        except Exception as e:
            logger.error(f"Erro ao executar MediaAgent para Meta Ads: {e}", exc_info=True)
            meta_results = {"report": "Erro ao gerar relatório do Meta Ads.", "kpis": {}, "comparatives": {}}

        final_report = "Erro ao gerar relatório consolidado."
        try:
            consolidated_prompt_template = load_prompt('consolidated_report')

            all_platforms_reports_text = []
            if google_results and google_results.get('report'):
                all_platforms_reports_text.append(f"### Análise Detalhada do Google Ads\n\n{google_results['report']}")
            if meta_results and meta_results.get('report'):
                all_platforms_reports_text.append(f"### Análise Detalhada do Meta Ads\n\n{meta_results['report']}")
            
            all_platforms_reports_markdown = "\n\n".join(all_platforms_reports_text) if all_platforms_reports_text else "Nenhuma análise de plataforma disponível."

            kpis_data = {
                'Google Ads': google_results.get('kpis', {}),
                'Meta Ads': meta_results.get('kpis', {})
            }
            kpis_df = pd.DataFrame(kpis_data).T.fillna(0)
            kpis_markdown = formatar_markdown_consolidado(kpis_df, "Resumo de KPIs Consolidados")

            comparatives_data = {
                'Google Ads': google_results.get('comparatives', {}),
                'Meta Ads': meta_results.get('comparatives', {})
            }
            comparatives_df = pd.DataFrame(comparatives_data).T.fillna(0)
            comparatives_markdown = formatar_markdown_consolidado(comparatives_df, "Resumo de Comparativos Consolidados (MoM & YoY)")

            prompt = consolidated_prompt_template.format(
                client_name=client_name,
                mes_analise=datetime.strptime(mes_analise_atual_str, "%Y-%m-%d").strftime('%B de %Y'),
                kpis_consolidated_markdown=kpis_markdown,
                comparatives_consolidates_markdown=comparatives_markdown,
                all_platforms_reports=all_platforms_reports_markdown
            )
            
            final_report = self.llm_service.generate_text(prompt)

        except Exception as e:
            logger.error(f"Erro ao gerar relatório consolidado com LLM: {e}", exc_info=True)

        file_path = get_report_path(client_name, mes_analise_atual_str, file_type="consolidated")
        try:
            save_to_file(file_path, final_report)
        except Exception as e:
            logger.error(f"Erro ao salvar relatório final: {e}", exc_info=True)
            return "Erro ao salvar relatório final."

        return file_path

def get_orchestrator():
    """
    Função factory para criar uma instância do Orchestrator.
    """
    llm_service = get_llm_service()
    return Orchestrator(llm_service)