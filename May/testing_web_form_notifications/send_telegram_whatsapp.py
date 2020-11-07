import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
from datetime import datetime, date, timedelta

import os

###### global variables ######
first_time_threshold_set_check = True
##############################

#### For WhatsApp ####
from twilio.rest import Client 

account_sid = 'ACb57b07af4c72e89c16a87a2341d26a32' 
auth_token = '3b773f9bc3be631a33dfea84b2dc4110' 
client = Client(account_sid, auth_token) 

def send_whatsapp_message(msg_text):
    message = client.messages.create( 
                                from_='whatsapp:+14155238886',  
                                body=msg_text,      
                                to='whatsapp:+6596159059' 
                            ) 
    
    print("WhatsApp sid :", message.sid)

#### End of - For WhatsApp ####

#### For Telegram ####
import requests 
import json

# chat_id = 387218772 # fill in your chat id here
chat_id = -376934065 # fill in your chat id here
api_token = '1075159647:AAGLjAejPey6VpHyOxAqbUR2tS18BnhXdP4' # fill in your API token here
base_url = 'https://api.telegram.org/bot{}/'.format(api_token)

sendMsg_url = base_url + 'sendMessage'

def send_telegram_message(msg_text):

	# write your code here
	params = {'chat_id':chat_id,'text':msg_text,'parse_mode':'markdown'}
	r = requests.post(sendMsg_url, params=params)
	print("Telegram :", r.status_code)
	# print(r.text)
	return r.json()["result"]["message_id"]
#### End of - For Telegram ####

#### is_thresholds_set Function checks if the threshold values have been set to monitor ####
def is_thresholds_set():
    if not os.path.exists('set_values_df.csv'):
        set_values_df = pd.DataFrame.from_dict(
            {
                "Asset Type": ["Equities", "Fixed Income", "Alternatives"],
                "Column Set": [],
                "Filter Condition": [],
                "Percentage Amount Set": [],
            }, orient='index'
        )
        set_values_df = set_values_df.transpose()
        now = datetime.now()
        now = now - timedelta(microseconds=now.microsecond)
        set_values_df["Time Updated"] = now
        set_values_df.to_csv(r"set_values_df.csv", index = False)
        return False

    print("Importing for latest set_values_df...")
    set_values_df = pd.read_csv('set_values_df.csv')
    check_no_of_nulls = set_values_df["Column Set"].isnull().sum()
    print("No. of values NOT set:",set_values_df["Column Set"].isnull().sum())
    if check_no_of_nulls != 3:
        return True
    return False
#### End of - is_thresholds_set Function ####


#### is_same_as_last_updated_lists Function checks if current results are same as last updated results ####
def is_same_as_last_updated_lists(current_eq_companies_list, current_fi_companies_list, current_al_clients_list):
    current_eq_companies_list.sort()
    current_fi_companies_list.sort()
    current_al_clients_list.sort()

    if not os.path.exists('last_updated_values_df.csv'):
        last_updated_values_df = pd.DataFrame.from_dict(
            {
                "Equities List": current_eq_companies_list,
                "Fixed Income List": current_fi_companies_list,
                "Alternatives List": current_al_clients_list,
            }, orient='index'
        )
        last_updated_values_df = last_updated_values_df.transpose()
        last_updated_values_df.to_csv(r"last_updated_values_df.csv", index = False)
        return False
    
    last_updated_values_df = pd.read_csv('last_updated_values_df.csv')

    latest_equities_clients_list = last_updated_values_df["Equities List"].tolist()
    latest_fixed_income_clients_list = last_updated_values_df["Fixed Income List"].tolist()
    latest_alternatives_clients_list = last_updated_values_df["Alternatives List"].tolist()

    latest_equities_clients_list = [x for x in latest_equities_clients_list if str(x) != 'nan']
    latest_fixed_income_clients_list = [x for x in latest_fixed_income_clients_list if str(x) != 'nan']
    latest_alternatives_clients_list = [x for x in latest_alternatives_clients_list if str(x) != 'nan']

    if ((current_eq_companies_list == latest_equities_clients_list) & (current_fi_companies_list == latest_fixed_income_clients_list) & (current_al_clients_list == latest_alternatives_clients_list)):
        return True
    else:
        last_updated_values_df = pd.DataFrame.from_dict(
            {
                "Equities List": latest_equities_clients_list,
                "Fixed Income List": latest_fixed_income_clients_list,
                "Alternatives List": latest_alternatives_clients_list
            }, orient='index'
        )
        last_updated_values_df = last_updated_values_df.transpose()
        last_updated_values_df.to_csv(r"last_updated_values_df.csv", index = False)
        return False
    
#### End of - is_same_as_last_updated_lists Function ####

#### return_filtered_df Function that returns filtered df based on asset_type,column_name,condition,value set in web form ####
def return_filtered_df(df,asset_type,column_name,condition,value):
    excel_asset_type_mapping = {
        "Equities": "EQUITIES",
        "Fixed Income": "FIXED INCOME",
        "Alternatives": "ALTERNATIVE INVESTMENTS",
        }
    selected_asset_type = excel_asset_type_mapping[asset_type]
    
    df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
    df = df.dropna(subset=[column_name])
  
    conditions_dict = {
        "equal to": df[(df["Asset Class"] == selected_asset_type) & (df[column_name] == value)],
        "less than": df[(df["Asset Class"] == selected_asset_type) & (df[column_name] < value)],
        "less than or equal to": df[(df["Asset Class"] == selected_asset_type) & (df[column_name] <= value)],
        "greater than": df[(df["Asset Class"] == selected_asset_type) & (df[column_name] > value)],
        "greater than or equal to": df[(df["Asset Class"] == selected_asset_type) & (df[column_name] >= value)],
        }
    
    new_df = conditions_dict[condition]
    return new_df

#### End of - return_filtered_df Function ####

#### return_values_for_msg Function: imports lastest data and returns the three lists and three values ####
def return_values_for_msg():
    ############ Import all data files #################
    print("Importing for latest Client data...")
    client_df = pd.read_csv('Client.csv')
    print("Importing for latest set_values_df...")
    set_values_df = pd.read_csv('set_values_df.csv')
    ####################################################

    ############ DateTime conversion ###################
    client_df['Position As of Date'] = pd.to_datetime(client_df['Position As of Date'], errors='coerce').dt.strftime('%d/%m/%Y')
    client_df['Position As of Date']= pd.to_datetime(client_df['Position As of Date'])
    ####################################################

    ############ Get latest data ###################
    latest_date = client_df["Position As of Date"].max()
    latest_client_data = client_df[client_df['Position As of Date'] == latest_date]
    ################################################

    if pd.isnull(set_values_df["Column Set"][0]):
        no_of_companies_affected_in_equities = "-"
        eq_companies_list = []
    else:
        eq_df = return_filtered_df(latest_client_data,set_values_df["Asset Type"][0],set_values_df["Column Set"][0],set_values_df["Filter Condition"][0],set_values_df["Percentage Amount Set"][0])
        eq_companies_list = eq_df["Name"].unique().tolist()
        no_of_companies_affected_in_equities = len(eq_df["Name"].unique())
    if pd.isnull(set_values_df["Column Set"][1]):
        no_of_companies_affected_in_fixedincome = "-"
        fi_companies_list = []
    else:
        fi_df = return_filtered_df(latest_client_data,set_values_df["Asset Type"][1],set_values_df["Column Set"][1],set_values_df["Filter Condition"][1],set_values_df["Percentage Amount Set"][1])
        fi_companies_list = fi_df["Name"].unique().tolist()
        no_of_companies_affected_in_fixedincome = len(fi_df["Name"].unique())
    if  pd.isnull(set_values_df["Column Set"][2]):
        no_of_clients_affected_in_alternatives = "-"
        al_clients_list = []
    else:
        al_df = return_filtered_df(latest_client_data,set_values_df["Asset Type"][2],set_values_df["Column Set"][2],set_values_df["Filter Condition"][2],set_values_df["Percentage Amount Set"][2])
        al_clients_list = al_df["Client Name"].unique().tolist()
        no_of_clients_affected_in_alternatives = len(al_df["Client Name"].unique())
    print(no_of_companies_affected_in_equities, no_of_companies_affected_in_fixedincome, no_of_clients_affected_in_alternatives)
    return eq_companies_list, fi_companies_list, al_clients_list, no_of_companies_affected_in_equities, no_of_companies_affected_in_fixedincome, no_of_clients_affected_in_alternatives
#### End of - return_values_for_msg Function ####

######### text message format to send #########
more_details_text = "====================\n"+\
    "For more details, please visit:\nhttps://fyp-app-deployment.herokuapp.com\n"+\
    "====================\n"

to_set_threshold_text = "====================\n"+\
    "To set thresholds for monitoring, please visit:\nhttps://fyp-app-deployment.herokuapp.com\n"+\
    "====================\n"

def return_monitoring_info_text_w_values(eq_companies_no, fi_companies_no, al_clients_no):
    monitoring_info_text = "Here is a quick monitoring info of all the clients!\n\n"+\
        f"*{eq_companies_no}*  : companies affected by Equities threshold\n"+\
        f"*{fi_companies_no}*  : companies affected by Fixed Income threshold\n"+\
        f"*{al_clients_no}*  : clients affected by Alternatives threshold\n\n"
    return monitoring_info_text

def return_normal_msg_text(eq_companies_no, fi_companies_no, al_clients_no):
    normal_msg_text = "❗️*Monitoring Alert*❗️\n\n"+\
        return_monitoring_info_text_w_values(eq_companies_no, fi_companies_no, al_clients_no) +\
        more_details_text +\
        "Have a great day! "+u'\U0001F917'
    return normal_msg_text

def return_no_threshold_msg_text():
    no_threshold_msg_text = "Good Day! "+u'\U0001F60A'+"\n\n"+\
        "_No threshold values have been set to monitor yet._\n\n" +\
        to_set_threshold_text +\
        "Have a great day! "+u'\U0001F917'
    return no_threshold_msg_text
######### End of - text message format to send #########

def send_to_telegram_whatsapp():
    if is_thresholds_set():
        eq_companies_list, fi_companies_list, al_clients_list, eq_companies_no, fi_companies_no, al_clients_no = return_values_for_msg()
        if not is_same_as_last_updated_lists(eq_companies_list, fi_companies_list, al_clients_list):
            normal_msg_text = return_normal_msg_text(eq_companies_no, fi_companies_no, al_clients_no)
            send_whatsapp_message(normal_msg_text)
            send_telegram_message(normal_msg_text)
            print(f"Normal Monitoring Alert Sent! ServerTime: {datetime.now().time().hour}:{datetime.now().time().minute}:{datetime.now().time().second}")
    else:
        global first_time_threshold_set_check
        if first_time_threshold_set_check:
            no_threshold_msg_text = return_no_threshold_msg_text()
            send_whatsapp_message(no_threshold_msg_text)
            send_telegram_message(no_threshold_msg_text)
            print(f"No Threshold Set Msg Sent! ServerTime: {datetime.now().time().hour}:{datetime.now().time().minute}:{datetime.now().time().second}")
            first_time_threshold_set_check = False

