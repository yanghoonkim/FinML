from math import sqrt, nan

def indicator(market, ind, low_or_high, num_pf=30):
    ''' Portfolio selection based on indicator
    args:
        ind: name of indicator, such as ['per', 'pbr', 'pcr', 'psr']
        low_or_high: the lower(higher), the better, ['low', 'high']
        num_pf: number of stocks included in the portfolio
    '''
    if low_or_high not in ['low', 'high']:
        raise ValueError('low_or_high should be one of ["low", "high"]')
        
    ind_value = market.indicators.loc[ind.upper()]
    
    # Ranking: the bigger, the better 
    ascending = low_or_high == 'low'
    ranked = ind_value[ind_value.rank(ascending=ascending)<= num_pf]
    tickers = ranked.index
    
    return tickers