from math import sqrt, nan

def lowVol(market, last_nyears=None, num_pf=30):
    ''' Portfolio selection based on low volatility (annualized)
    args:
        last_nyears: int
        num_pf: number of stocks included in the portfolio
    '''
    returns = market.calculate_returns()
    
    if type(last_nyears) == int:
        num_days = str(last_nyears * 365)+'D' # 365 includes holidays
        returns = returns.last(num_days)
    
    std = returns.std(axis=0, skipna=True) * sqrt(252) # annualize
    std[std == 0] = nan # Get rid of non-traded stocks
    
    # rank
    ranked = std[std.rank(ascending=True)<= num_pf]
    tickers = ranked.index
    
    return tickers