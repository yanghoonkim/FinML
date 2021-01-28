from datetime import datetime
from math import sqrt, nan
import pandas as pd

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
    ''' Portfolio selection based on indicator (value investing)
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


def fscore_kr(market, scores=[9]):
    ''' Portfolio selection based on f-score (Piotroski et al., 2000) (quality investing)
    args:
        scores: stocks with the given scores are returned
    '''
    print('Attention: you have to keep financial statements up-to-date!')

    # Financial statement
    fs  = market.fss
    
    # Probability
    roa = fs['지배주주순이익'] / fs['자산']
    cfo = fs['영업활동으로인한현금흐름'] / fs['자산']
    accurual = cfo - roa
    
    # Financial performance
    lev = fs['장기차입금'] / fs['자산']
    liq = fs['유동자산'] / fs['유동부채']
    offer = fs['유상증자'] # estimated

    # Operating efficiency
    margin = fs['매출총이익'] / fs['매출액']
    turn = fs['매출액'] / fs['자산']

    if datetime.now().month not in [1,2,3,4]:
        col_idx = -1
    else:
        col_idx = -2

    f_1 = (roa.iloc[:, col_idx] > 0).astype(int)
    f_2 = (cfo.iloc[:, col_idx] > 0).astype(int)
    f_3 = ((roa.iloc[:, col_idx] - roa.iloc[:, col_idx-1]) > 0).astype(int)
    f_4 = (accurual.iloc[:, col_idx] > 0).astype(int)
    f_5 = ((lev.iloc[:, col_idx] - lev.iloc[:, col_idx-1]) <= 0).astype(int)
    f_6 = ((liq.iloc[:, col_idx] - liq.iloc[:, col_idx-1]) > 0).astype(int)
    f_7 = (offer.iloc[:, col_idx].isna() | (offer.iloc[:, col_idx] <= 0)).astype(int)
    f_8 = ((margin.iloc[:, col_idx] - margin.iloc[:, col_idx-1]) > 0).astype(int)
    f_9 = ((turn.iloc[:, col_idx] - turn.iloc[:, col_idx-1]) > 0).astype(int)

    f_table = pd.concat([f_1, f_2, f_3, f_4, f_5, f_6, f_7, f_8, f_9], axis=1)
    f_score = f_table.sum(axis=1) 
    
    tickers = pd.Series()
    for score in scores:
        tickers = tickers.append(f_score[f_score == score])
    
    tickers = tickers.index
    return tickers
