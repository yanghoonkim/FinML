from datetime import datetime

from finml.data_reader import GetInitData
from finml.data_reader import StockMarket
from finml.portfolio_optimization import SimpleMeanVariance

# Get market data
kor_market = GetInitData(source='krx', data_path = 'data')
kor_market.get_tickers(initialize=False)
kor_market.get_prices(initialize=False)
kor_market.get_fs(initialize=False)
kor_market.calculate_indicators(initialize=False)

# get market data
market = StockMarket(start_date=datetime(2018,1,1), end_date=datetime.now())
market.get_stock_price(['AAPL', 'TSLA', 'MSFT', 'NVDA'])
market_mean, market_covariance, _ = market.get_stock_statistics()

# simple mean-variance plot
SMV = SimpleMeanVariance(market_mean, market_covariance)
SMV.plot(show=True, save_path='log/simple_mean_variance.jpeg')
