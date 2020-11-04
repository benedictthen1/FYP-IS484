import dash
import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
from datetime import datetime, date, timedelta

###### global variables ######
morning_time_string = "8 am"
evening_time_string = "5 pm"
##############################

#### For WhatsApp ####
from twilio.rest import Client 

account_sid = 'ACb57b07af4c72e89c16a87a2341d26a32' 
auth_token = '2012586a77273c845da7a014c8aec217' 
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

chat_id = 387218772 # fill in your chat id here
# chat_id = -376934065 # fill in your chat id here
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
#### End of - For WhatsApp ####

#### is_thresholds_set Function checks if the threshold values have been set to monitor ####
def is_thresholds_set():
    print("Importing for latest set_values_df...")
    set_values_df = pd.read_csv('set_values_df.csv')
    check_no_of_nulls = set_values_df["Column Set"].isnull().sum()
    print(set_values_df["Column Set"].isnull().sum())
    if check_no_of_nulls != 3:
        return True
    return False
#### End of - is_thresholds_set Function ####

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

#### return_values_for_msg Function: imports lastest data and  ####
def return_values_for_msg():
    ############ Import all data files #################
    print("Importing for latest Client data...")
    client_df = pd.read_csv('Client.csv')
    print("Importing for latest set_values_df...")
    set_values_df = pd.read_csv('set_values_df.csv')
    print(set_values_df)
    print(set_values_df["Column Set"].isnull().sum())
    ####################################################

    ############ DateTime conversion ###################
    client_df['Position As of Date'] = pd.to_datetime(client_df['Position As of Date'], errors='coerce').dt.strftime('%d/%m/%Y')
    client_df['Position As of Date']= pd.to_datetime(client_df['Position As of Date'])
    ####################################################

    ############ Get latest data ###################
    latest_date = client_df["Position As of Date"].max()
    latest_client_data = client_df[client_df['Position As of Date'] == latest_date]
    ################################################

    # print(type(set_values_df["Percentage Amount Set"][0]))
    eq_df = return_filtered_df(latest_client_data,set_values_df["Asset Type"][0],set_values_df["Column Set"][0],set_values_df["Filter Condition"][0],set_values_df["Percentage Amount Set"][0])
    print("Equities Clients List:",eq_df["Client Name"].unique().tolist())
    no_of_clients_affected_in_equities = len(eq_df["Client Name"].unique())
    fi_df = return_filtered_df(latest_client_data,set_values_df["Asset Type"][1],set_values_df["Column Set"][1],set_values_df["Filter Condition"][1],set_values_df["Percentage Amount Set"][1])
    print("Fixed Income Clients List:",fi_df["Client Name"].unique().tolist())
    no_of_clients_affected_in_fixedincome = len(fi_df["Client Name"].unique())
    al_df = return_filtered_df(latest_client_data,set_values_df["Asset Type"][2],set_values_df["Column Set"][2],set_values_df["Filter Condition"][2],set_values_df["Percentage Amount Set"][2])
    print("Alternatives Clients List:",al_df["Client Name"].unique().tolist())
    no_of_clients_affected_in_alternatives = len(al_df["Client Name"].unique())

    return no_of_clients_affected_in_equities, no_of_clients_affected_in_fixedincome, no_of_clients_affected_in_alternatives


######### text message format to send #########
more_details_text = "====================\n"+\
    "For more details, please visit:\nhttps://fyp-app-deployment.herokuapp.com\n"+\
    "====================\n"

to_set_threshold_text = "====================\n"+\
    "To set thresholds for monitoring, please visit:\nhttps://fyp-app-deployment.herokuapp.com\n"+\
    "====================\n"

def return_monitoring_info_text_w_values(eq_client_no, fi_client_no, al_client_no):
    monitoring_info_text = "Here is a quick monitoring info of all the clients!\n\n"+\
        f"*{eq_client_no}*  : clients affected by Equities threshold\n"+\
        f"*{fi_client_no}*  : clients affected by Fixed Income threshold\n"+\
        f"*{al_client_no}*  : clients affected by Alternatives threshold\n\n"
    return monitoring_info_text

def return_morning_msg_text(eq_client_no, fi_client_no, al_client_no):
    morning_msg_text = f"==========\nThis is morning testing message. (Supposed to be sent at {morning_time_string})\n"+\
        f"== Server Time Now: {datetime.now().time().hour}hr{datetime.now().time().minute}min ==\n==========\n"+\
        "Good Morning! "+u'\U0001F604'+"\n\n"+\
        return_monitoring_info_text_w_values(eq_client_no, fi_client_no, al_client_no) +\
        more_details_text +\
        "Have a wonderful day ahead! "+u'\U0001F60A'
    return morning_msg_text

def return_evening_msg_text(eq_client_no, fi_client_no, al_client_no):
    evening_msg_text = f"==========\nThis is evening testing message. (Supposed to be sent at {evening_time_string})\n"+\
        f"== Server Time Now: {datetime.now().time().hour}hr{datetime.now().time().minute}min ==\n==========\n"+\
        "Good Evening! I hope you had a great day! "+u'\U0001F60A'+"\n\n"+\
        return_monitoring_info_text_w_values(eq_client_no, fi_client_no, al_client_no) +\
        more_details_text +\
        "Have a lovely evening! "+u'\U0001F917'
    return evening_msg_text

def return_normal_msg_text(eq_client_no, fi_client_no, al_client_no):
    normal_msg_text = f"==========\nThis is normal testing message.\n"+\
        f"== Server Time Now: {datetime.now().time().hour}hr{datetime.now().time().minute}min ==\n==========\n"+\
        "Good Day! "+u'\U0001F60A'+"\n\n"+\
        return_monitoring_info_text_w_values(eq_client_no, fi_client_no, al_client_no) +\
        more_details_text +\
        "Have a great day! "+u'\U0001F917'
    return normal_msg_text

def return_no_threshold_msg_text():
    no_threshold_msg_text = f"==========\nThis is no thresholds set testing message.\n"+\
        f"== Server Time Now: {datetime.now().time().hour}hr{datetime.now().time().minute}min ==\n==========\n"+\
        "Good Day! "+u'\U0001F60A'+"\n\n"+\
        "_No threshold values have been set to monitor yet._\n\n" +\
        to_set_threshold_text +\
        "Have a great day! "+u'\U0001F917'
    return no_threshold_msg_text

######### End of - text message format to send #########

######### Testing ###########
if is_thresholds_set():
    eq_client_no, fi_client_no, al_client_no = return_values_for_msg()
    print(eq_client_no, fi_client_no, al_client_no)
    normal_msg_text = return_normal_msg_text(eq_client_no, fi_client_no, al_client_no)
    send_whatsapp_message(normal_msg_text)
    send_telegram_message(normal_msg_text)
else:
    no_threshold_msg_text = return_no_threshold_msg_text()
    send_whatsapp_message(no_threshold_msg_text)
    send_telegram_message(no_threshold_msg_text)

    