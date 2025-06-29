
from app.agents.base_agent import BaseAgent
from app.utils.prompt_loader import load_prompt
from app.agents.media_agent import MediaAgent
from app.core.llm_service import get_llm_service

class Orchestrator(BaseAgent):
    """
    Agente orquestrador que interpreta a tarefa do usuário e
    aciona o agente apropriado para executá-la.
    """
    def __init__(self, llm_service):
        super().__init__(llm_service)
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
        
        # 1. Análise do Google Ads
        google_report = self.media_agent.run(
            data_source='google_ads',
            client_name=client_name,
            client_config=cliente_config,
            mes_analise=mes_analise_atual_str,
            metricas=metricas_selecionadas
        )

        # 2. Análise do Meta Ads
        meta_report = self.media_agent.run(
            data_source='meta_ads',
            client_name=client_name,
            client_config=cliente_config,
            mes_analise=mes_analise_atual_str,
            metricas=metricas_selecionadas
        )

        # 3. Consolidação e Relatório Final
        # Carrega o prompt para o relatório consolidado
        consolidated_prompt_template = load_prompt('consolidated_report') # Novo prompt necessário

        prompt = consolidated_prompt_template.format(
            client_name=client_name,
            mes_analise=mes_analise_atual_str,
            google_ads_report=google_report,
            meta_ads_report=meta_report
        )

        # Gera o relatório final usando o LLM
        final_report = self.llm_service.generate_text(prompt)

        # TODO: Salvar o `final_report` em um arquivo e retornar o caminho
        # Por enquanto, vamos apenas retornar o conteúdo.
        print(f"Relatório Final Gerado para {client_name}:
{final_report}")

        # Esta parte precisa ser implementada para salvar o arquivo e retornar o caminho
        # conforme esperado pelo main.py
        return final_report # Retorno temporário

# Função para ser usada no startup do FastAPI
def get_orchestrator():
    """
    Função factory para criar uma instância do Orchestrator.
    """
    llm_service = get_llm_service()
    return Orchestrator(llm_service)
