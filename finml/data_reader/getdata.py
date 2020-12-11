import os
from tqdm import tqdm
import pickle as pkl
from datetime import datetime
import pandas as pd
import pandas_datareader as pdr
import requests


class GetInitData:
    def __init__(self, source='krx', data_path = 'data'):
        '''
        args:
            source: name of data source ('krx', ...)
        '''
        self.source = source
        self.tickers = None
        self.prices = pd.DataFrame()
        
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
            print('Load tickers: %s' %ticker_path)
            with open(ticker_path, 'rb') as f:
                self.tickers = pkl.load(f)
            
        
    def get_prices(self, 
                   start_date=datetime(2010, 1, 1), 
                   end_date=datetime.now(), 
                   initialize=False):
        ''' Get stock prices with pandas-datareader
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
            
            if self.source == 'krx':
                for ticker in tqdm(self.tickers['종목코드']):
                    price_data = pdr.DataReader(ticker, 'naver', start=start_date, end=end_date)[['Close']]
                    price_data = price_data.rename(columns={'Close': ticker})
                    with open(os.path.join(price_path, ticker)+'.pkl', 'wb') as f:
                        pkl.dump(price_data, f)
                    self.prices = pd.concat([self.prices, price_data], axis=1)
            
            with open(prices_path, 'wb') as f:
                pkl.dump(self.prices, f)
            print('Complete!')
                    
        else:
            print('Load prices: %s' %prices_path)
            with open(prices_path, 'rb') as f:
                self.prices = pkl.load(f)
                
    
    def get_fs(self, initialize=False):
        ''' Get financial statement with pandas'''
        if self.tickers is None:
            raise ValueError('ticker is not initialized')
        
        fs_path = os.path.join(self.data_path, 'fs')
        
        if not os.path.exists(fs_path):
            os.mkdir(fs_path)
        
        if len(os.listdir(fs_path)) == 0 or initialize == True:
    
            if self.source == 'krx':
                for ticker in tqdm(self.tickers['종목코드']):
                    fs_url = 'http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A%s' %ticker
                    fs_page = requests.get(fs_url)

                    # fs_tables consists of:
                    # [0]: Income statement (annual)
                    # [1]: Income statement (quarterly)
                    # [2]: Balance sheet (annual)
                    # [3]: Balance sheet (quarterly)
                    # [4]: Statement of cash flow (annual)
                    # [5]: Statement of cash flow (quarterly)
                    try:
                        fs_tables = pd.read_html(fs_page.text, displayed_only=False)
                    except: 
                        print('Error in ticker: %s' %ticker)
                        continue
                    
                    # We only use annual information
                    is_data = fs_tables[0]
                    bs_data = fs_tables[2]
                    cf_data = fs_tables[4]

                    # Remove '전년동기', '전년동기(%)' columns in is_data
                    is_data = is_data.drop(columns = ['전년동기', '전년동기(%)'])

                    # Concatenation
                    fs_data = pd.concat([is_data, bs_data, cf_data], axis = 0)

                    # Refinement
                    fs_data.iloc[:, 0] = fs_data.iloc[:, 0].str.replace('계산에 참여한 계정 펼치기', '', regex=False)
                    fs_data = fs_data.drop_duplicates(fs_data.columns[0], keep='first')
                    fs_data.index = fs_data.iloc[:, 0]
                    fs_data = fs_data.drop(columns = fs_data.columns[0])
                    valid_cols = [col for col in fs_data.columns if col.endswith('/12')]
                    fs_data = fs_data[valid_cols]
                    
                    with open(os.path.join(fs_path, ticker)+'.pkl', 'wb') as f:
                        pkl.dump(fs_data, f)
                        
            print('Complete!')
            
        else:
            print('Financial statements are already downloaded')