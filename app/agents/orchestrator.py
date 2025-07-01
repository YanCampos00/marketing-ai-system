import os
from datetime import datetime
import logging
import traceback
import pandas as pd
from app.utils.data_formatters import formatar_markdown_consolidado

from app.utils.prompt_loader import load_prompt
from app.agents.media_agent import MediaAgent
from app.core.llm_service import get_llm_service
from app.utils.file_utils import save_to_file, create_directory_if_not_exists

PASTA_RELATORIOS_BASE = "reports"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Orchestrator:
    """
    Agente orquestrador que interpreta a tarefa do usuário e
    aciona o agente apropriado para executá-la.
    """
    def __init__(self, llm_service):
        self.llm_service = llm_service
        # Inicializa os agentes especializados
        self.media_agent = MediaAgent(llm_service)

    def executar_fluxo_analise_cliente(self, cliente_config: dict, mes_analise_atual_str: str, metricas_selecionadas: list):
        """
        Executa o fluxo de análise de mídia para um cliente específico.
        Esta função é o ponto de entrada chamado pela API em main.py.

        Args:
            cliente_config (dict): Dicionário com a configuração do cliente (nome, planilha, etc.).
            mes_analise_atual_str (str): O mês da análise no formato 'AAAA-MM-DD'.
            metricas_selecionadas (list): Lista de métricas a serem analisadas.

        Returns:
            str: O caminho para o relatório final gerado.
        """
        client_name = cliente_config.get("nome_exibicao", "Cliente Desconhecido")
        logger.info(f"Iniciando análise para cliente: {client_name}, mês: {mes_analise_atual_str}")

        # Dicionários para armazenar os resultados completos dos agentes
        google_results = None
        meta_results = None

        try:
            # 1. Análise do Google Ads
            google_results = self.media_agent.run(
                data_source='google_ads',
                client_name=client_name,
                client_config=cliente_config,
                mes_analise=mes_analise_atual_str,
                metricas=metricas_selecionadas
            )
        except Exception as e:
            logger.error(f"Erro ao executar MediaAgent para Google Ads: {e}")
            traceback.print_exc()
            google_results = {"report": "Erro ao gerar relatório do Google Ads.", "kpis": {}, "comparatives": {}}

        try:
            # 2. Análise do Meta Ads
            meta_results = self.media_agent.run(
                data_source='meta_ads',
                client_name=client_name,
                client_config=cliente_config,
                mes_analise=mes_analise_atual_str,
                metricas=metricas_selecionadas
            )
        except Exception as e:
            logger.error(f"Erro ao executar MediaAgent para Meta Ads: {e}")
            traceback.print_exc()
            meta_results = {"report": "Erro ao gerar relatório do Meta Ads.", "kpis": {}, "comparatives": {}}

        final_report = "Erro ao gerar relatório consolidado."
        try:
            # 3. Consolidação e Relatório Final
            consolidated_prompt_template = load_prompt('consolidated_report')

            # Extrair relatórios textuais
            google_ads_report_text = google_results.get('report', 'N/A')
            meta_ads_report_text = meta_results.get('report', 'N/A')

            # Consolidar KPIs
            kpis_data = {
                'Google Ads': google_results.get('kpis', {}),
                'Meta Ads': meta_results.get('kpis', {})
            }
            kpis_df = pd.DataFrame(kpis_data).T.fillna(0) # Transpor para ter plataformas como linhas
            kpis_markdown = formatar_markdown_consolidado(kpis_df, "Resumo de KPIs Consolidados")

            # Consolidar Comparativos
            comparatives_data = {
                'Google Ads': google_results.get('comparatives', {}),
                'Meta Ads': meta_results.get('comparatives', {})
            }
            comparatives_df = pd.DataFrame(comparatives_data).T.fillna(0)
            comparatives_markdown = formatar_markdown_consolidado(comparatives_df, "Resumo de Comparativos Consolidados (MoM & YoY)")

            # Formatar o prompt final
            prompt = consolidated_prompt_template.format(
                client_name=client_name,
                mes_analise=datetime.strptime(mes_analise_atual_str, "%Y-%m-%d").strftime('%B de %Y'),
                google_ads_report=google_ads_report_text,
                meta_ads_report=meta_ads_report_text,
                kpis_consolidated_markdown=kpis_markdown,
                comparatives_consolidated_markdown=comparatives_markdown
            )

            final_report = self.llm_service.generate_text(prompt)
        except Exception as e:
            logger.error(f"Erro ao gerar relatório consolidado com LLM: {e}")
            traceback.print_exc()

        # Salvar o relatório final
        safe_client_name = "".join(c if c.isalnum() else "_" for c in client_name)
        safe_mes_analise = mes_analise_atual_str.replace("-", "_")
        reports_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', PASTA_RELATORIOS_BASE)
        client_report_dir = os.path.join(reports_base_dir, safe_client_name, safe_mes_analise)
        create_directory_if_not_exists(client_report_dir)
        file_name = f"{safe_client_name}_relatorio_consolidado_{safe_mes_analise}.txt"
        file_path = os.path.join(client_report_dir, file_name)

        try:
            save_to_file(file_path, final_report)
            logger.info(f"Relatório final salvo em: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Erro ao salvar relatório final: {e}")
            traceback.print_exc()
            return "Erro ao salvar relatório final."

# Função para ser usada no startup do FastAPI
def get_orchestrator():
    """
    Função factory para criar uma instância do Orchestrator.
    """
    llm_service = get_llm_service()
    return Orchestrator(llm_service)