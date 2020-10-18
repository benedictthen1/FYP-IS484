import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
from datetime import date,time, datetime, timedelta   

import requests 
import json
# import time
# from time import sleep
import threading
from threading import Thread

# chat_id = 387218772 # fill in your chat id here
chat_id = -376934065 # fill in your chat id here
api_token = '1075159647:AAGLjAejPey6VpHyOxAqbUR2tS18BnhXdP4' # fill in your API token here
base_url = 'https://api.telegram.org/bot{}/'.format(api_token)

sendMsg_url = base_url + 'sendMessage'

def send_msg(chat_id, msg_text):

	# write your code here
	params = {'chat_id':chat_id,'text':msg_text}
	r = requests.post(sendMsg_url, params=params)
	print(r.status_code)
	print(r.text)
	# threading.Timer(interval_sec,send_msg,(chat_id,msg_text)).start()
	return r.json()["result"]["message_id"]


msg_text = 'I love you <3' # fill in a message here
# msg_id = send_msg(chat_id, msg_text)

now = datetime.now()
print("Start Time (minute):",now.time().minute)
send_msg(chat_id, "Hi, I'll send you love every 10 mins. <3")
start_minute = (now.time().minute//10)*10
while True:   # send every 10 mins
    if start_minute == 50:
        next_trigger = 0
    else:
        next_trigger = start_minute+10
    print("Next Trigger (minute):",next_trigger)
    while now.time().minute != next_trigger:
        now = datetime.now()
    print("Trigger Time (minute):",now.time())
    send_msg(chat_id, msg_text)
    start_minute = (now.time().minute//10)*10







