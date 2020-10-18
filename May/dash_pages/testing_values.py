import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
from datetime import date, timedelta   

# def format(val):
#     a = pd.to_datetime(val, errors='coerce', cache=False).strftime('%m/%d/%Y')
#     try:
#         date_time_obj = datetime.datetime.strptime(a, '%d/%m/%Y')
#     except:
#         date_time_obj = datetime.datetime.strptime(a, '%m/%d/%Y')
#     return date_time_obj.date()

# df = pd.read_csv('../Client.csv')
# position_date = df['Position As of Date'].loc[0]
# df[['Position As of Date','Maturity','Next Call Date']] = df[['Position As of Date','Maturity','Next Call Date']].apply(pd.to_datetime)
# #print(df[['Position As of Date','Maturity','Next Call Date']])

# ex_div_date = df['Dividend EX Date'].loc[50]
# print(ex_div_date)
# # df['Dividend EX Date1'] = df['Dividend EX Date'].dt.strftime('%m/%d/%Y')
# # print(df.dtypes)

# # df['Dividend EX Date1'] = pd.to_datetime(df['Dividend EX Date1'])
# # print(df.dtypes)

# # df['Dividend EX Date'] = df['Dividend EX Date'].apply(lambda x: format(x))

# df['Dividend EX Date'] = pd.to_datetime(df['Dividend EX Date'], errors='coerce').dt.strftime('%m/%d/%Y')
# df['Dividend EX Date']= pd.to_datetime(df['Dividend EX Date'])
# # print(df['Dividend EX Date'].head())
# # ex_div_date = df['Dividend EX Date'].loc[50]
# # position_date = df['Position As of Date'].loc[0]
# # maturity_date = df['Next Call Date'].loc[53]
# # print(ex_div_date, position_date,maturity_date)

# # not_null_boolean = pd.notnull(df["Next Call Date"])
# # next_call_df = df[not_null_boolean]
# # print(df["Position As of Date"].head())


# Eq_FI = ["EQUITIES","FIXED INCOME"]
# df = df[df["Asset Class"].isin(Eq_FI)]
# common_columns = ["Client Name","Base Number","Position As of Date","Asset Class","Asset Sub Class","Name","Ticker","CCY","Nominal Units","Nominal Amount (CCY)",
# "Nominal Amount (USD)","Current Price","Closing Price","Average Cost","% Change from Avg Cost","1d %","5d %","1m %","6m %","12m %","YTD%",
# "Sector","Country (Domicile)","Region (Largest Revenue)"]
# equities_columns = ["Citi rating","Citi TARGET","% to target","Market Consensus","12M Div Yield (%)",
# "P/E Ratio","P/B Ratio","EPS (Current Year)","EPS (Next Year)","YoY EPS Growth (%)","50D MA","200D MA","Profit Margin",
# "Company Description"]
# equities_date = ["Dividend EX Date"]
# # "CoCo Action","Duration" are left out in fixed_income_columns because Client.csv do not have them
# fixed_income_columns = ["Rank","Moodys R","S&P R","Fitch","Coupon","YTC","YTM","Coupon type","Issue Date"]
# fixed_income_date = ["Maturity","Next Call Date"]
# reminders_columns = common_columns + equities_columns + fixed_income_columns + equities_date + fixed_income_date
# reminders_columns_without_dates = common_columns + equities_columns + fixed_income_columns
# print(len(reminders_columns))

# df = df[reminders_columns]
# print(df.shape)

# # client_data = df.loc[df["Client Name"] == 'SR250824955']
# client_data = df.loc[df["Client Name"] == 'SR004022615']

# # latest_date = client_data["Position As of Date"].max()
# # latest_client_data = client_data[client_data['Position As of Date'] == latest_date]
# #print(latest_client_data)

# # melted_df = latest_client_data.melt(id_vars=reminders_columns_without_dates,var_name="Reminder Type",value_name="Date")
# melted_df = client_data.melt(id_vars=reminders_columns_without_dates,var_name="Reminder Type",value_name="Date")
# print(melted_df)
# # melted_df.to_csv (r'C:\Users\User\Desktop\melted_df_not_latest.csv', index = False, header=True)

# today = date.today()
# next_week_date =  today + timedelta(weeks=4) # change time accordingly here
# # last_week_date =  today - timedelta(weeks=8)

# df_next_week = melted_df[(melted_df['Date'].dt.date <= next_week_date) & (melted_df['Date'].dt.date >= today)]
# # df_last_week = df[(df['Dividend EX Date'].dt.date >= last_week_date) & (df['Dividend EX Date'].dt.date <= today)]
# count = len(df_next_week.index)
# print(today)
# print(next_week_date)
# print(df_next_week)
# print(count)

# all_list = ["ALTERNATIVES",]
# Eq_FI = ["EQUITIES","FIXED INCOME"]

# if any(i in all_list for i in Eq_FI):
#     print("exists")
# else:
#     print("not exist")

# df = pd.DataFrame({
#     'brand': ['Yum Yum', 'Yum Yum', 'Indomie', 'Indomie', 'Indomie'],
#     'style': ['cup', 'cup', 'cup', 'pack', 'pack'],
#     'rating': [4, 4, 3.5, 15, 5]
# })

# print(df)
# df = df.drop_duplicates()
# print(df)
df = pd.read_csv('../Client.csv')
risk_df = pd.read_csv('../RiskLevelsAllocation.csv')

df['Position As of Date'] = pd.to_datetime(df['Position As of Date'], errors='coerce').dt.strftime('%d/%m/%Y')
df['Position As of Date']= pd.to_datetime(df['Position As of Date'])
df['Maturity'] = pd.to_datetime(df['Maturity'], errors='coerce').dt.strftime('%d/%m/%Y')
df['Maturity']= pd.to_datetime(df['Maturity'])
df['Next Call Date'] = pd.to_datetime(df['Next Call Date'], errors='coerce').dt.strftime('%d/%m/%Y')
df['Next Call Date']= pd.to_datetime(df['Next Call Date'])
df['Dividend EX Date'] = pd.to_datetime(df['Dividend EX Date'], errors='coerce').dt.strftime('%m/%d/%Y')
df['Dividend EX Date']= pd.to_datetime(df['Dividend EX Date'])

latest_date = df["Position As of Date"].max()
latest_client_data = df[df['Position As of Date'] == latest_date]

# Eq_FI = ["EQUITIES","FIXED INCOME"]
# client_data = latest_client_data[latest_client_data["Asset Class"].isin(Eq_FI)]

# common_columns = ["Client Name","Base Number","Position As of Date","Asset Class","Asset Sub Class","Name","Ticker","CCY","Nominal Units","Nominal Amount (CCY)",
# "Nominal Amount (USD)","Current Price","Closing Price","Average Cost","% Change from Avg Cost","1d %","5d %","1m %","6m %","12m %","YTD%",
# "Sector","Country (Domicile)","Region (Largest Revenue)"]
# equities_columns = ["Citi rating","Citi TARGET","% to target","Market Consensus","12M Div Yield (%)",
# "P/E Ratio","P/B Ratio","EPS (Current Year)","EPS (Next Year)","YoY EPS Growth (%)","50D MA","200D MA","Profit Margin",
# "Company Description"]
# equities_date = ["Dividend EX Date"]
# # "CoCo Action","Duration" are left out in fixed_income_columns because Client.csv do not have them
# fixed_income_columns = ["Rank","Moodys R","S&P R","Fitch","Coupon","YTC","YTM","Coupon type","Issue Date"]
# fixed_income_date = ["Maturity","Next Call Date"]
# reminders_columns = common_columns + equities_columns + fixed_income_columns + equities_date + fixed_income_date
# reminders_columns_without_dates = common_columns + equities_columns + fixed_income_columns

# reminder_df = client_data[reminders_columns]

# melted_reminder_df = reminder_df.melt(id_vars=reminders_columns_without_dates,var_name="Reminder Type",value_name="DateTime")
# melted_reminder_df['Date'] = melted_reminder_df['DateTime'].dt.date

# melted_reminder_df = melted_reminder_df.drop_duplicates()
# today = date.today()
# next_reminder_date =  today + timedelta(weeks=52) # change time accordingly here
# # time_string = "1 Year" # change accordingly here also

# df_next_reminder = melted_reminder_df[(melted_reminder_df['Date'] <= next_reminder_date) & (melted_reminder_df['Date'] >= today)]
# # df_all_reminder = melted_reminder_df[melted_reminder_df['Date'] >= today]
# # df_next_reminder = df_next_reminder[["Name","Reminder Type","Date"]]
# # print(df_next_reminder)
# df_next_reminder = df_next_reminder.drop_duplicates()
# print(df_next_reminder["Date"].unique())
# print(len(df_next_reminder["Client Name"].unique()))
# df_overdue_reminder = melted_reminder_df[melted_reminder_df['Date'] <= today]

# df_overdue_reminder = df_overdue_reminder.drop_duplicates()
# print(len(df_overdue_reminder["Client Name"].unique()))


################ Profit/Loss Breakdown ####################

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

# decimals = 3
# Profit_Loss_df['Estimated Profit/Loss'] = Profit_Loss_df['Estimated Profit/Loss'].apply(lambda x: round(x, decimals))
# #print(Profit_Loss_df.head())
# total_profit_loss = Profit_Loss_df['Estimated Profit/Loss'].sum()

group_by_PL_asset_class = Profit_Loss_df\
.groupby(['Client Name'], as_index=False)\
.agg({'Estimated Profit/Loss':'sum'})

print(group_by_PL_asset_class)
negative_client_count = sum(n < 0 for n in group_by_PL_asset_class['Estimated Profit/Loss'].values.flatten())
print(negative_client_count)