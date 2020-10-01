import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt

# df = pd.read_csv('../TestDataManipulatedAllCols.csv')

# df['Position As of Date']= pd.to_datetime(df['Position As of Date']) 
# df['Position As of Date'] = df['Position As of Date'].apply(lambda x: dt.datetime.strftime(x, '%Y-%d-%m'))
# df['Position As of Date']= pd.to_datetime(df['Position As of Date']) 
# print(df["Nominal Amount (USD)"].head(3))
# numeric_cols = df.select_dtypes([np.number]).columns.to_list()
# print (numeric_cols)
# decimals = 3    
# df[numeric_cols] = df[numeric_cols].apply(lambda x: round(x, decimals))
# print(df["Nominal Amount (USD)"].head(3))
# client_data = df.loc[df["Client Name"] == "SR004022615"]

# client_data["Asset Class"][client_data["Asset Class"]!="Loans"] = "Others" 
	
# group_by_asset_class = client_data\
# .groupby(['Position As of Date','Asset Class'], as_index=False)\
# .agg({'Nominal Amount (USD)':'sum'})

# this is based on assumption that all other assets other than loan are considered as "assets"
# group_by_asset_class["Asset Class"][group_by_asset_class["Asset Class"]=="Others"] = "Total Assets"
# group_by_asset_class["Asset Class"][group_by_asset_class["Asset Class"]=="Loans"] = "Total Liabilities"

# latest_date = group_by_asset_class["Position As of Date"].max()
# print(type(latest_date))
# latest_data = group_by_asset_class[\
#     group_by_asset_class['Position As of Date'] == latest_date]
# latest_total_cash = latest_data[latest_data["Asset Class"]=="Total Assets"]["Nominal Amount (USD)"].item()
# print(type(latest_total_cash))
# print("${:.3f}M".format(latest_total_cash/1000000))
# latest_total_cash = group_by_asset_class["Nominal Amount (USD)"][group_by_asset_class["Position As of Date"].max() & group_by_asset_class["Asset Class"]=="Others"]
# latest_total_loans = group_by_asset_class["Nominal Amount (USD)"][group_by_asset_class["Position As of Date"].max() & group_by_asset_class["Asset Class"]=="Loans"]

# print(group_by_asset_class["Nominal Amount (USD)"][group_by_asset_class["Position As of Date"].max() & group_by_asset_class["Asset Class"]=="Others"])

