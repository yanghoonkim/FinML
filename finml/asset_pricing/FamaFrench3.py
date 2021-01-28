from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from finml.utils import GoogleDriveDownloader
import statsmodels.formula.api as smf
from sklearn.linear_model import LinearRegression
from linearmodels.asset_pricing import LinearFactorModel

plt.style.use('ggplot')

def FamaFrench3(market, ticker, tools='statsmodels', plot_return=False):
    ''' Implementation of Fama-French 3-factor model
    args:
        tools: one from ['statsmodels', 'sklearn']
    '''
    # Fama French 3 factor in korea daily return (kospi & kosdaq)
    # expected_return = rf + beta_mkt * (rm - rf) + beta_smb * SMB + beta_hml * HML

    # Download factor data (data may not be accurate)
    print('Download factor data (data may not be accurate)...')
    file_id = '10VLyoL0YO7Q_jPW_TjXf4LC2ZLt5FQtU'
    destination = 'data/ff3_kospi_kosdaq_kor.csv'
    GoogleDriveDownloader(file_id, destination)

    ff3 = pd.read_csv(destination)

    ff3 = ff3.set_index(keys=ff3.columns[0])
    ff3.index = [datetime.strptime(idx, '%Y-%m-%d') for idx in ff3.index]
    ff3.index.name='Date'
    ff3 = ff3.rename(columns={'Mkt-Rf': 'Mkt'})

    # Calculate return of the given ticker
    ticker_return = market.calculate_returns(subset=[ticker])
    ticker_return = ticker_return.rename(columns={ticker:'T'+ticker})

    if tools == 'statsmodels':
        FamaFrench3_statsmodels(ff3, ticker_return, plot_return)
    elif tools == 'sklearn':
        FamaFrench3_sklearn_lr(ff3, ticker_return, plot_return)


def FamaFrench3_statsmodels(ff3, ticker_return, plot_return=False):
    # Plot cumulated returns
    if plot_return:
        ax = ((ticker_return+1).cumprod()-1).plot()
        ((ff3+1).cumprod()-1).plot(ax=ax)   
    
    merged = pd.merge(ticker_return, ff3, how='inner', on='Date')
    
    # Linear regression using statsmodels
    ticker = ticker_return.columns[0] 
    formula = '(' + ticker + ' - Rf) ~ Mkt + SMB + HML'
    result = smf.ols(formula=formula, data=merged).fit()
    print(result.summary())

    
def FamaFrench3_sklearn_lr(ff3, ticker_return, plot_return=False):
    # Plot cumulated returns
    if plot_return:
        ax = ((ticker_return+1).cumprod()-1).plot()
        ((ff3+1).cumprod()-1).plot(ax=ax)     
        
    merged = pd.merge(ticker_return, ff3, how='inner', on='Date')
    
    # Linaer regression using sklearn
    intersection = ff3.index.intersection(ticker_return.index)
    ticker_return_ = ticker_return.loc[intersection, :]
    ff3_ = ff3.loc[intersection, :]

    y = ticker_return_ - ff3_[['Rf']].values
    x = ff3_.drop(['Rf'], axis=1)

    mlr = LinearRegression()
    mlr.fit(x, y)

    print('| Coef\t|\tMKT\t|\tSMB\t|\tHML\t|')
    print('|\t|\t%.3f\t|\t%.3f\t|\t%.3f\t|'%(mlr.coef_[0][0], mlr.coef_[0][1], mlr.coef_[0][2]))
    

def FamaMacbeth(market, tickers, plot_return=False):
    ''' Implementation of Fama-Macbeth regression
    args:

    '''
    # Fama French 3 factor in korea daily return (kospi & kosdaq)
    # expected_return = rf + beta_mkt * (rm - rf) + beta_smb * SMB + beta_hml * HML

    # Download factor data (data may not be accurate)
    print('Download factor data (data may not be accurate)...')
    file_id = '10VLyoL0YO7Q_jPW_TjXf4LC2ZLt5FQtU'
    destination = 'data/ff3_kospi_kosdaq_kor.csv'
    GoogleDriveDownloader(file_id, destination)

    ff3 = pd.read_csv(destination)

    ff3 = ff3.set_index(keys=ff3.columns[0])
    ff3.index = [datetime.strptime(idx, '%Y-%m-%d') for idx in ff3.index]
    ff3.index.name='Date'
    ff3 = ff3.rename(columns={'Mkt-Rf': 'Mkt'})
    ff3 = ff3.drop(['Rf'], axis=1)
    ff3_m = ff3.resample('m').ffill().pct_change()
    
    portfolio_returns = market.calculate_returns(interval = 'm', subset=tickers)

    intersection = ff3_m.index.intersection(portfolio_returns.index)
    portfolio_returns_ = portfolio_returns.loc[intersection, :]
    ff3_m_ = ff3_m.loc[intersection, :]
    
    mod = LinearFactorModel(portfolios=portfolio_returns_, 
                        factors=ff3_m_)
    res = mod.fit()
    print(res)