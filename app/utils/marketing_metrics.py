def roi(revenue, investment):
    """Return on Ad Spend."""
    if investment == 0:
        return 0
    return revenue / investment

def cps(investment, sessions):
    """Custo por Sessão."""
    if sessions == 0:
        return 0
    return investment / sessions

def tkm(revenue, conversions):
    """Ticket Médio."""
    if conversions == 0:
        return 0
    return revenue / conversions

def conversion_rate(conversions, sessions):
    """Taxa de Conversão."""
    if sessions == 0:
        return 0
    return conversions / sessions

def cpc(investment, clicks):
    """Custo por Cliques."""
    if clicks == 0:
        return 0
    return investment / clicks

def cpm(investment, impressions):
    """Custo por Mil Impressões."""
    if impressions == 0:
        return 0
    return (investment / impressions) * 1000

def percent_change(current, previous):
    """Retorna a variação percentual, lidando com None e zero."""
    if current is None or previous is None:
        return 0  # Ou float('nan'), ou None, conforme seu padrão
    if previous == 0:
        return float('inf') if current != 0 else 0
    return ((current / previous) - 1)*100  # Retorna em porcentagem
