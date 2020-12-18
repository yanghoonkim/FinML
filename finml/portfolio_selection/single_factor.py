from math import sqrt, nan

def lowVol(market, last_nyears=1, num_pf=30, interval='d'):
    ''' Portfolio selection based on low volatility (annualized)
    args:
        last_nyears: int
        num_pf: number of stocks included in the portfolio
        interval: time unit the volatility is calculated, ['d', 'w', 'm', 'y']
    '''
    if type(last_nyears) == int:
        num_days = str(last_nyears * 365)+'D' # 365 includes holidays
        start = market.prices.last(num_days).index[0]

    else:
        start = market.prices.index[0]
    
    returns = market.calculate_returns(interval=interval, start=start)
    
    if interval == 'd':
        n_units = 252
    elif interval == 'w':
        n_units = 52
    elif interval == 'm':
        n_units = 12
    else: # 'y'
        n_units = 1
        
    std = returns.std(axis=0, skipna=True) * sqrt(n_units) # annualize
    std[std == 0] = nan # Get rid of non-traded stocks
    
    # Ranking: the smaller, the better 
    ranked = std[std.rank(ascending=True)<= num_pf]
    tickers = ranked.index
    
    return tickers

from math import sqrt, nan



def momentum(market, last_nyears=1, num_pf=30):
    ''' Portfolio selection based on momentum
    args:
        last_nyears: int
        num_pf: number of stocks included in the portfolio
    '''
    if type(last_nyears) == int:
        num_days = str(last_nyears * 365)+'D' # 365 includes holidays
        start = market.prices.last(num_days).index[0]

    else:
        start = market.prices.index[0]
    
    returns = market.calculate_returns(interval='d', start=start)
    accumulated_returns = (returns+1).prod(axis=0, skipna=True)
    
    # Ranking: the bigger, the better 
    ranked = accumulated_returns[accumulated_returns.rank(ascending=False)<= num_pf]
    tickers = ranked.index
    
    return tickers


def riskAdj(market, last_nyears=1, num_pf=30, interval='d'):
    ''' Portfolio selection based on risk-adjusted return (annualized volatility)
    args:
        last_nyears: int
        num_pf: number of stocks included in the portfolio
        interval: time unit the volatility is calculated, ['d', 'w', 'm', 'y']
    '''
    if type(last_nyears) == int:
        num_days = str(last_nyears * 365)+'D' # 365 includes holidays
        start = market.prices.last(num_days).index[0]

    else:
        start = market.prices.index[0]
    
    # Numerator: accumulated return
    daily_returns = market.calculate_returns(interval='d', start=start)
    accumulated_returns = (daily_returns+1).prod(axis=0)
    
    # Denominator: risk (annualized volatility)
    returns = market.calculate_returns(interval=interval, start=start)
    
    if interval == 'd':
        n_units = 252
    elif interval == 'w':
        n_units = 52
    elif interval == 'm':
        n_units = 12
    else: # 'y'
        n_units = 1
        
    std = returns.std(axis=0, skipna=True) * sqrt(n_units) # annualize
    std[std == 0] = nan # Get rid of non-traded stocks
    
    # risk-adjusted return
    risk_adj = accumulated_returns / std
    
    # Ranking: the bigger, the better 
    ranked = risk_adj[risk_adj.rank(ascending=False)<= num_pf]
    tickers = ranked.index
    
    return tickers


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