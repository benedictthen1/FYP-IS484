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

chat_id = 387218772 # fill in your chat id here
# chat_id = -376934065 # fill in your chat id here
api_token = '1075159647:AAGLjAejPey6VpHyOxAqbUR2tS18BnhXdP4' # fill in your API token here
base_url = 'https://api.telegram.org/bot{}/'.format(api_token)

sendMsg_url = base_url + 'sendMessage'
sendPhoto_url = base_url + 'sendPhoto'

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

def send_photo(chat_id, photo_url):

	# write your code here
	params = {'chat_id':chat_id,'photo':photo_url}
	r = requests.post(sendPhoto_url, params=params)
	print(r.status_code)
	if r.status_code == 200:
		return r.status_code

	return None 

# photo_url = 'https://spectator.imgix.net/content/uploads/2016/05/iStock_000076568217_Large.jpg?auto=compress,enhance,format&crop=faces,entropy,edges&fit=crop&w=620&h=413' # fill in a URL that points to an image
# photo_path = open('C:/Users/User/OneDrive - Singapore Management University/SMU/Year 4 Sem 1/FYP/FYP-IS484/May/dash_pages/images/pie_figure.png', 'rb')
photo_path = open('../dash_pages/images/pie_figure.png', 'rb')
# send_photo(chat_id, photo_path)
r = requests.post(base_url + 'sendPhoto', data={'chat_id': chat_id}, files={'photo': photo_path})
print(r.status_code)

# now = datetime.now()
# print("Start Time (minute):",now.time().minute)
# send_msg(chat_id, "Hi, I'll send you love every 10 mins. <3")
# start_minute = (now.time().minute//10)*10
# while True:   # send every 10 mins
#     if start_minute == 50:
#         next_trigger = 0
#     else:
#         next_trigger = start_minute+10
#     print("Next Trigger (minute):",next_trigger)
#     while now.time().minute != next_trigger:
#         now = datetime.now()
#     print("Trigger Time (minute):",now.time())
#     send_msg(chat_id, msg_text)
#     start_minute = (now.time().minute//10)*10







