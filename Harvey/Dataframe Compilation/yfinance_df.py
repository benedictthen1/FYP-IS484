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
import numpy as np
from datetime import datetime

def get_client_df():
    #Dash app with SQLAlchemy db query
    engine = create_engine('postgres://plrsqsxfozyrze:74a321364d3ec3d66ae04ea0711455ff1d224c5eb7e4f01d2d9e29dd99dddec8@ec2-34-198-103-34.compute-1.amazonaws.com:5432/dfk757hnbfc8ik')
    return pd.read_sql('SELECT * FROM public.\"Client\"', engine)

def yfinance_update(df):

    equities_common_stock = df.loc[(df['Asset Class'] == "EQUITIES") & (df['Asset Sub Class'] == "Common Stocks")]

    ticker_list = equities_common_stock.Ticker.unique()

    ticker_list = list(filter(None, ticker_list))

    #To be removed during deployment
    print(ticker_list)

    yfinance_list = []
    for ticker in ticker_list:
        ticker_row = [ticker]
        stock = yf.Ticker(ticker)

        #Progress of yfinance_update()
        print(ticker)

        #Include latest price as closing price in ticker_row
        ytd_df = stock.history(period="ytd")['Close']
        ticker_row.append(float(ytd_df[len(stock.history(period="ytd"))-1]))
        ticker_row.append(float(ytd_df[len(stock.history(period="ytd"))-1]))

        #Include YTD% in ticker_row
        to_minus_for_ytd = float(ytd_df[0])
        ticker_row.append(round(((ticker_row[1] / to_minus_for_ytd) - 1 )*100 , 2))

        #Include 1d % in ticker_row
        one_year_df = stock.history(period="1y")['Close']
        one_year_length = len(one_year_df)
        to_minus_for_1d = float(one_year_df[one_year_length-2])
        ticker_row.append(round(((ticker_row[1] / to_minus_for_1d) - 1 )*100 , 2))

        #Include 5d % in ticker_row
        to_minus_for_5d = float(one_year_df[one_year_length-6])
        ticker_row.append(round(((ticker_row[1] / to_minus_for_5d) - 1 )*100 , 2))

        #Include 1m % in ticker_row
        to_minus_for_1mo = float(one_year_df[one_year_length-23])
        ticker_row.append(round(((ticker_row[1] / to_minus_for_1mo) - 1 )*100 , 2))

        #Include 6m % in ticker_row
        to_minus_for_6mo = float(one_year_df[one_year_length-129])
        ticker_row.append(round(((ticker_row[1] / to_minus_for_6mo) - 1 )*100 , 2))

        #Include 12m % in ticker_row
        to_minus_for_12mo = float(one_year_df[0])
        ticker_row.append(round(((ticker_row[1] / to_minus_for_12mo) - 1 )*100 , 2))


        #Include Company Description in ticker_row
        info_df = stock.info
        ticker_row.append(info_df["longBusinessSummary"])

        #Include 12M Dividend Yield % in ticker_row
        ticker_row.append(info_df["trailingAnnualDividendYield"])

        #Include Dividend EX datein ticker_row
        if info_df["exDividendDate"] != None:
            timestamp = datetime.fromtimestamp(info_df["exDividendDate"])
            timestamp = timestamp.strftime("%d/%m/%Y")
            ticker_row.append(timestamp)
        else:
            ticker_row.append(np.nan)


        #Include PE Ratio in ticker_row
        if "trailingPE" in info_df:
            ticker_row.append(info_df["trailingPE"])
        else:
            ticker_row.append(np.nan)

        #Include PB Ratio in ticker_row
        ticker_row.append(info_df["priceToBook"])

        #Include EPS (Current Year) in ticker_row
        if info_df["trailingEps"] != None:
            ticker_row.append(info_df["trailingEps"])
        else:
            ticker_row.append(np.nan)

        #Include EPS (Next Year) in ticker_row
        if info_df["forwardEps"] != None:
            ticker_row.append(info_df["forwardEps"])
        else:
            ticker_row.append(np.nan)

        #Include YoY EPS Growth % in ticker_row
        if info_df["forwardEps"] != None and info_df["trailingEps"] != None: 
            ticker_row.append(round(((info_df["forwardEps"] / info_df["trailingEps"]) - 1 )*100 , 2))
        else:
            ticker_row.append(np.nan)

        #Include 50D MA in ticker_row
        ticker_row.append(info_df["fiftyDayAverage"])

        #Include 200D MA in ticker_row
        ticker_row.append(info_df["twoHundredDayAverage"])

        #Include profit margin in ticker_row
        ticker_row.append(info_df["profitMargins"])

        #Include sector in ticker_row
        if "sector" in info_df:
            ticker_row.append(info_df["sector"])
        else:
            ticker_row.append(np.nan)

        #Include country in ticker_row
        if "country" in info_df:
            ticker_row.append(info_df["country"])
        else:
            ticker_row.append(np.nan)

        #Compile to yFinance list
        yfinance_list.append(ticker_row)

    # ,'YTD%','1d %','5d %','1m %','6m %','12m %','Company Description'
    yfinance_df = pd.DataFrame(yfinance_list,columns=['Ticker','Current Price','Closing Price','YTD%','1d %','5d %','1m %','6m %','12m %','Company Description',"12M Div Yield (%)","Dividend EX Date","P/E Ratio","P/B Ratio","EPS (Current Year)","EPS (Next Year)","YoY EPS Growth (%)","50D MA","200D MA","Profit Margin","Sector","Country (Domicile)"])

    #Merge and drop extra columns
    df = df.merge(yfinance_df, on='Ticker', how='left')

    df['Current Price'] = df['Current Price_y'].fillna(df['Current Price_x'])

    df['Closing Price'] = df['Closing Price_y'].fillna(df['Closing Price_x'])

    df['YTD%'] = df['YTD%_y'].fillna(df['YTD%_x'])

    df['1d %'] = df['1d %_y'].fillna(df['1d %_x'])

    df['5d %'] = df['5d %_y'].fillna(df['5d %_x'])

    df['1m %'] = df['1m %_y'].fillna(df['1m %_x'])

    df['6m %'] = df['6m %_y'].fillna(df['6m %_x'])

    df['12m %'] = df['12m %_y'].fillna(df['12m %_x'])

    df['Company Description'] = df['Company Description_y'].fillna(df['Company Description_x'])

    df['12M Div Yield (%)'] = df['12M Div Yield (%)_y'].fillna(df['12M Div Yield (%)_x'])

    df['Dividend EX Date'] = df['Dividend EX Date_y'].fillna(df['Dividend EX Date_x'])

    df['P/E Ratio'] = df['P/E Ratio_y'].fillna(df['P/E Ratio_x'])

    df['P/B Ratio'] = df['P/B Ratio_y'].fillna(df['P/B Ratio_x'])

    df['EPS (Current Year)'] = df['EPS (Current Year)_y'].fillna(df['EPS (Current Year)_x'])

    df['EPS (Next Year)'] = df['EPS (Next Year)_y'].fillna(df['EPS (Next Year)_x'])

    df['YoY EPS Growth (%)'] = df['YoY EPS Growth (%)_y'].fillna(df['YoY EPS Growth (%)_x'])

    df['50D MA'] = df['50D MA_y'].fillna(df['50D MA_x'])

    df['200D MA'] = df['200D MA_y'].fillna(df['200D MA_x'])

    df['Profit Margin'] = df['Profit Margin_y'].fillna(df['Profit Margin_x'])

    df['Sector'] = df['Sector_y'].fillna(df['Sector_x'])

    df['Country (Domicile)'] = df['Country (Domicile)_y'].fillna(df['Country (Domicile)_x'])

    df = df[df.columns.drop(list(df.filter(regex='_y')))]

    df = df[df.columns.drop(list(df.filter(regex='_x')))]

    #Update % Change from Avg cost
    df['% Change from Avg Cost']=(df['Current Price'].astype("float")-df['Average Cost'].astype("float"))/df['Average Cost'].astype("float")*100

    #Update % to target
    df['% to target'] = np.where(pd.to_numeric(df['Citi TARGET']) != None, (pd.to_numeric(df['Citi TARGET'])-df['Current Price'].astype("float"))/df['Current Price'].astype("float")*100,np.nan)

    #Update Citi Rating
    df['Citi rating'] = np.where(abs(df['% to target']) < 0.1, "neutral",np.where(abs(df['% to target']) > 0, "buy","sell"))

    return df

def get_risk_allocation_df():
    #Dash app with SQLAlchemy db query
    engine = create_engine('postgres://plrsqsxfozyrze:74a321364d3ec3d66ae04ea0711455ff1d224c5eb7e4f01d2d9e29dd99dddec8@ec2-34-198-103-34.compute-1.amazonaws.com:5432/dfk757hnbfc8ik')
    return pd.read_sql('SELECT * FROM public.\"RiskAllocation\"', engine)

#To be removed in deployment
df = get_client_df()
df = yfinance_update(df)
risk_df = get_risk_allocation_df()
print(df)
print(risk_df)