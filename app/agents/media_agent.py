
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
import traceback

from app.agents.base_agent import BaseAgent
from app.utils.prompt_loader import load_prompt
from app.core.gsheet_connector import GoogleSheetConnector
from app.utils.data_cleaners import clean_text, clean_dataframe, limpar_numero, limpar_porcentagem
from app.utils.data_formatters import format_to_markdown_table, formatar_markdown_consolidado
from app.utils.marketing_metrics import roi, cps, tkm, conversion_rate, cpc, cpm, percent_change
from app.utils.save_json import salvar_json_kpis
from app.utils.file_utils import create_directory_if_not_exists

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MediaAgent(BaseAgent):
    """
    Agente especializado em analisar dados de mídia paga (Google Ads, Meta Ads).
    """
    def __init__(self, llm_service):
        super().__init__(llm_service)
        self.gsheet_connector = GoogleSheetConnector()
        # Mapeamento de métricas para suas funções de cálculo e suas dependências de coluna (em inglês)
        self.METRICAS_DISPONIVEIS = {
            'ROI': {'func': roi, 'deps': ['Revenue', 'Spend']},
            'CPS': {'func': cps, 'deps': ['Spend', 'Sessions']},
            'TKM': {'func': tkm, 'deps': ['Revenue', 'Conversions']},
            'Conversion_Rate': {'func': conversion_rate, 'deps': ['Conversions', 'Sessions']},
            'CPC': {'func': cpc, 'deps': ['Spend', 'Clicks']},
            'CPM': {'func': cpm, 'deps': ['Spend', 'Impressions']},
        }

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
            dict: Um dicionário contendo o relatório textual, os KPIs e os comparativos.
        """
        logger.info(f"Executando MediaAgent para {data_source} do cliente {client_name}")
        try:
            # Normaliza a lista de métricas para corresponder ao case esperado (ex: 'Revenue' em vez de 'revenue')
            normalized_metricas = []
            for m in metricas:
                # Tenta encontrar a métrica no self.METRICAS_DISPONIVEIS (que usa Title Case ou ALL CAPS)
                found = False
                for key in self.METRICAS_DISPONIVEIS.keys():
                    if m.lower() == key.lower(): # Compara de forma case-insensitive
                        normalized_metricas.append(key)
                        found = True
                        break
                if not found:
                    # Para métricas base como 'Spend', 'Revenue', etc., assume Title Case
                    normalized_metricas.append(m.title())
            metricas = normalized_metricas

            # Mapeamento de nomes de colunas da planilha (Português) para o código (Inglês)
            COLUMN_MAPPING = {
                'Data': 'Date',
                'Investimento': 'Spend',
                'Receita': 'Revenue',
                'Sessões': 'Sessions',
                'Conversões': 'Conversions',
                'Cliques': 'Clicks',
                'Impressões': 'Impressions',
                'ROI (Return Over Investiment)': 'ROI',
                'CPS (Custo por Sessão)': 'CPS',
                'TKM (Ticket Médio)': 'TKM',
                'Taxa de Conversão': 'Conversion_Rate',
            }

            # Colunas obrigatórias para qualquer plataforma de mídia (em inglês, para uso interno)
            COLUNAS_OBRIGATORIAS_BASE_EN = ['Date', 'Spend', 'Revenue', 'Sessions', 'Conversions']

            # Determina qual aba da planilha usar com base na fonte de dados
            if data_source == 'google_ads':
                sheet_tab_name = client_config.get('google_sheet_tab_name')
            elif data_source == 'meta_ads':
                sheet_tab_name = client_config.get('meta_sheet_tab_name')
            else:
                return {
                    "report": f"Fonte de dados desconhecida: {data_source}",
                    "kpis": {}, "comparatives": {}
                }

            if not sheet_tab_name:
                return {
                    "report": f"Aba da planilha para '{data_source}' não configurada para o cliente '{client_name}'.",
                    "kpis": {}, "comparatives": {}
                }

            spreadsheet_name = client_config.get("planilha_id_ou_nome")
            data = self.gsheet_connector.get_data_from_sheet(spreadsheet_name, sheet_tab_name)

            if data.empty:
                return {
                    "report": f"Não foram encontrados dados para o cliente '{client_name}' na planilha '{spreadsheet_name}' na aba '{sheet_tab_name}'.",
                    "kpis": {}, "comparatives": {}
                }

            df = data
            logger.info(f"[DEBUG MEDIA AGENT] DataFrame após extração e antes de renomear ({data_source}):\n{df.head()}\n{df.dtypes}")

            # Renomeia as colunas do DataFrame para os nomes em inglês
            reverse_column_mapping = {pt_name: en_name for pt_name, en_name in COLUMN_MAPPING.items()}
            df.rename(columns=reverse_column_mapping, inplace=True)
            logger.info(f"[DEBUG MEDIA AGENT] DataFrame após renomear colunas ({data_source}):\n{df.head()}\n{df.dtypes}")

            # Converte a coluna 'Date' para datetime
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%d/%m/%Y')
            df.dropna(subset=['Date'], inplace=True) # Remove linhas com datas inválidas

            # Converte colunas numéricas para float
            numeric_cols = [col for col in df.columns if col != 'Date']
            for col in numeric_cols:
                original_col_data = df[col].copy()
                df[col] = pd.to_numeric(df[col], errors='coerce')
                failed_conversion_mask = df[col].isna() & original_col_data.notna()
                if failed_conversion_mask.any():
                    logger.warning(f"[DEBUG MEDIA AGENT] Tentando limpar valores não numéricos na coluna '{col}' ({data_source})...")
                    df.loc[failed_conversion_mask, col] = original_col_data[failed_conversion_mask].apply(limpar_numero)
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            df = df.fillna(0)
            logger.info(f"[DEBUG MEDIA AGENT] DataFrame após conversão numérica e fillna ({data_source}):\n{df.head()}\n{df.dtypes}")

            # Calcular métricas selecionadas
            for metrica_nome in metricas:
                if metrica_nome in self.METRICAS_DISPONIVEIS:
                    func = self.METRICAS_DISPONIVEIS[metrica_nome]['func']
                    dependencies = self.METRICAS_DISPONIVEIS[metrica_nome]['deps']
                    if not all(dep_col in df.columns for dep_col in dependencies):
                        continue
                    if metrica_nome == 'ROI':
                        df['ROI'] = df.apply(lambda row: func(row['Revenue'], row['Spend']), axis=1)
                    elif metrica_nome == 'CPS':
                        df['CPS'] = df.apply(lambda row: func(row['Spend'], row['Sessions']), axis=1)
                    elif metrica_nome == 'TKM':
                        df['TKM'] = df.apply(lambda row: func(row['Revenue'], row['Conversions']), axis=1)
                    elif metrica_nome == 'Conversion_Rate':
                        df['Conversion_Rate'] = df.apply(lambda row: func(row['Conversions'], row['Sessions']), axis=1)
                    elif metrica_nome == 'CPC':
                        df['CPC'] = df.apply(lambda row: func(row['Spend'], row['Clicks']), axis=1)
                    elif metrica_nome == 'CPM':
                        df['CPM'] = df.apply(lambda row: func(row['Spend'], row['Impressions']), axis=1)

            # Filtrar dados para o mês de análise e períodos comparativos
            data_analise_dt = datetime.strptime(mes_analise, "%Y-%m-%d")
            start_current_month = data_analise_dt.replace(day=1)
            end_current_month = (start_current_month + relativedelta(months=1)) - relativedelta(days=1)
            start_prev_month = start_current_month - relativedelta(months=1)
            end_prev_month = (start_prev_month + relativedelta(months=1)) - relativedelta(days=1)
            start_yoy_month = start_current_month - relativedelta(years=1)
            end_yoy_month = (start_yoy_month + relativedelta(months=1)) - relativedelta(days=1)

            df_current = df[(df['Date'] >= start_current_month) & (df['Date'] <= end_current_month)]
            df_prev_month = df[(df['Date'] >= start_prev_month) & (df['Date'] <= end_prev_month)]
            df_yoy = df[(df['Date'] >= start_yoy_month) & (df['Date'] <= end_yoy_month)]

            # Resumo de KPIs por período
            resumo_periodos = {}
            for label, df_period in [('atual', df_current), ('mom', df_prev_month), ('yoy', df_yoy)]:
                period_kpis = {}
                if not df_period.empty:
                    # Inclui apenas as métricas base que existem no DataFrame
                    for metrica_base in [m for m in metricas if m not in self.METRICAS_DISPONIVEIS]:
                        if metrica_base in df_period.columns:
                            period_kpis[metrica_base] = df_period[metrica_base].sum()

                    # Calcula as métricas compostas selecionadas
                    temp_sum_kpis = {
                        'Spend': df_period['Spend'].sum() if 'Spend' in df_period else 0,
                        'Revenue': df_period['Revenue'].sum() if 'Revenue' in df_period else 0,
                        'Sessions': df_period['Sessions'].sum() if 'Sessions' in df_period else 0,
                        'Conversions': df_period['Conversions'].sum() if 'Conversions' in df_period else 0,
                        'Clicks': df_period['Clicks'].sum() if 'Clicks' in df_period else 0,
                        'Impressions': df_period['Impressions'].sum() if 'Impressions' in df_period else 0,
                    }
                    for metrica in [m for m in metricas if m in self.METRICAS_DISPONIVEIS]:
                        func = self.METRICAS_DISPONIVEIS[metrica]['func']
                        # Mapeia as dependências para os valores somados
                        deps_values = [temp_sum_kpis.get(dep, 0) for dep in self.METRICAS_DISPONIVEIS[metrica]['deps']]
                        period_kpis[metrica] = func(*deps_values)
                
                resumo_periodos[label] = period_kpis

            # Comparativos MoM e YoY (apenas para métricas selecionadas)
            comparativos = {}
            for metrica in metricas:
                current_val = resumo_periodos['atual'].get(metrica, 0)
                mom_val = resumo_periodos['mom'].get(metrica, 0)
                yoy_val = resumo_periodos['yoy'].get(metrica, 0)

                if mom_val is not None:
                    comparativos[f'{metrica}_MoM'] = percent_change(current_val, mom_val)
                if yoy_val is not None:
                    comparativos[f'{metrica}_YoY'] = percent_change(current_val, yoy_val)

            # Filtrar dicionários para conter apenas as métricas selecionadas
            kpis_finais = {k: v for k, v in resumo_periodos['atual'].items() if k in metricas}
            comparativos_finais = {k: v for k, v in comparativos.items()}

            # Salvar KPIs em JSON
            safe_client_name = "".join(c if c.isalnum() else "_" for c in client_name)
            safe_mes_analise = mes_analise.replace("-", "_")
            reports_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reports')
            client_report_dir = os.path.join(reports_base_dir, safe_client_name, safe_mes_analise)
            create_directory_if_not_exists(client_report_dir)
            
            # Passa apenas os dados filtrados para a função de salvar
            salvar_json_kpis(
                plataforma=data_source.replace('_', ' ').title(),
                mes_analise=mes_analise,
                resumo_periodos={'atual': kpis_finais, 'mom': resumo_periodos['mom'], 'yoy': resumo_periodos['yoy']},
                comparativos=comparativos_finais,
                pasta_saida=client_report_dir,
                sufixo_nome=data_source.replace('_', ' ').title(),
                metricas_selecionadas=metricas
            )

            # Formatação para o prompt do LLM
            markdown_parts = []
            markdown_parts.append(f"## Análise de {data_source.replace('_', ' ').title()} para {client_name} - Mês de {data_analise_dt.strftime('%B %Y')}\n\n")
            
            # Criar DataFrames apenas com as métricas selecionadas
            kpis_df = pd.DataFrame([kpis_finais])
            markdown_parts.append(formatar_markdown_consolidado(kpis_df, "KPIs do Período Atual"))

            comparativos_df = pd.DataFrame([comparativos_finais])
            markdown_parts.append(formatar_markdown_consolidado(comparativos_df, "Comparativos (MoM e YoY)"))

            # Formatar a lista de métricas para o prompt
            metrics_to_analyze_list_markdown = "\n".join([f"- {m}" for m in metricas])

            prompt_template = load_prompt('media_analysis')
            prompt = prompt_template.format(
                plataforma=data_source.replace('_', ' ').title(),
                cliente_contexto=client_config.get("contexto_cliente_prompt", ""),
                dados_markdown_summary_month_name=data_analise_dt.strftime('%B de %Y'),
                metrics_to_analyze_list_markdown=metrics_to_analyze_list_markdown,
                dados_markdown="\n".join(markdown_parts)
            )

            # Gerar o relatório usando o LLM
            report = self.llm_service.generate_text(prompt)
            
            return {
                "report": report,
                "kpis": kpis_finais,
                "comparatives": comparativos_finais
            }
        except Exception as e:
            logger.error(f"Erro no MediaAgent.run para {data_source} do cliente {client_name}: {e}")
            traceback.print_exc()
            return {
                "report": f"Erro no MediaAgent para {data_source}: {e}",
                "kpis": {},
                "comparatives": {}
            }