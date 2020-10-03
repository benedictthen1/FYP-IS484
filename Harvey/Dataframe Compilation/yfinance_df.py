from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import inspect
import pandas as pd
import os
import psycopg2
import yfinance.__init__ as yf
import math

server = Flask('app')
server.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://plrsqsxfozyrze:74a321364d3ec3d66ae04ea0711455ff1d224c5eb7e4f01d2d9e29dd99dddec8@ec2-34-198-103-34.compute-1.amazonaws.com:5432/dfk757hnbfc8ik'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(server)

engine = create_engine(server.config['SQLALCHEMY_DATABASE_URI'])
inspector = inspect(engine)
inspector.get_columns('Client')

df = pd.read_sql('SELECT * FROM public.\"Client\"', engine)

ticker_list = df.Ticker.unique()

ticker_list = list(filter(None, ticker_list))

yfinance_list = []
for ticker in ticker_list:
    ticker_row = [ticker]
    stock = yf.Ticker(ticker)
    #Include last Closing price in ticker_row
    ticker_row.append(float(stock.history(period="ytd")['Close'][len(stock.history(period="ytd"))-1]))
    
    #Include YTD% in ticker_row
    to_minus = float(stock.history(period="ytd")['Close'][0])
    ticker_row.append(round((ticker_row[1] / to_minus-1)*100 , 2))
    
    #Include 1d% in ticker_row
    to_minus = float(stock.history(period="ytd")['Close'][len(stock.history(period="ytd"))-2])
    ticker_row.append(round((ticker_row[1] / to_minus-1)*100 , 2))
    
    #Include 5d% in ticker_row
    to_minus = float(stock.history(period="5d")['Close'][0])
    ticker_row.append(round((ticker_row[1] / to_minus-1)*100 , 2))
    
    #Include 1mo% in ticker_row
    to_minus = float(stock.history(period="1mo")['Close'][0])
    ticker_row.append(round((ticker_row[1] / to_minus-1)*100 , 2))
    
    #Include 6mo% in ticker_row
    to_minus = float(stock.history(period="6mo")['Close'][0])
    ticker_row.append(round((ticker_row[1] / to_minus-1)*100 , 2))
    
    #Include 12mo% in ticker_row
    to_minus = float(stock.history(period="1y")['Close'][0])
    ticker_row.append(round((ticker_row[1] / to_minus-1)*100 , 2))
    
    #include Company Description in ticker_row
    ticker_row.append(stock.info["longBusinessSummary"])
    
    #Compile to yFinance list
    yfinance_list.append(ticker_row)

yfinance_df = pd.DataFrame(yfinance_list,columns=['Ticker','Closing Price','YTD%','1d %','5d %','1m %','6m %','12m %','Company Description'])

#Left join client df with yfinance df using "Ticker"
df = df.merge(yfinance_df, on='Ticker', how='left')

#Calculate % Change in Average Cost
avg_list = df["Average Unit Cost"].tolist()
closing_price_list = df["Closing Price"].tolist()

percentage_change = []
for i in range(len(avg_list)):
    if math.isnan(closing_price_list[i]) == False and avg_list[i] != None:
        percentage = (float(closing_price_list[i])/float(avg_list[i]) - 1) * 100
        percentage_change.append(percentage)
    else:
        percentage_change.append(None)

series = pd.Series(percentage_change, name="% Change from Avg Cost")

#Concatenate % Change in Average Cost series with Main df
df = pd.concat([df, series], axis=1)

#It should return 46(Client columns) + 8(yFinance Columns) + 1(% Change of Avg Cost) = 55 Columns
print(df)
