import os
from tqdm import tqdm
import pickle as pkl
from datetime import datetime
import pandas as pd
import pandas_datareader as pdr

class GetInitData:
    def __init__(self, source='krx', data_path = 'data'):
        '''
        args:
            source: name of data source ('krx', ...)
        '''
        self.source = source
        self.tickers = None
        self.price = None
        
        self.data_path = os.path.join(data_path, self.source)
        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)
    
    def get_tickers(self, initialize=False):
        ''' Get tickers from the given source
        args:
            initialize: if True, ignore existing ticker data and initialize ticker.pkl
        '''
        
        ticker_path = os.path.join(self.data_path, 'tickers.pkl')
        
        if not os.path.exists(ticker_path) or initialize == True:
            print('Get ticker symbol from [%s] ... ' %self.source, end='')
        
            if self.source == 'krx': # KOSPI / KOSDAQ / KONEX
                df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]

                # Add 0 padding to tickers
                df.종목코드 = df.종목코드.map('{:06d}'.format)

                if not os.path.exists(self.data_path): 
                    os.makedirs(self.data_path)

                # Save 
                with open(ticker_path, 'wb') as f:
                    pkl.dump(df, f)
                
                self.tickers = df

            print('Complete!')
            
        else: 
            print('Load ticker: %s' %ticker_path)
            with open(ticker_path, 'rb') as f:
                self.tickers = pkl.load(f)
            
        
    def get_prices(self, 
                       start_date=datetime(2010, 1, 1), 
                       end_date=datetime.now(), 
                       initialize=False):
        ''' Get stock prices with pandas datareader
        args:
            initialize: if True, ignore existing price data and initialize 
        '''
        if self.tickers is None:
            raise ValueError('ticker is not initialized')
        
        price_path = os.path.join(self.data_path, 'price')
        prices_path = os.path.join(self.data_path, 'prices.pkl')
        
        if not os.path.exists(price_path):
            os.mkdir(price_path)
            
        if not os.path.exists(prices_path) or initialize == True:
            prices = pd.DataFrame()
            
            if self.source == 'krx':
                for ticker in tqdm(self.tickers['종목코드']):
                    price_data = pdr.DataReader(ticker, 'naver', start=start_date, end=end_date)[['Close']]
                    with open(os.path.join(price_path, ticker)+'.pkl', 'wb') as f:
                        pkl.dump(price_data, f)
                    prices = pd.concat([prices, price_data], axis=1)
            
            with open(prices_path, 'wb') as f:
                pkl.dump(prices, f)
            print('Complete!')
                    
        else:
            print('Prices are already downloaded')