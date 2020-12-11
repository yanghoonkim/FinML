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
    
    def get_ticker(self, source = 'krx'):
        ''' Get tickers from the given source
        args:
            source: source of data ('krx', ...)
        '''
        print('Get ticker symbol from [%s] ... ' %source, end='')
        
        if source == 'krx': # KOSPI / KOSDAQ / KONEX
            df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
            
            # Add 0 padding to tickers
            df.종목코드 = df.종목코드.map('{:06d}'.format)
            
            ticker_path = os.path.join(self.data_path, 'krx')
            if not os.path.exists(ticker_path): 
                os.makedirs(ticker_path)
            
            # Save 
            with open(os.path.join(ticker_path, 'kor_ticker'+'.pkl'), 'wb') as f:
                pkl.dump(df, f)
                
        print('Complete!')