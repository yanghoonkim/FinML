import numpy as np
import matplotlib.pyplot as plt


# polyfit may be replaced with 'np.linalg.lstsq' or .fit() method from statsmodels.formula.api
def CAPM(market, stock_tickers, index_ticker, risk_free, start, end):
    ''' Implementation of Capital Asset Pricing Model
    args:
        market: initialized market CLASS instance
        stock_tickers: a list of tickers
        index_ticker: a ticker of market index such as 'KPI200'
        risk_free: risk free rate
        start: starting date, CLASS datetime
        end: ending date, CLASS datetime
    '''
    # Calculate returns
    stock_prices = market.prices[stock_tickers]
    stock_returns = market.calculate_returns(start=start, end=end, subset=stock_tickers)
    index_returns = market.calculate_returns(start=start, subset=[index_ticker]).squeeze()

    
    
    # Calculate Beta for a portfolio of stocks
    beta = dict()
    alpha = dict()
    expected_returns = dict()
    
    for ticker in stock_tickers:
        # Drop NA
        return_ = stock_returns[ticker].dropna()
        index_return_ = index_returns[return_.index]

        plt.scatter(x=index_return_, y=return_)
        b, a = np.polyfit(index_return_, return_, 1)
        plt.plot(index_return_, b * index_return_ + a, '-', color='r')
        plt.xlabel(index_ticker)
        plt.ylabel(ticker)
        
        beta[ticker] = b
        alpha[ticker] = a
        plt.show()
        
        # Expected return
        rm = index_return_.mean() * 252
        expected_returns[ticker] = risk_free + (beta[ticker] * (rm - risk_free))
        
    return expected_returns, beta, alpha