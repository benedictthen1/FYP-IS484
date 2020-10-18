import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
from datetime import date,time, datetime, timedelta   

import requests 
import json
import threading
from threading import Thread

chat_id = 387218772 # fill in your chat id here
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

summary_info_text = "Here is the current summary info of all the clients!\n\n"+\
    "*X  : poorly performing clients*\n"+\
    "*X  : clients out of risk target*\n"+\
    "*X  : clients to remind*\n\n"

morning_msg_text = "==========\nThis is morning testing message. (Supposed to be sent at 8am)\n"+\
    f"== Server Time Now: {datetime.now().time().hour}hr{datetime.now().time().minute}min ==\n==========\n"+\
    "Good Morning! "+u'\U0001F604'+"\n\n"+\
    summary_info_text + more_details_text +\
    "Have a wonderful day ahead! "+u'\U0001F60A'
    
evening_msg_text = "==========\nThis is evening testing message. (Supposed to be sent at 8pm)\n"+\
    f"== Server Time Now: {datetime.now().time().hour}hr{datetime.now().time().minute}min ==\n==========\n"+\
    "Good Evening! I hope you had a great day! "+u'\U0001F60A'+"\n\n"+\
    summary_info_text + more_details_text +\
    "Have a lovely evening! "+u'\U0001F917'

now = datetime.now()
print("Noti Start Time (hour):",now.time().hour)
send_msg(chat_id, "Hi, I'll be test sending you 2 messages everyday (at 8am and 8pm).")
start_hour = now.time().hour
while True:   
    if start_hour <= 8 or start_hour > 20:
        next_trigger = 8
    else:
        next_trigger = 20
    print("Noti Next Trigger (hour):",next_trigger)
    while now.time().hour != next_trigger:
        now = datetime.now()
    print("Noti Trigger Time Now:",now.time())
    if now.time().hour == 8:
        send_msg(chat_id, morning_msg_text)
        start_hour = 20
    elif now.time().hour == 20:
        send_msg(chat_id, evening_msg_text)
        start_hour = 8
    







