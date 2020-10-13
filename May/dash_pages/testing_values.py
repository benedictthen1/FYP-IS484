import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt

df = pd.read_csv('../Client.csv')

df['Position As of Date']= pd.to_datetime(df['Position As of Date']) 
# df['Position As of Date'] = df['Position As of Date'].apply(lambda x: dt.datetime.strftime(x, '%Y-%d-%m'))
# df['Position As of Date']= pd.to_datetime(df['Position As of Date']) 

# client_data = df.loc[df["Client Name"] == 'SR004022615']
# base_numbers = list(client_data["Base Number"].unique())
# print(base_numbers)

latest_date = df["Position As of Date"].max()
latest_client_data = df[df['Position As of Date'] == latest_date]

Eq_FI = ["EQUITIES","FIXED INCOME"]
Eq_FI_df = latest_client_data[latest_client_data["Asset Class"].isin(Eq_FI)]
Alt_df = latest_client_data[latest_client_data["Asset Class"]=="ALTERNATIVE INVESTMENTS"]

Eq_FI_df = Eq_FI_df[["Client Name","Base Number","Asset Class","Estimated Profit/Loss"]]
Alt_df = Alt_df[["Client Name","Base Number","Asset Class","Distribution Amount","Estimated Profit/Loss"]]

Alt_Distribution_boolean = pd.notnull(Alt_df["Distribution Amount"])
Alt_Distribution_df = Alt_df[Alt_Distribution_boolean]
#print(Alt_Distribution_df.tail())
Alt_Distribution_df = Alt_Distribution_df[["Client Name","Base Number","Asset Class","Distribution Amount"]][Alt_Distribution_df["Distribution Amount"]!=0]
#print(Alt_Distribution_df.tail())
Alt_Distribution_df.rename(columns={"Distribution Amount": "Estimated Profit/Loss"}, inplace=True)
#print(Eq_FI_df.shape)
#print(Alt_Distribution_df.shape)

Alt_Profit_Loss_boolean = pd.isnull(Alt_df["Distribution Amount"])
Alt_Profit_Loss_NA_df = Alt_df[["Client Name","Base Number","Asset Class","Estimated Profit/Loss"]][Alt_Profit_Loss_boolean]
#print(Alt_Profit_Loss_NA_df.shape)
Alt_Profit_Loss_zero_df = Alt_df[["Client Name","Base Number","Asset Class","Estimated Profit/Loss"]][Alt_df["Distribution Amount"]==0]
#print(Alt_Profit_Loss_zero_df.shape)

frames = [Eq_FI_df,Alt_Distribution_df,Alt_Profit_Loss_NA_df,Alt_Profit_Loss_zero_df]
Profit_Loss_df = pd.concat(frames,ignore_index=True)
#print(Profit_Loss_df.tail())
#print(Profit_Loss_df.shape)

decimals = 3
Profit_Loss_df['Estimated Profit/Loss'] = Profit_Loss_df['Estimated Profit/Loss'].apply(lambda x: round(x, decimals))
#print(Profit_Loss_df.head())