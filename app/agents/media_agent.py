import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
import traceback
from typing import List, Dict, Any

from app.agents.base_agent import BaseAgent
from app.utils.prompt_loader import load_prompt
from app.core.connectors.base_connector import BaseConnector
from app.utils.data_cleaners import limpar_numero
from app.utils.data_formatters import formatar_markdown_consolidado
from app.utils.marketing_metrics import roi, cps, tkm, conversion_rate, cpc, cpm, percent_change
from app.utils.save_json import salvar_json_kpis
from app.utils.file_utils import create_directory_if_not_exists

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MediaAgent(BaseAgent):
    """
    Agente especializado em analisar dados de mídia paga (Google Ads, Meta Ads).
    """
    def __init__(self, llm_service, data_connector: BaseConnector):
        super().__init__(llm_service)
        self.data_connector = data_connector
        self.METRICAS_DISPONIVEIS = {
            'ROI': {'func': roi, 'deps': ['Revenue', 'Spend']},
            'CPS': {'func': cps, 'deps': ['Spend', 'Sessions']},
            'TKM': {'func': tkm, 'deps': ['Revenue', 'Conversions']},
            'Conversion_Rate': {'func': conversion_rate, 'deps': ['Conversions', 'Sessions']},
            'CPC': {'func': cpc, 'deps': ['Spend', 'Clicks']},
            'CPM': {'func': cpm, 'deps': ['Spend', 'Impressions']},
        }
        self.COLUMN_MAPPING = {
            'Data': 'Date', 'Investimento': 'Spend', 'Receita': 'Revenue',
            'Sessões': 'Sessions', 'Conversões': 'Conversions', 'Cliques': 'Clicks',
            'Impressões': 'Impressions', 'ROI (Return Over Investiment)': 'ROI',
            'CPS (Custo por Sessão)': 'CPS', 'TKM (Ticket Médio)': 'TKM',
            'Taxa de Conversão': 'Conversion_Rate',
        }

    def _normalize_metrics(self, metricas: List[str]) -> List[str]:
        """Normaliza a lista de métricas para corresponder ao case esperado."""
        normalized = []
        for m in metricas:
            found = False
            for key in self.METRICAS_DISPONIVEIS.keys():
                if m.lower() == key.lower():
                    normalized.append(key)
                    found = True
                    break
            if not found:
                normalized.append(m.title())
        return normalized

    def _fetch_and_clean_data(self, data_source: str, client_config: dict, mes_analise: str) -> pd.DataFrame:
        """Busca e limpa os dados da fonte especificada."""
        data = self.data_connector.get_data(
            data_source=data_source, client_config=client_config, mes_analise=mes_analise
        )
        if data.empty:
            return pd.DataFrame()

        df = data
        logger.debug(f"DataFrame após extração ({data_source}):\n{df.head()}")
        
        df.rename(columns={pt: en for pt, en in self.COLUMN_MAPPING.items()}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%d/%m/%Y')
        df.dropna(subset=['Date'], inplace=True)

        numeric_cols = [col for col in df.columns if col != 'Date']
        for col in numeric_cols:
            original_col = df[col].copy()
            df[col] = pd.to_numeric(df[col], errors='coerce')
            failed_mask = df[col].isna() & original_col.notna()
            if failed_mask.any():
                logger.debug(f"Limpando valores não numéricos na coluna '{col}'...")
                df.loc[failed_mask, col] = original_col[failed_mask].apply(limpar_numero)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.fillna(0)
        logger.debug(f"DataFrame após limpeza ({data_source}):\n{df.head()}\n{df.dtypes}")
        return df

    def _calculate_metrics(self, df: pd.DataFrame, metricas: List[str]) -> pd.DataFrame:
        """Calcula as métricas selecionadas e as adiciona ao DataFrame."""
        for metrica_nome in metricas:
            if metrica_nome in self.METRICAS_DISPONIVEIS:
                config = self.METRICAS_DISPONIVEIS[metrica_nome]
                if not all(dep in df.columns for dep in config['deps']):
                    continue
                
                # Usar apply com lambda para passar as colunas corretas para cada função
                df[metrica_nome] = df.apply(
                    lambda row: config['func'](*(row[dep] for dep in config['deps'])), 
                    axis=1
                )
        return df

    def _summarize_and_compare(self, df: pd.DataFrame, mes_analise: str, metricas: List[str]) -> Dict[str, Any]:
        """Filtra os dados por período e calcula os KPIs e comparativos."""
        data_analise_dt = datetime.strptime(mes_analise, "%Y-%m-%d")
        start_current = data_analise_dt.replace(day=1)
        end_current = (start_current + relativedelta(months=1)) - relativedelta(days=1)
        start_prev = start_current - relativedelta(months=1)
        end_prev = (start_prev + relativedelta(months=1)) - relativedelta(days=1)
        start_yoy = start_current - relativedelta(years=1)
        end_yoy = (start_yoy + relativedelta(months=1)) - relativedelta(days=1)

        periods = {
            'atual': df[(df['Date'] >= start_current) & (df['Date'] <= end_current)],
            'mom': df[(df['Date'] >= start_prev) & (df['Date'] <= end_prev)],
            'yoy': df[(df['Date'] >= start_yoy) & (df['Date'] <= end_yoy)],
        }

        resumo_periodos = {}
        for label, period_df in periods.items():
            kpis = {}
            if not period_df.empty:
                base_metrics_sum = {m: period_df[m].sum() for m in metricas if m not in self.METRICAS_DISPONIVEIS and m in period_df}
                kpis.update(base_metrics_sum)
                
                # Recalcula métricas compostas com base nos totais do período
                deps_sum = {dep: period_df[dep].sum() for dep in ['Spend', 'Revenue', 'Sessions', 'Conversions', 'Clicks', 'Impressions'] if dep in period_df}
                for metrica in [m for m in metricas if m in self.METRICAS_DISPONIVEIS]:
                    config = self.METRICAS_DISPONIVEIS[metrica]
                    deps_values = [deps_sum.get(dep, 0) for dep in config['deps']]
                    kpis[metrica] = config['func'](*deps_values)
            resumo_periodos[label] = kpis

        comparativos = {}
        for metrica in metricas:
            current_val = resumo_periodos['atual'].get(metrica, 0)
            mom_val = resumo_periodos['mom'].get(metrica, 0)
            yoy_val = resumo_periodos['yoy'].get(metrica, 0)
            comparativos[f'{metrica}_MoM'] = percent_change(current_val, mom_val)
            comparativos[f'{metrica}_YoY'] = percent_change(current_val, yoy_val)

        kpis_finais = {k: v for k, v in resumo_periodos['atual'].items() if k in metricas}
        return {"kpis": kpis_finais, "comparatives": comparativos, "resumo_periodos": resumo_periodos}

    def _prepare_llm_prompt(self, data_source: str, client_name: str, client_config: dict, mes_analise: str, metricas: List[str], kpis: Dict, comparatives: Dict) -> str:
        """Prepara o prompt final para ser enviado ao LLM."""
        data_analise_dt = datetime.strptime(mes_analise, "%Y-%m-%d")
        markdown_parts = [f"## Análise de {data_source.replace('_', ' ').title()} para {client_name} - Mês de {data_analise_dt.strftime('%B %Y')}\n"]
        
        kpis_df = pd.DataFrame([kpis])
        markdown_parts.append(formatar_markdown_consolidado(kpis_df, "KPIs do Período Atual"))

        comparatives_df = pd.DataFrame([comparatives])
        markdown_parts.append(formatar_markdown_consolidado(comparatives_df, "Comparativos (MoM e YoY)"))

        metrics_list_md = "\n".join([f"- {m}" for m in metricas])
        prompt_template = load_prompt('media_analysis')
        
        return prompt_template.format(
            plataforma=data_source.replace('_', ' ').title(),
            cliente_contexto=client_config.get("contexto_cliente_prompt", ""),
            dados_markdown_summary_month_name=data_analise_dt.strftime('%B de %Y'),
            metrics_to_analyze_list_markdown=metrics_list_md,
            dados_markdown="\n".join(markdown_parts)
        )

    def run(self, data_source: str, client_name: str, client_config: dict, mes_analise: str, metricas: list):
        """
        Executa o fluxo de análise de dados de mídia orquestrando os métodos privados.
        """
        logger.info(f"Executando MediaAgent para {data_source} do cliente {client_name}")
        try:
            # 1. Normalizar e Preparar
            metricas_norm = self._normalize_metrics(metricas)

            # 2. Buscar e Limpar Dados
            df = self._fetch_and_clean_data(data_source, client_config, mes_analise)
            if df.empty:
                return {"report": f"Não foram encontrados dados para {client_name} em {data_source}.", "kpis": {}, "comparatives": {}}

            # 3. Calcular Métricas
            df_com_metricas = self._calculate_metrics(df, metricas_norm)

            # 4. Resumir e Comparar
            analysis_results = self._summarize_and_compare(df_com_metricas, mes_analise, metricas_norm)
            kpis_finais = analysis_results["kpis"]
            comparativos_finais = analysis_results["comparatives"]

            # 5. Salvar Artefatos (KPIs em JSON)
            safe_client_name = "".join(c if c.isalnum() else "_" for c in client_name)
            safe_mes_analise = mes_analise.replace("-", "_")
            client_report_dir = os.path.join('app', 'reports', safe_client_name, safe_mes_analise)
            create_directory_if_not_exists(client_report_dir)
            salvar_json_kpis(
                plataforma=data_source.replace('_', ' ').title(),
                mes_analise=mes_analise,
                resumo_periodos=analysis_results["resumo_periodos"],
                comparativos=comparativos_finais,
                pasta_saida=client_report_dir,
                sufixo_nome=data_source.replace('_', ' ').title(),
                metricas_selecionadas=metricas_norm
            )

            # 6. Preparar Prompt e Gerar Relatório
            prompt = self._prepare_llm_prompt(data_source, client_name, client_config, mes_analise, metricas_norm, kpis_finais, comparativos_finais)
            report = self.llm_service.generate_text(prompt)
            
            return {"report": report, "kpis": kpis_finais, "comparatives": comparativos_finais}

        except Exception as e:
            logger.error(f"Erro no MediaAgent.run para {data_source} do cliente {client_name}: {e}")
            traceback.print_exc()
            return {"report": f"Erro no MediaAgent para {data_source}: {e}", "kpis": {}, "comparatives": {}}