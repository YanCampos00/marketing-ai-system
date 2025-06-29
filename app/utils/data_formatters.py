import pandas as pd
from app.utils.marketing_metrics import roi, cps, tkm, conversion_rate, cpc, cpm

def formatar_markdown_consolidado(df_periodo, periodo_nome):
    """
    Gera um markdown com valores consolidados (totais) e KPIs calculados a partir dos totais.
    """
    if df_periodo is None or df_periodo.empty:
        return f"**{periodo_nome}:**\n- Data: Not available\n\n"

    # Cria uma cópia para evitar SettingWithCopyWarning
    df_periodo_copy = df_periodo.copy()

    # Garantir que tudo é numérico e colunas obrigatórias existam
    for col in ['Spend', 'Revenue', 'Sessions', 'Conversions', 'Clicks', 'Impressions']:
        if col in df_periodo_copy.columns:
            df_periodo_copy.loc[:, col] = pd.to_numeric(df_periodo_copy[col], errors='coerce').fillna(0)
        else:
            df_periodo_copy.loc[:, col] = 0

    spend_total = df_periodo_copy['Spend'].sum()
    revenue_total = df_periodo_copy['Revenue'].sum()
    sessions_total = df_periodo_copy['Sessions'].sum()
    conversions_total = df_periodo_copy['Conversions'].sum()
    clicks_total = df_periodo_copy['Clicks'].sum() if 'Clicks' in df_periodo_copy.columns else 0
    impressions_total = df_periodo_copy['Impressions'].sum() if 'Impressions' in df_periodo_copy.columns else 0

    # KPIs consolidados
    roi_val = roi(revenue_total, spend_total)
    cps_val = cps(spend_total, sessions_total)
    tkm_val = tkm(revenue_total, conversions_total)
    conversion_rate_val = conversion_rate(conversions_total, sessions_total)
    cpc_val = cpc(spend_total, clicks_total) if clicks_total else None
    cpm_val = cpm(spend_total, impressions_total) if impressions_total else None

    md_str = f"**{periodo_nome}:**\n"
    md_str += f"- Spend (Total): R$ {spend_total:,.2f}\n"
    md_str += f"- Revenue (Total): R$ {revenue_total:,.2f}\n"
    md_str += f"- Sessions (Total): {int(sessions_total):,}\n"
    md_str += f"- Conversions (Total): {int(conversions_total):,}\n"
    md_str += f"- ROI (Calculated): {roi_val:.2f}\n"
    md_str += f"- CPS (Cost Per Session): R$ {cps_val:.2f}\n"
    md_str += f"- TKM (Ticket Médio): R$ {tkm_val:.2f}\n"
    md_str += f"- Conversion Rate: {conversion_rate_val:.2%}\n"
    if cpc_val is not None:
        md_str += f"- CPC (Cost Per Click): R$ {cpc_val:.2f}\n"
    if cpm_val is not None:
        md_str += f"- CPM (Cost Per Mille): R$ {cpm_val:.2f}\n"
    return md_str + "\n"
