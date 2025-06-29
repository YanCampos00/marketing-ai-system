import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import traceback

from app.utils.data_cleaners import limpar_numero, limpar_porcentagem
from app.utils.data_formatters import formatar_markdown_consolidado
from app.utils.marketing_metrics import roi, cps, tkm, conversion_rate, cpc, cpm, percent_change
from app.utils.file_utils import gerar_caminho_kpis_json, save_to_file
from app.utils.custom_exceptions import (
    PlanilhaNaoEncontradaError, 
    AbaNaoEncontradaError, 
    ColunaNaoEncontradaError, 
    ErroLeituraDadosError,
    FormatoDataInvalidoError,
    ErroProcessamentoDadosAgente
)
from app.core.gsheet_connector import extrair_dados_base
from app.config.config_loader import carregar_config_global
from app.utils.prompt_loader import carregar_prompt_de_arquivo

# Carrega o prompt do agente de mídia
PROMPT_FILE_PATH_MEDIA = "app/config/prompts/media_agent_prompt.txt"
media_instructions_template = carregar_prompt_de_arquivo(PROMPT_FILE_PATH_MEDIA)

if media_instructions_template is None:
    print("ERRO CRÍTICO: Template de instruções do Agente de Mídia não pôde ser carregado. A aplicação pode não funcionar corretamente.")
    media_instructions_template = "ERRO DE CARREGAMENTO DE PROMPT - MEDIA"

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

# Mapeamento de métricas para suas funções de cálculo e suas dependências de coluna (em inglês)
METRICAS_DISPONIVEIS = {
    'ROI': {'func': roi, 'deps': ['Revenue', 'Spend']},
    'CPS': {'func': cps, 'deps': ['Spend', 'Sessions']},
    'TKM': {'func': tkm, 'deps': ['Revenue', 'Conversions']},
    'Conversion_Rate': {'func': conversion_rate, 'deps': ['Conversions', 'Sessions']},
    'CPC': {'func': cpc, 'deps': ['Spend', 'Clicks']},
    'CPM': {'func': cpm, 'deps': ['Spend', 'Impressions']},
}

def get_media_data_tool(gspread_client, tool_input_params, str_mes_analise_atual):
    """
    Extrai, processa e formatar dados de uma plataforma de mídia específica.
    tool_input_params deve ser um dicionário contendo:
    - 'plataforma': Nome da plataforma (ex: 'Google Ads', 'Meta Ads')
    - 'nome_planilha': Nome da planilha no Google Sheets
    - 'nome_aba': Nome da aba na planilha
    - 'colunas_extras': Lista de colunas adicionais específicas da plataforma (ex: ['Clicks', 'Impressions'])
    - 'metricas_selecionadas': Lista de strings com os nomes das métricas a serem calculadas (ex: ['ROI', 'CPC'])
    """
    plataforma = tool_input_params.get('plataforma')
    nome_planilha = tool_input_params.get('nome_planilha')
    nome_aba = tool_input_params.get('nome_aba')
    colunas_extras_en = tool_input_params.get('colunas_extras', []) # Colunas extras já em inglês
    # Usa as métricas selecionadas passadas, ou todas as disponíveis como fallback
    metricas_selecionadas = tool_input_params.get('metricas_selecionadas', list(METRICAS_DISPONIVEIS.keys()))

    # Constrói a lista de colunas necessárias em inglês
    colunas_necessarias_en = COLUNAS_OBRIGATORIAS_BASE_EN.copy()
    for metrica_nome in metricas_selecionadas:
        if metrica_nome in METRICAS_DISPONIVEIS:
            for dep_col in METRICAS_DISPONIVEIS[metrica_nome]['deps']:
                if dep_col not in colunas_necessarias_en:
                    colunas_necessarias_en.append(dep_col)
    
    for col in colunas_extras_en:
        if col not in colunas_necessarias_en:
            colunas_necessarias_en.append(col)

    # Mapeia as colunas necessárias para o português para extrair da planilha
    colunas_necessarias_pt = [pt_name for pt_name, en_name in COLUMN_MAPPING.items() if en_name in colunas_necessarias_en]
    # Adiciona colunas extras que não estão no mapeamento padrão (se houver)
    for col_en in colunas_extras_en:
        if col_en not in COLUMN_MAPPING.values():
            # Se a coluna extra não está no mapeamento, assume que o nome da planilha é o mesmo
            colunas_necessarias_pt.append(col_en)

    try:
        print(f"Agente de Mídia ({plataforma}): Acessando planilha '{nome_planilha}', aba '{nome_aba}'...")
        df_full = extrair_dados_base(
            gspread_client,
            nome_planilha,
            nome_aba,
            colunas_necessarias=colunas_necessarias_pt,
            formato_data='%d/%m/%Y'
        )

        # Renomeia as colunas do DataFrame para os nomes em inglês
        # Cria um dicionário de mapeamento inverso para renomear
        reverse_column_mapping = {pt_name: en_name for pt_name, en_name in COLUMN_MAPPING.items()}
        df_full.rename(columns=reverse_column_mapping, inplace=True)
        print(f"[DEBUG MEDIA AGENT] DataFrame após renomear colunas ({plataforma}):\n{df_full.head()}")

        # Converter colunas numéricas para tipo float, tratando erros
        numeric_cols = [col for col in colunas_necessarias_en if col != 'Date']
        for col in numeric_cols:
            if col in df_full.columns:
                df_full[col] = pd.to_numeric(df_full[col], errors='coerce')
        
        # Preencher NaNs com 0 após a conversão, para evitar erros em cálculos
        df_full = df_full.fillna(0)
        print(f"[DEBUG MEDIA AGENT] DataFrame após conversão numérica e fillna ({plataforma}):\n{df_full.head()}")

        # Calcular métricas selecionadas
        for metrica_nome in metricas_selecionadas:
            if metrica_nome in METRICAS_DISPONIVEIS:
                func = METRICAS_DISPONIVEIS[metrica_nome]['func']
                dependencies = METRICAS_DISPONIVEIS[metrica_nome]['deps']
                
                # Verifica se as colunas de dependência existem no DataFrame
                if not all(dep_col in df_full.columns for dep_col in dependencies):
                    print(f"Aviso: Métrica '{metrica_nome}' não calculada para {plataforma} devido à falta de colunas: {dependencies}")
                    continue # Pula para a próxima métrica

                if metrica_nome == 'ROI':
                    df_full['ROI'] = df_full.apply(lambda row: func(row['Revenue'], row['Spend']), axis=1)
                elif metrica_nome == 'CPS':
                    df_full['CPS'] = df_full.apply(lambda row: func(row['Spend'], row['Sessions']), axis=1)
                elif metrica_nome == 'TKM':
                    df_full['TKM'] = df_full.apply(lambda row: func(row['Revenue'], row['Conversions']), axis=1)
                elif metrica_nome == 'Conversion_Rate':
                    df_full['Conversion_Rate'] = df_full.apply(lambda row: func(row['Conversions'], row['Sessions']), axis=1)
                elif metrica_nome == 'CPC': # Depende de Clicks
                    df_full['CPC'] = df_full.apply(lambda row: func(row['Spend'], row['Clicks']), axis=1)
                elif metrica_nome == 'CPM': # Depende de Impressions
                    df_full['CPM'] = df_full.apply(lambda row: func(row['Spend'], row['Impressions']), axis=1)
        print(f"[DEBUG MEDIA AGENT] DataFrame após cálculo de métricas ({plataforma}):\n{df_full.head()}")

        try:
            data_analise_dt = datetime.strptime(str_mes_analise_atual, "%Y-%m-%d")
        except ValueError:
            raise FormatoDataInvalidoError(f"Formato de 'str_mes_analise_atual' ('{str_mes_analise_atual}') inválido para {plataforma}. Use AAAA-MM-DD.")
        
        start_current_month = data_analise_dt.replace(day=1)
        end_current_month = (start_current_month + relativedelta(months=1)) - relativedelta(days=1)
        start_prev_month = start_current_month - relativedelta(months=1)
        end_prev_month = (start_prev_month + relativedelta(months=1)) - relativedelta(days=1)
        start_yoy_month = start_current_month - relativedelta(years=1)
        end_yoy_month = (start_yoy_month + relativedelta(months=1)) - relativedelta(days=1)

        df_current = df_full[(df_full['Date'] >= start_current_month) & (df_full['Date'] <= end_current_month)]
        df_prev_month = df_full[(df_full['Date'] >= start_prev_month) & (df_full['Date'] <= end_prev_month)]
        df_yoy = df_full[(df_full['Date'] >= start_yoy_month) & (df_full['Date'] <= end_yoy_month)]
        
        resumo_periodos = {}
        for label, df_period in [
            ('atual', df_current), 
            ('mom', df_prev_month), 
            ('yoy', df_yoy)
        ]:
            spend_total = df_period['Spend'].sum()
            revenue_total = df_period['Revenue'].sum()
            sessions_total = df_period['Sessions'].sum()
            conversions_total = df_period['Conversions'].sum()
            clicks_total = df_period['Clicks'].sum() if 'Clicks' in df_period.columns else 0
            impressions_total = df_period['Impressions'].sum() if 'Impressions' in df_period.columns else 0

            period_kpis = {
                'Spend': spend_total,
                'Revenue': revenue_total,
                'Sessions': sessions_total,
                'Conversions': conversions_total,
            }
            for metrica_nome in metricas_selecionadas:
                if metrica_nome in METRICAS_DISPONIVEIS:
                    dependencies = METRICAS_DISPONIVEIS[metrica_nome]['deps']
                    if not all(dep_col in df_period.columns for dep_col in dependencies):
                        continue # Pula se as dependências não existirem no df_period

                    func = METRICAS_DISPONIVEIS[metrica_nome]['func']
                    if metrica_nome == 'ROI':
                        period_kpis['ROI'] = func(revenue_total, spend_total)
                    elif metrica_nome == 'CPS':
                        period_kpis['CPS'] = func(spend_total, sessions_total)
                    elif metrica_nome == 'TKM':
                        period_kpis['TKM'] = func(revenue_total, conversions_total)
                    elif metrica_nome == 'Conversion_Rate':
                        period_kpis['Conversion_Rate'] = func(conversions_total, sessions_total)
                    elif metrica_nome == 'CPC':
                        period_kpis['CPC'] = func(spend_total, clicks_total)
                    elif metrica_nome == 'CPM':
                        period_kpis['CPM'] = func(spend_total, impressions_total)
            resumo_periodos[label] = period_kpis
        print(f"[DEBUG MEDIA AGENT] Resumo de Períodos ({plataforma}):\n{resumo_periodos}")

        comparativos = {}
        for metrica in metricas_selecionadas: # Itera apenas sobre as métricas selecionadas
            if metrica in resumo_periodos['atual'] and metrica in resumo_periodos['mom']:
                comparativos[f'{metrica}_MoM'] = percent_change(resumo_periodos['atual'].get(metrica), resumo_periodos['mom'].get(metrica))
            if metrica in resumo_periodos['atual'] and metrica in resumo_periodos['yoy']:
                comparativos[f'{metrica}_YoY'] = percent_change(resumo_periodos['atual'].get(metrica), resumo_periodos['yoy'].get(metrica))
        print(f"[DEBUG MEDIA AGENT] Comparativos ({plataforma}):\n{comparativos}")

        # Formatação para markdown
        markdown_parts = []
        colunas_para_detalhe = ['Date', 'Spend', 'Revenue', 'Sessions', 'Conversions']
        # Adiciona as colunas de métricas calculadas dinamicamente
        for metrica_nome in metricas_selecionadas:
            if metrica_nome == 'ROI': colunas_para_detalhe.append('ROI')
            elif metrica_nome == 'CPS': colunas_para_detalhe.append('CPS')
            elif metrica_nome == 'TKM': colunas_para_detalhe.append('TKM')
            elif metrica_nome == 'Conversion_Rate': colunas_para_detalhe.append('Conversion_Rate')
            elif metrica_nome == 'CPC': colunas_para_detalhe.append('CPC')
            elif metrica_nome == 'CPM': colunas_para_detalhe.append('CPM')

        colunas_existentes_atual = [col for col in colunas_para_detalhe if col in df_current.columns]

        if not df_current.empty and colunas_existentes_atual:
            df_current_sorted = df_current.sort_values(by='Date')
            # Arredondamento para exibição no markdown
            for col in df_current_sorted.columns:
                # Apenas tenta arredondar colunas que são numéricas
                if pd.api.types.is_numeric_dtype(df_current_sorted[col]):
                    if 'Spend' in col or 'Revenue' in col or 'Cost' in col or 'TKM' in col:
                        df_current_sorted[col] = df_current_sorted[col].apply(lambda x: round(x, 2) if pd.notnull(x) else x)
                    elif 'Rate' in col:
                        df_current_sorted[col] = df_current_sorted[col].apply(lambda x: round(x, 4) if pd.notnull(x) else x)

            markdown_parts.append(
                f"**Detailed {plataforma} Data for {start_current_month.strftime('%B %Y')}:**\n"
                f"{df_current_sorted[colunas_existentes_atual].to_markdown(index=False)}\n\n"
            )       
        else:
            markdown_parts.append(f"**Detailed {plataforma} Data for {start_current_month.strftime('%B %Y')}:**\n- Data: Not available or insufficient columns.\n\n")

        markdown_parts.append(formatar_markdown_consolidado(df_prev_month, 
                                                              f"Comparative {plataforma} Previous Month ({start_prev_month.strftime('%B %Y')})"))
        markdown_parts.append(formatar_markdown_consolidado(df_yoy, 
                                                              f"Comparative {plataforma} Same Month Previous Year ({start_yoy_month.strftime('%B %Y')})"))
        
        summary_last_4_months_md = f"**Consolidated {plataforma} Summary for Last 4 Months (prior to {start_current_month.strftime('%B %Y')}):**\n"
        data_found_for_last_4_months = False
        for i in range(2, 5):
            month_start_hist = (start_current_month - relativedelta(months=i))
            month_end_hist = (month_start_hist + relativedelta(months=1)) - relativedelta(days=1)
            df_month_hist = df_full[(df_full['Date'] >= month_start_hist) & (df_full['Date'] <= month_end_hist)]
            
            if not df_month_hist.empty:
                data_found_for_last_4_months = True
            summary_last_4_months_md += formatar_markdown_consolidado(df_month_hist, 
                                                                        f"{plataforma} - Month of {month_start_hist.strftime('%B %Y')}")
        
        if not data_found_for_last_4_months:
             summary_last_4_months_md += "No data available for the last 4 months for summary.\n"
        markdown_parts.append(summary_last_4_months_md)

        print(f"Agente de Mídia ({plataforma}): Dados históricos e comparativos processados.")

        # Gerar caminho e salvar JSON de KPIs
        mes_analise_formatado_json = start_current_month.strftime("%B de %Y")
        # Passa o nome do cliente para gerar o caminho correto
        caminho_json = gerar_caminho_kpis_json(plataforma, mes_analise_formatado_json, cliente_nome=tool_input_params.get('cliente_nome_para_kpis'))
        
        # Salvar o JSON de KPIs
        from app.utils.save_json import salvar_json_kpis # Importar aqui para evitar circular dependency
        salvar_json_kpis(
            plataforma=plataforma,
            mes_analise=mes_analise_formatado_json,
            resumo_periodos=resumo_periodos,
            comparativos=comparativos,
            pasta_saida=os.path.dirname(caminho_json),
            sufixo_nome=plataforma.upper().replace(' ', '_'),
            metricas_selecionadas=metricas_selecionadas # Passa as métricas selecionadas
        )

        return {
            "markdown": "".join(markdown_parts),
            "caminho_json": caminho_json,
        } 

    except (PlanilhaNaoEncontradaError, AbaNaoEncontradaError, ColunaNaoEncontradaError, 
            ErroLeituraDadosError, FormatoDataInvalidoError) as e_custom:
        raise e_custom 
    except Exception as e:
        tb_str = traceback.format_exc()
        raise ErroProcessamentoDadosAgente(f"Erro inesperado na ferramenta de dados do Agente de Mídia ({plataforma}): {type(e).__name__} - {e}\nTraceback:\n{tb_str}")



