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
    print(std)
    std[std == 0] = nan # Get rid of non-traded stocks
    
    # rank
    ranked = std[std.rank(ascending=True)<= num_pf]
    tickers = ranked.index
    
    return tickers