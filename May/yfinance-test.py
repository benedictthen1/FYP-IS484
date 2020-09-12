import pandas as pd

import pandas_datareader.data as web
import datetime


df = pd.read_csv('TestData.csv')
#print(df['Ticker'].unique())
print(len(df['Ticker'].unique()))
ticker_list = [ticker.strip() for ticker in df['Ticker'].unique()]
print(len(ticker_list))