import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
from datetime import date,time, datetime, timedelta   

import requests 
import json
import threading
from threading import Thread

evening_time_string = "5pm"

def return_values_for_tele_msg():
    ############ Import all data files #################
    print("Importing for latest data...")
    df = pd.read_csv('Client.csv')
    risk_df = pd.read_csv('RiskLevelsAllocation.csv')
    ####################################################

    ############ DateTime conversion #################
    df['Position As of Date'] = pd.to_datetime(df['Position As of Date'], errors='coerce').dt.strftime('%d/%m/%Y')
    df['Position As of Date']= pd.to_datetime(df['Position As of Date'])
    df['Maturity'] = pd.to_datetime(df['Maturity'], errors='coerce').dt.strftime('%d/%m/%Y')
    df['Maturity']= pd.to_datetime(df['Maturity'])
    df['Next Call Date'] = pd.to_datetime(df['Next Call Date'], errors='coerce').dt.strftime('%d/%m/%Y')
    df['Next Call Date']= pd.to_datetime(df['Next Call Date'])
    df['Dividend EX Date'] = pd.to_datetime(df['Dividend EX Date'], errors='coerce').dt.strftime('%m/%d/%Y')
    df['Dividend EX Date']= pd.to_datetime(df['Dividend EX Date'])
    ####################################################

    latest_date = df["Position As of Date"].max()
    latest_client_data = df[df['Position As of Date'] == latest_date]

    ################# Data Processing for Poorly Performing Client Information #########################
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

    group_by_PL_asset_class = Profit_Loss_df\
    .groupby(['Client Name'], as_index=False)\
    .agg({'Estimated Profit/Loss':'sum'})

    # print(group_by_PL_asset_class)
    poorly_performing_client_count = sum(n < 0 for n in group_by_PL_asset_class['Estimated Profit/Loss'].values.flatten())
    ################# End of Data Processing for Poorly Performing Client Information #########################

    ################# Data Processing for Risky Client Information #########################

    latest_client_data["Asset Class"].replace({"Investment Cash & Short Term Investments": "CASH"}, inplace=True)
    risk_asset_classes = ["CASH", "FIXED INCOME", "EQUITIES"]
    risk_analysis_df = latest_client_data[latest_client_data["Asset Class"].isin(risk_asset_classes)]

    group_by_risk_asset_class = risk_analysis_df\
    .groupby(['Client Name','Asset Class'], as_index=True)\
    .agg({'Nominal Amount (USD)':'sum'})
    group_by_risk_asset_class["%"] = group_by_risk_asset_class.groupby(level=0).apply(lambda x:  100*x / x.sum())
    group_by_risk_asset_class = group_by_risk_asset_class.reset_index()
    #print(group_by_risk_asset_class)

    transformed_risk_analysis_df = \
        group_by_risk_asset_class.pivot(index='Client Name', columns='Asset Class', values='%')\
        .fillna(0)
    #print(transformed_risk_analysis_df)
    stacked_risk_analysis_df = transformed_risk_analysis_df.stack().reset_index()
    # rename last column
    stacked_risk_analysis_df.set_axis([*stacked_risk_analysis_df.columns[:-1], 'Current Nominal Amount (%)'], axis=1, inplace=True)
    #print(stacked_risk_analysis_df)

    client_target_risk_df = latest_client_data[["Client Name","Target Risk Level"]]
    client_target_risk_df = client_target_risk_df.drop_duplicates()
    #print(client_target_risk_df)

    stacked_risk_analysis_df = stacked_risk_analysis_df[stacked_risk_analysis_df["Asset Class"] == "EQUITIES"]
    risk_analysis_df = pd.merge(stacked_risk_analysis_df,client_target_risk_df,on="Client Name")
    #print(risk_analysis_df)

    risk_df = risk_df[risk_df["Asset Class"]=="EQUITIES"]
    #print(risk_df)
    risk_analysis_df["Current Risk Level"] = risk_analysis_df['Current Nominal Amount (%)'].apply(lambda x: risk_df.iloc[(risk_df['Breakdown by Percentage']-x).abs().argsort()[:1]]['Level'].iloc[0])
    #print(risk_analysis_df)
    risk_analysis_df['Target Status'] = np.where(risk_analysis_df['Target Risk Level']==risk_analysis_df['Current Risk Level'], 'In Target', 'Out of Target')

    risk_analysis_df['Count'] = 1
    risk_analysis_df = risk_analysis_df['Target Status'].value_counts().to_frame().reset_index()
    out_of_target_client_no = risk_analysis_df.loc[risk_analysis_df['index'] == "Out of Target", 'Target Status'].iloc[0]
    # print(out_of_target_client_no)
    ################# End of Data Processing for Risky Client Information #########################

    ################# Data Processing for Reminders Client Information #########################
    Eq_FI = ["EQUITIES","FIXED INCOME"]
    client_data = latest_client_data[latest_client_data["Asset Class"].isin(Eq_FI)]

    common_columns = ["Client Name","Base Number","Position As of Date","Asset Class","Asset Sub Class","Name","Ticker","CCY","Nominal Units","Nominal Amount (CCY)",
    "Nominal Amount (USD)","Current Price","Closing Price","Average Cost","% Change from Avg Cost","1d %","5d %","1m %","6m %","12m %","YTD%",
    "Sector","Country (Domicile)","Region (Largest Revenue)"]
    equities_columns = ["Citi rating","Citi TARGET","% to target","Market Consensus","12M Div Yield (%)",
    "P/E Ratio","P/B Ratio","EPS (Current Year)","EPS (Next Year)","YoY EPS Growth (%)","50D MA","200D MA","Profit Margin",
    "Company Description"]
    equities_date = ["Dividend EX Date"]
    # "CoCo Action","Duration" are left out in fixed_income_columns because Client.csv do not have them
    fixed_income_columns = ["Rank","Moodys R","S&P R","Fitch","Coupon","YTC","YTM","Coupon type","Issue Date"]
    fixed_income_date = ["Maturity","Next Call Date"]
    reminders_columns = common_columns + equities_columns + fixed_income_columns + equities_date + fixed_income_date
    reminders_columns_without_dates = common_columns + equities_columns + fixed_income_columns

    reminder_df = client_data[reminders_columns]

    melted_reminder_df = reminder_df.melt(id_vars=reminders_columns_without_dates,var_name="Reminder Type",value_name="DateTime")
    melted_reminder_df['Date'] = melted_reminder_df['DateTime'].dt.date

    melted_reminder_df = melted_reminder_df.drop_duplicates()
    today = date.today()
    next_reminder_date =  today + timedelta(weeks=52) # change time accordingly here

    df_next_reminder = melted_reminder_df[(melted_reminder_df['Date'] <= next_reminder_date) & (melted_reminder_df['Date'] >= today)]
    # df_all_reminder = melted_reminder_df[melted_reminder_df['Date'] >= today]

    df_next_reminder = df_next_reminder.drop_duplicates()

    no_of_clients_due_in_1y = len(df_next_reminder["Client Name"].unique())
    df_overdue_reminder = melted_reminder_df[melted_reminder_df['Date'] <= today]

    df_overdue_reminder = df_overdue_reminder.drop_duplicates()
    no_of_clients_overdue = len(df_overdue_reminder["Client Name"].unique())
    ################# End of Data Processing for Reminders Client Information #########################
    return poorly_performing_client_count, out_of_target_client_no, no_of_clients_due_in_1y, no_of_clients_overdue

# chat_id = 387218772 # fill in your chat id here
chat_id = -376934065 # fill in your chat id here
api_token = '1075159647:AAGLjAejPey6VpHyOxAqbUR2tS18BnhXdP4' # fill in your API token here
base_url = 'https://api.telegram.org/bot{}/'.format(api_token)

sendMsg_url = base_url + 'sendMessage'

def send_msg(chat_id, msg_text):

	# write your code here
	params = {'chat_id':chat_id,'text':msg_text,'parse_mode':'markdown'}
	r = requests.post(sendMsg_url, params=params)
	print(r.status_code)
	# print(r.text)
	return r.json()["result"]["message_id"]

more_details_text = "====================\n"+\
    "For more details, please visit:\nhttps://fyp-app-deployment.herokuapp.com\n"+\
    "====================\n"

def return_summary_info_text_w_values(poorly_performing_client_count,out_of_target_client_no,no_of_clients_due_in_1y):
    summary_info_text = "Here is a quick summary info of all the clients!\n\n"+\
        f"*{poorly_performing_client_count}  : poorly performing clients*\n"+\
        f"*{out_of_target_client_no}  : clients out of risk target*\n"+\
        f"*{no_of_clients_due_in_1y}  : clients to remind (for Assets due in 1 year)*\n\n"
    return summary_info_text

def return_morning_msg_text(poorly_performing_client_count,out_of_target_client_no,no_of_clients_due_in_1y):
    morning_msg_text = "Good Morning! "+u'\U0001F604'+"\n\n"+\
        return_summary_info_text_w_values(poorly_performing_client_count,out_of_target_client_no,no_of_clients_due_in_1y) +\
        more_details_text +\
        "Have a wonderful day ahead! "+u'\U0001F60A'
    return morning_msg_text

def return_evening_msg_text(poorly_performing_client_count,out_of_target_client_no,no_of_clients_due_in_1y):
    evening_msg_text = "Good Evening! I hope you had a great day! "+u'\U0001F60A'+"\n\n"+\
        return_summary_info_text_w_values(poorly_performing_client_count,out_of_target_client_no,no_of_clients_due_in_1y) +\
        more_details_text +\
        "Have a lovely evening! "+u'\U0001F917'
    return evening_msg_text

def send_evening_message():
    now = datetime.now()
    print("Noti Trigger Time Now:",now.time())
    poorly_performing_client_count,out_of_target_client_no,no_of_clients_due_in_1y,no_of_clients_overdue = return_values_for_tele_msg()
    evening_msg_text = return_evening_msg_text(poorly_performing_client_count,out_of_target_client_no,no_of_clients_due_in_1y)
    send_msg(chat_id, evening_msg_text)
    # print(f"Evening Message Sent! ServerTime: {datetime.now().time().hour}:{datetime.now().time().minute}:{datetime.now().time().second}")

send_evening_message()







