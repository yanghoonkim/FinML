from datetime import datetime

from finml.data_reader import GetInitData, StockMarket
from finml.portfolio_selection.single_factor import lowVol
from finml.portfolio_optimization import SimpleMeanVariance

# >>> Korean market
# Get initial data (For the first time, this will takes about an hour)
kor_market = GetInitData(source='krx', data_path = 'data')
kor_market.get_tickers() # Get a list of stock tickers
kor_market.get_prices(start=datetime(2010,1,1), # Get price information (for all stocks)
                      end=datetime.now()) 
kor_market.get_fs() # Get financial statements (for all stocks)
kor_market.calculate_indicators() # Calculate investment indicators

# Portfolio selection
stock_list = lowVol(market=kor_market, 
                    last_nyears=1, 
                    num_pf=30, 
                    interval='d')

start, end = kor_market.convert_to_date(last_nyears=1)
mean, cov = kor_market.get_mean_cov(interval='d',
                                    start=start,
                                    end=end,
                                    subset=stock_list)

# Portfolio optimization
SMV = SimpleMeanVariance(mean, cov)
SMV.plot(show=True, save_path='simple_mean_variance.jpeg')


# >>> American market
'''
# get market data
market = StockMarket(start_date=datetime(2018,1,1), end_date=datetime.now())
market.get_stock_price(['AAPL', 'TSLA', 'MSFT', 'NVDA'])
market_mean, market_covariance, _ = market.get_stock_statistics()

# simple mean-variance plot
SMV = SimpleMeanVariance(market_mean, market_covariance)
SMV.plot(show=True, save_path='log/simple_mean_variance.jpeg')
'''