import os
from tqdm import tqdm
import pickle as pkl
from datetime import datetime
import pandas as pd
import pandas_datareader as pdr
import requests
import lxml
from lxml.html import fromstring

from math import nan
import numpy as np


class GetInitData:
    def __init__(self, source='krx', data_path = 'data'):
        '''
        args:
            source: name of data source ('krx', ...)
        '''
        self.source = source
        self.tickers = None
        self.prices = pd.DataFrame()
        self.volumes = pd.DataFrame()
        self.fss = dict()
        self.indicators = pd.DataFrame()
        
        self.data_path = os.path.join(data_path, self.source)
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
    
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
            
        
    def get_prices_and_volumes(self, 
                   start=datetime(2010, 1, 1), 
                   end=datetime.now(), 
                   initialize=False):
        ''' Get stock prices & volumes with pandas-datareader
        args:
            initialize: if True, ignore existing price data and initialize 
        '''
        if self.tickers is None:
            raise ValueError('ticker is not initialized')
        
        price_path = os.path.join(self.data_path, 'price')
        prices_path = os.path.join(self.data_path, 'prices.pkl')
        volume_path = os.path.join(self.data_path, 'volume')
        volumes_path = os.path.join(self.data_path, 'volumes.pkl')
        
        if not os.path.exists(price_path):
            os.makedirs(price_path)
        
        if not os.path.exists(volume_path):
            os.makedirs(volume_path)
            
        if not os.path.exists(prices_path) or initialize == True:
            print('Get prices/volumes from [naver] ...', end='')
            if self.source == 'krx':
                for ticker in tqdm(list(self.tickers['종목코드'])+['KOSPI', 'KPI200', 'KOSDAQ']):
                    cv = pdr.DataReader(ticker, 'naver', start=start, end=end)[['Close', 'Volume']]
                    cv = cv.astype('float64')
                    price_data = cv[['Close']].rename(columns={'Close': ticker})
                    volume_data = cv[['Volume']].rename(columns={'Volume': ticker})

                    with open(os.path.join(price_path, ticker)+'.pkl', 'wb') as f:
                        pkl.dump(price_data, f)
                    with open(os.path.join(volume_path, ticker)+'.pkl', 'wb') as f:
                        pkl.dump(volume_data, f)
                    self.prices = pd.concat([self.prices, price_data], axis=1)
                    self.volumes = pd.concat([self.volumes, volume_data], axis=1)
                self.prices = self.prices.astype('float64')
                self.volumes = self.volumes.astype('float64')
                
            with open(prices_path, 'wb') as f:
                pkl.dump(self.prices, f)
            with open(volumes_path, 'wb') as f:
                pkl.dump(self.volumes, f)
                
            print('Complete!')
                    
        else:
            print('Load prices & volumes: %s & %s' %(prices_path, volumes_path))
            with open(prices_path, 'rb') as f:
                self.prices = pkl.load(f)
            with open(volumes_path, 'rb') as f:
                self.volumes = pkl.load(f)
                
    
    def get_fs(self, initialize=False):
        ''' Get financial statement with pandas
        args:
            initialize: if True, ignore existing financial statement data and initialize
        '''
        if self.tickers is None:
            raise ValueError('ticker is not initialized')
        
        fs_path = os.path.join(self.data_path, 'fs')
        
        if not os.path.exists(fs_path):
            os.makedirs(fs_path)
        
        if len(os.listdir(fs_path)) == 0 or initialize == True:
            print('Get financial statements from [fnguide] ...', end='')
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
                        if len(fs_tables) != 6:
                            fs_tables.pop(2)
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
                    fs_data = fs_data.set_index(keys=fs_data.columns[0])
                    last_col = fs_data.columns[-1] # last quarter
                    fs_data = fs_data.drop(columns=last_col)
                    #valid_cols = [col for col in fs_data.columns if col.endswith('/12')]
                    #fs_data = fs_data[valid_cols]
                    
                    with open(os.path.join(fs_path, ticker)+'.pkl', 'wb') as f:
                        pkl.dump(fs_data, f)
                        
            print('Complete!')
            
        else:
            print('Financial statements exists: %s' %fs_path)

                
    def fs_cleansing(self, standard='005930', initialize=False):
        ''' Get refined financial statement with pandas
        args:
            initialize: if True, ignore existing financial statement (fss.pkl) data and initialize
            standard: elements of financial statement are selected based on the given standard
        '''
        if self.tickers is None:
            raise ValueError('ticker is not initialized')
        fs_path = os.path.join(self.data_path, 'fs')
        fss_path = os.path.join(self.data_path, 'fss.pkl')
        
        # Get element list based on the given standard ticker
        with open(os.path.join(fs_path, standard)+'.pkl', 'rb') as f:
            standard_fs = pkl.load(f)
        standard_date = standard_fs.columns
        standard_elements = standard_fs.index
        years = [date.split('/')[0] for date in standard_fs.columns]

        for item in standard_elements:
            self.fss[item] = pd.DataFrame(columns=standard_date)
        
        if not os.path.exists(fss_path) or initialize == True:
            print('Cleansing financial statements ...', end='')
            if self.source == 'krx':
                for ticker in tqdm(self.tickers['종목코드']):
                    try:
                        path = os.path.join(fs_path, ticker)+'.pkl'
                        with open(path, 'rb') as f:
                            fs_data = pkl.load(f)

                        if (fs_data.columns != standard_date).any():
                            print('Financial statement is not complete: %s'%ticker)
                            for element in standard_elements:
                                self.fss[element].loc[ticker] = nan

                        else:
                            for element in standard_elements:
                                if element in fs_data.index:
                                    self.fss[element].loc[ticker] = fs_data.loc[element]
                                else:
                                    self.fss[element].loc[ticker] = nan

                    except:
                        print('Not exists: %s'%ticker)
            
            with open(fss_path, 'wb') as f:
                pkl.dump(self.fss, f)
            
            print('Complete!')

        else:
            print('Load financial statements: %s' %fss_path)
            with open(fss_path, 'rb') as f:
                self.fss = pkl.load(f)        
            
    
    def calculate_returns(self,
                          interval='d',
                          start=datetime(2010, 1, 1),
                          end=datetime.now(),
                          subset=None):
        ''' Calculate returns
        args:
            interval: 'd' (daily), 'w' (weekly), 'm' (monthly), and 'y' (annual)
        returns:
            returns: dataframe of float64
        '''
        if self.prices.empty:
            raise ValueError('prices are not initialized')
        
        
        prices = self.prices[subset] if subset is not None else self.prices
        prices = prices[start <= prices.index]
        prices = prices[prices.index <= end]
        
        # Calculate return (related to the given time interval)
        returns = prices.pct_change() if interval=='d' else prices.resample(interval).ffill().pct_change()
        returns = returns.dropna(axis=0, how='all')
            
        return returns
    
        
    
    def calculate_indicators(self, initialize=False):
        ''' Calculate investment indicators (currently: PER/PBR/PCR/PSR)
        args:
            initialize: if True, ignore calculated indicators and initialize
        '''
        if self.tickers is None:
            raise ValueError('ticker is not initialized')    
        
        indicator_path = os.path.join(self.data_path, 'indicator')
        indicators_path = os.path.join(self.data_path, 'indicators.pkl')
        
        if not os.path.exists(indicator_path):
            os.makedirs(indicator_path)
        
        if not os.path.exists(indicators_path) or initialize == True:
            print('Calculate investment indicators ...')
            if self.source == 'krx':
                for ticker in tqdm(self.tickers['종목코드']):
                    try:
                        fs_data = self.fss.loc[:,[ticker]]
                        last_col = fs_data.columns[-1]
                        earnings = '지배주주순이익' if '지배주주순이익' in fs_data.index else '당기순이익'
                        denominator = fs_data.loc[[earnings, '자본', '영업활동으로인한현금흐름', '매출액'], [last_col]]

                        url = 'http://comp.fnguide.com/SVO2/ASP/SVD_main.asp?pGB=1&gicode=A%s' %ticker
                        page = requests.get(url)
                        parser = fromstring(page.text)
                        xpath_price = '//*[@id="svdMainChartTxt11"]'
                        xpath_num_issued = '//*[@id="svdMainGrid1"]/table/tbody/tr[7]/td[1]'
                        price = float(parser.xpath(xpath_price)[0].text.replace(',',''))
                        num_issued = float(parser.xpath(xpath_num_issued)[0].text.split('/')[0].replace(',','')) # only common share

                    except: 
                        print('Error in ticker: %s' %ticker)
                        continue
                    

                    indicator = price / (denominator * 1e8 / num_issued)
                    indicator[indicator < 0] = nan

                    # Set names
                    indicator.index.name = 'indicator'
                    indicator.index = ['PER', 'PBR', 'PCR', 'PSR']
                    indicator.columns = [ticker]
                    
                    with open(os.path.join(indicator_path, ticker)+'.pkl', 'wb') as f:
                        pkl.dump(indicator, f)
                    self.indicators = pd.concat([self.indicators, indicator], axis=1)

                with open(indicators_path, 'wb') as f:
                    pkl.dump(self.indicators, f)

            print('Complete!')
        else:
            print('Load indicators: %s' %indicators_path)
            with open(indicators_path, 'rb') as f:
                self.indicators = pkl.load(f)
        
    
    def get_mean_cov(self, 
                     interval='d',
                     start=datetime(2010, 1, 1),
                     end=datetime.now(),
                     subset=None):
        ''' Calculate mean and covariance of returns
        args:
            interval: 'd' (daily), 'w' (weekly), 'm' (monthly), and 'y' (annual)
            subset: a list of tickers
        returns:
            mean, variance
        '''
        returns = self.calculate_returns(interval, start, end, subset)
        mean_returns = np.array(returns.mean(axis=0)).reshape(len(subset), 1)
        covariance = np.array(returns.cov())
        
        return mean_returns, covariance
    
    def convert_to_date(self, last_nyears=1):
        ''' Convert last_nyers to start date and end date
        '''
        num_days = str(last_nyears * 365) + 'D' # 365 includes holidays
        start = self.prices.last(num_days).index[0]
        end = datetime.now()
        
        return start, end
