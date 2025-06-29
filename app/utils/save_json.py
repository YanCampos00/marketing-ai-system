import os
import json

def safe_float(val, casas=2):
    """Converte para float e arredonda, retorna None se não for possível."""
    try:
        if val is None:
            return None
        return round(float(val), casas)
    except Exception:
        return None

def safe_int(val):
    """Converte para int, retorna None se não for possível."""
    try:
        if val is None:
            return None
        return int(val)
    except Exception:
        return None

def salvar_json_kpis(
    plataforma, mes_analise, resumo_periodos, comparativos, pasta_saida, sufixo_nome, metricas_selecionadas
):
    # Função auxiliar para formatar variações com segurança
    def format_variation(value, unit="%"):
        if value is None or value == float('inf') or value == float('-inf'):
            return "N/A"
        # Para taxas de conversão, a unidade é 'pp' (pontos percentuais)
        if unit == "pp":
            return f"{value:+.2f}pp"
        return f"{value:+.1f}{unit}"

    # Mapeamento de métricas para seus nomes de KPI no JSON
    kpi_names_map = {
        'ROI': 'ROI',
        'Conversion_Rate': 'CONVERSION_RATE',
        'Spend': 'SPEND',
        'Revenue': 'REVENUE',
        'Conversions': 'CONVERSIONS',
        'CPS': 'CPS',
        'TKM': 'TKM',
        'CPC': 'CPC',
        'CPM': 'CPM'
    }

    kpis_atuais = {}
    for metrica in metricas_selecionadas:
        kpi_base_name = kpi_names_map.get(metrica)
        if kpi_base_name:
            if metrica == 'Conversion_Rate':
                kpis_atuais[f"{kpi_base_name}_CURRENT_{sufixo_nome}"] = safe_float(resumo_periodos['atual'].get(metrica), 4)
            elif metrica in ['Spend', 'Revenue', 'ROI', 'CPS', 'TKM', 'CPC', 'CPM']:
                kpis_atuais[f"{kpi_base_name}_CURRENT_{sufixo_nome}"] = safe_float(resumo_periodos['atual'].get(metrica), 2)
            elif metrica == 'Conversions':
                kpis_atuais[f"{kpi_base_name}_CURRENT_{sufixo_nome}"] = safe_int(resumo_periodos['atual'].get(metrica))

    comp_mom = {}
    for metrica in metricas_selecionadas:
        kpi_base_name = kpi_names_map.get(metrica)
        if kpi_base_name and f'{metrica}_MoM' in comparativos:
            if metrica == 'Conversion_Rate':
                comp_mom[f"VARIATION_{kpi_base_name}_MOM_{sufixo_nome}"] = format_variation(comparativos.get(f'{metrica}_MoM'), unit="pp")
            else:
                comp_mom[f"VARIATION_{kpi_base_name}_MOM_{sufixo_nome}"] = format_variation(comparativos.get(f'{metrica}_MoM'))

    comp_yoy = {}
    for metrica in metricas_selecionadas:
        kpi_base_name = kpi_names_map.get(metrica)
        if kpi_base_name and f'{metrica}_YoY' in comparativos:
            if metrica == 'Conversion_Rate':
                comp_yoy[f"VARIATION_{kpi_base_name}_YOY_{sufixo_nome}"] = format_variation(comparativos.get(f'{metrica}_YoY'), unit="pp")
            else:
                comp_yoy[f"VARIATION_{kpi_base_name}_YOY_{sufixo_nome}"] = format_variation(comparativos.get(f'{metrica}_YoY'))

    dict_saida = {
        "PLATFORM": str(plataforma),
        "ANALYSIS_MONTH": str(mes_analise),
        "CURRENT_KPIs": kpis_atuais,
        "COMPARATIVES_MOM": comp_mom,
        "COMPARATIVES_YOY": comp_yoy
    }

    os.makedirs(pasta_saida, exist_ok=True)
    nome_arquivo = f"{plataforma.lower().replace(' ', '_')}_{mes_analise.replace(' ', '_')}.json"
    caminho_arquivo = os.path.join(pasta_saida, nome_arquivo)
    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dict_saida, f, ensure_ascii=False, indent=2)
        print(f"Arquivo JSON salvo em: {caminho_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar JSON: {e}")
        raise

