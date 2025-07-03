import pandas as pd

def calculate_ctr(clicks: pd.Series, impressions: pd.Series) -> pd.Series:
    """Calcula o Click-Through Rate (CTR)."""
    return (clicks / impressions) * 100

def calculate_cpc(cost: pd.Series, clicks: pd.Series) -> pd.Series:
    """Calcula o Cost Per Click (CPC)."""
    return cost / clicks

def calculate_cpm(cost: pd.Series, impressions: pd.Series) -> pd.Series:
    """Calcula o Cost Per Mille (CPM)."""
    return (cost / impressions) * 1000

def calculate_roas(revenue: pd.Series, cost: pd.Series) -> pd.Series:
    """Calcula o Return On Ad Spend (ROAS)."""
    return revenue / cost

def roi(revenue, spend):
    """Calcula o Retorno sobre Investimento (ROI) como um múltiplo.
       Ex: R$ 2 de receita para R$ 1 de gasto = ROI de 2.0
    """
    if spend == 0:
        return 0.0
    return revenue / spend

def cps(spend, sessions):
    """Calcula o Custo por Sessão (CPS)."""
    if sessions == 0:
        return 0
    return spend / sessions

def tkm(revenue, conversions):
    """Calcula o Ticket Médio (TKM)."""
    if conversions == 0:
        return 0
    return revenue / conversions

def conversion_rate(conversions, sessions):
    """Calcula a Taxa de Conversão."""
    if sessions == 0:
        return 0
    return (conversions / sessions) * 100

def cpc(spend, clicks):
    """Calcula o Custo por Clique (CPC)."""
    if clicks == 0:
        return 0
    return spend / clicks

def cpm(spend, impressions):
    """Calcula o Custo por Mil Impressões (CPM)."""
    if impressions == 0:
        return 0
    return (spend / impressions) * 1000

def percent_change(current, previous):
    """Calcula a variação percentual entre dois valores."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return ((current - previous) / previous) * 100
