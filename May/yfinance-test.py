import pandas as pd

import pandas_datareader.data as web
import datetime


df = pd.read_csv('TestData.csv')
print(df['Ticker'].unique())