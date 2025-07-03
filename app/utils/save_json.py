import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def salvar_json_kpis(
    plataforma: str,
    mes_analise: str,
    resumo_periodos: dict,
    comparativos: dict,
    pasta_saida: str,
    sufixo_nome: str = "",
    metricas_selecionadas: list = []
):
    """
    Salva os KPIs processados e filtrados em um arquivo JSON.
    Apenas as métricas selecionadas pelo usuário são salvas.
    """
    # Filtra o resumo do período atual
    kpis_atuais_filtrados = {k: round(v, 2) if isinstance(v, (int, float)) else v for k, v in resumo_periodos.get('atual', {}).items() if k in metricas_selecionadas}

    # Filtra os comparativos (MoM e YoY)
    comparativos_filtrados = {}
    for metrica in metricas_selecionadas:
        mom_key = f"{metrica}_MoM"
        yoy_key = f"{metrica}_YoY"
        if mom_key in comparativos:
            comparativos_filtrados[mom_key] = round(comparativos[mom_key], 2) if isinstance(comparativos[mom_key], (int, float)) else comparativos[mom_key]
        if yoy_key in comparativos:
            comparativos_filtrados[yoy_key] = round(comparativos[yoy_key], 2) if isinstance(comparativos[yoy_key], (int, float)) else comparativos[yoy_key]

    data_to_save = {
        "plataforma": plataforma,
        "mes_analise": mes_analise,
        "kpis_selecionados": kpis_atuais_filtrados,
        "comparativos_selecionados": comparativos_filtrados,
        "metricas_selecionadas": metricas_selecionadas
    }

    os.makedirs(pasta_saida, exist_ok=True)
    # Usar um nome de arquivo consistente baseado no mês de análise, não no timestamp da execução
    safe_sufixo = sufixo_nome.lower().replace(' ', '_')
    safe_mes = mes_analise.replace('-', '_')
    file_name = f"{safe_sufixo}_kpis_output_{safe_mes}.json"

    file_path = os.path.join(pasta_saida, file_name)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    return file_path
