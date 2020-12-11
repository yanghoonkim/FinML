import os
import pickle as pkl
from datetime import datetime
import pandas as pd

class GetInitData:
    def __init__(self):
        self.pwd = os.getcwd()
        self.data_path = os.path.join(self.pwd, 'data')
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
    
    def get_ticker(self, source='krx'):
        ''' Get tickers from the given source
        args:
            source: source of data ('krx', ...)
        '''
        
        base_path = os.path.join(self.data_path, source)
        ticker_path = os.path.join(base_path, 'ticker.pkl')
        
        if not os.path.exists(ticker_path):
            print('Get ticker symbol from [%s] ... ' %source, end='')
        
            if source == 'krx': # KOSPI / KOSDAQ / KONEX
                df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]

                # Add 0 padding to tickers
                df.종목코드 = df.종목코드.map('{:06d}'.format)

                if not os.path.exists(base_path): 
                    os.makedirs(base_path)

                # Save 
                with open(ticker_path, 'wb') as f:
                    pkl.dump(df, f)
                
                self.ticker = df

            print('Complete!')
            
        else: 
            print('Load ticker: %s' %ticker_path)
            with open(ticker_path, 'rb') as f:
                self.ticker = pkl.load(f)