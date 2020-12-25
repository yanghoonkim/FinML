import pandas as pd
import matplotlib.pyplot as plt
from finml.utils import GoogleDriveDownloader
#from sklearn.linear_model import LinearRegression

def FamaFrench3(market, ticker, plot_return=False):
    ticker_return = kor_market.calculate_returns(subset=[ticker])
    ticker_return = ticker_return.rename(columns={ticker:'T'+ticker})
    
    # Fama French 3 factor in korea daily return (kospi & kosdaq)
    # expected_return = rf + beta_mkt * (rm - rf) + beta_smb * SMB + beta_hml * HML
    file_id = '10VLyoL0YO7Q_jPW_TjXf4LC2ZLt5FQtU'
    destination = 'data/ff3_kospi_kosdaq_kor.csv'
    GoogleDriveDownloader(file_id, destination)

    ff3 = pd.read_csv(destination)

    ff3 = ff3.set_index(keys=ff3.columns[0])
    ff3.index = [datetime.strptime(idx, '%Y-%m-%d') for idx in ff3.index]
    ff3.index.name='Date'
    ff3 = ff3.rename(columns={'Mkt-Rf': 'Mkt'})
    
    # Plot cumulated returns
    if plot_return:
        ((plot_return+1).cumprod()-1).plot()
        ((ff3+1).cumprod()-1).plot()    
    
    merged = pd.merge(ticker_return, ff3, how='inner', on='Date')
    
    # Linear regression using statsmodels
    formula = '(T' + ticker + ' - Rf) ~ Mkt + SMB + HML'
    result = smf.ols(formula=formula, data=merged).fit()
    print(result.summary())
    
    # Linaer regression using sklearn
    #intersection = ff3.index.intersection(ticker_return.index)
    #ticker_return_ = ticker_return.loc[intersection, :]
    #ff3_ = ff3.loc[intersection, :]

    #y = ticker_return_ - ff3_[['Rf']].values
    #x = ff3_.drop(['Rf'], axis=1)
    #mlr = LinearRegression()
    #mlr.fit(x, y)