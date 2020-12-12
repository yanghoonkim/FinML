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
    accumulated_returns = (returns+1).prod(axis=0)
    
    # Ranking: the bigger, the better 
    ranked = accumulated_returns[accumulated_returns.rank(ascending=False)<= num_pf]
    tickers = ranked.index
    
    return tickers