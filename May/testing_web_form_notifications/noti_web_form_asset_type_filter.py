import dash
import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

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
latest_equities_clients_list = []
latest_fixed_income_clients_list = []
latest_alternatives_clients_list = []
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
    print("No. of values NOT set:",set_values_df["Column Set"].isnull().sum())
    if check_no_of_nulls != 3:
        return True
    return False
#### End of - is_thresholds_set Function ####


#### is_same_as_last_update_lists Function checks if current results are same as last updated results ####
def is_same_as_last_update_lists(eq_clients_list, fi_clients_list, al_clients_list):
    eq_clients_list.sort()
    fi_clients_list.sort()
    al_clients_list.sort()
    global latest_equities_clients_list
    global latest_fixed_income_clients_list
    global latest_alternatives_clients_list
    
    if ((eq_clients_list == latest_equities_clients_list) & (fi_clients_list == latest_fixed_income_clients_list) & (al_clients_list == latest_alternatives_clients_list)):
        return True
    else:
        latest_equities_clients_list = eq_clients_list
        latest_fixed_income_clients_list = fi_clients_list
        latest_alternatives_clients_list = al_clients_list
        return False
    
#### End of - is_same_as_last_update_lists Function ####

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

    # set_values_df.fillna('-', inplace=True)
    # print("After fillna:",set_values_df)
    # print(type(set_values_df["Percentage Amount Set"][0]))
    if pd.isnull(set_values_df["Column Set"][0]):
        no_of_clients_affected_in_equities = "-"
        eq_clients_list = []
    else:
        eq_df = return_filtered_df(latest_client_data,set_values_df["Asset Type"][0],set_values_df["Column Set"][0],set_values_df["Filter Condition"][0],set_values_df["Percentage Amount Set"][0])
        print("Equities Clients List:",eq_df["Client Name"].unique().tolist())
        eq_clients_list = eq_df["Client Name"].unique().tolist()
        no_of_clients_affected_in_equities = len(eq_df["Client Name"].unique())
    if pd.isnull(set_values_df["Column Set"][1]):
        no_of_clients_affected_in_fixedincome = "-"
        fi_clients_list = []
    else:
        fi_df = return_filtered_df(latest_client_data,set_values_df["Asset Type"][1],set_values_df["Column Set"][1],set_values_df["Filter Condition"][1],set_values_df["Percentage Amount Set"][1])
        print("Fixed Income Clients List:",fi_df["Client Name"].unique().tolist())
        fi_clients_list = fi_df["Client Name"].unique().tolist()
        no_of_clients_affected_in_fixedincome = len(fi_df["Client Name"].unique())
    if  pd.isnull(set_values_df["Column Set"][2]):
        no_of_clients_affected_in_alternatives = "-"
        al_clients_list = []
    else:
        al_df = return_filtered_df(latest_client_data,set_values_df["Asset Type"][2],set_values_df["Column Set"][2],set_values_df["Filter Condition"][2],set_values_df["Percentage Amount Set"][2])
        print("Alternatives Clients List:",al_df["Client Name"].unique().tolist())
        al_clients_list = al_df["Client Name"].unique().tolist()
        no_of_clients_affected_in_alternatives = len(al_df["Client Name"].unique())

    return eq_clients_list, fi_clients_list, al_clients_list, no_of_clients_affected_in_equities, no_of_clients_affected_in_fixedincome, no_of_clients_affected_in_alternatives


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
    morning_msg_text = f"==========\nThis is morning testing message from dash web form. (Supposed to be sent at {morning_time_string})\n"+\
        f"== Server Time Now: {datetime.now().time().hour}hr{datetime.now().time().minute}min ==\n==========\n"+\
        "Good Morning! "+u'\U0001F604'+"\n\n"+\
        return_monitoring_info_text_w_values(eq_client_no, fi_client_no, al_client_no) +\
        more_details_text +\
        "Have a wonderful day ahead! "+u'\U0001F60A'
    return morning_msg_text

def return_evening_msg_text(eq_client_no, fi_client_no, al_client_no):
    evening_msg_text = f"==========\nThis is evening testing message from dash web form. (Supposed to be sent at {evening_time_string})\n"+\
        f"== Server Time Now: {datetime.now().time().hour}hr{datetime.now().time().minute}min ==\n==========\n"+\
        "Good Evening! I hope you had a great day! "+u'\U0001F60A'+"\n\n"+\
        return_monitoring_info_text_w_values(eq_client_no, fi_client_no, al_client_no) +\
        more_details_text +\
        "Have a lovely evening! "+u'\U0001F917'
    return evening_msg_text

def return_normal_msg_text(eq_client_no, fi_client_no, al_client_no):
    normal_msg_text = f"==========\nThis is normal testing message from dash web form.\n"+\
        f"== Server Time Now: {datetime.now().time().hour}hr{datetime.now().time().minute}min ==\n==========\n"+\
        "Good Day! "+u'\U0001F60A'+"\n\n"+\
        return_monitoring_info_text_w_values(eq_client_no, fi_client_no, al_client_no) +\
        more_details_text +\
        "Have a great day! "+u'\U0001F917'
    return normal_msg_text

def return_no_threshold_msg_text():
    no_threshold_msg_text = f"==========\nThis is no thresholds set testing message from dash web form.\n"+\
        f"== Server Time Now: {datetime.now().time().hour}hr{datetime.now().time().minute}min ==\n==========\n"+\
        "Good Day! "+u'\U0001F60A'+"\n\n"+\
        "_No threshold values have been set to monitor yet._\n\n" +\
        to_set_threshold_text +\
        "Have a great day! "+u'\U0001F917'
    return no_threshold_msg_text

######### End of - text message format to send #########

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = html.Div([
    dcc.Interval(
        id='my_interval',
        disabled=False,     #if True, the counter will no longer update
        interval=10*1000,    #increment the counter n_intervals every interval milliseconds
        n_intervals=0,      #number of times the interval has passed
        max_intervals=-1,    #number of times the interval will be fired.
                            #if -1, then the interval has no limit (the default)
                            #and if 0 then the interval stops running.
    ),
    dbc.Row([
        dbc.Col(html.H6(children='Set Values to Monitor and Send Notifications', style={'textAlign': 'center','color': 'white','backgroundColor': "#003B70"}),width=8),
        dbc.Col(html.H6(children='Latest Values Set to Monitor', style={'textAlign': 'center','color': 'white','backgroundColor': "#003B70"}),width=4),
        ]),
    dbc.Row([
        dbc.Col(
            dbc.Card([
            # html.Div(html.H4("Set Values to Monitor and Send Notifications"), style={'textAlign': 'center'}),
            html.Br(),
            dbc.FormGroup([
                dbc.Col(dbc.Label("Equities", html_for="equities"), style={'textAlign': 'right'}, width=2),
                dbc.Col(
                    dcc.Dropdown(
                    id="equities_columns_dropdown",
                    options=[
                        {"label": "% Change from Avg Cost", "value": "% Change from Avg Cost"},
                        {"label": "1d %", "value": "1d %"},
                        {"label": "5d %", "value": "5d %"},
                        {"label": "1m %", "value": "1m %"},
                        {"label": "6m %", "value": "6m %"},
                        {"label": "12m %", "value": "12m %"},
                        {"label": "YTD%", "value": "YTD%"}
                    ],
                    placeholder="Choose column"), width=3),
                dbc.Col(
                    dcc.Dropdown(
                    id="equities_conditions_dropdown",
                    options=[
                        {"label": "equal to", "value": "equal to"},
                        {"label": "less than", "value": "less than"},
                        {"label": "less than or equal to", "value": "less than or equal to"},
                        {"label": "greater than", "value": "greater than"},
                        {"label": "greater than or equal to", "value": "greater than or equal to"},
                    ],
                    placeholder="Choose filter condition"), width=3),
                dbc.Col(dbc.Input(type="number", id="equities_percentage_amount", placeholder="Enter percentage amount"),width=3),
            ],row=True),

            dbc.FormGroup([
                dbc.Col(dbc.Label("Fixed Income", html_for="fixedincome"), style={'textAlign': 'right'}, width=2),
                dbc.Col(
                    dcc.Dropdown(
                    id="fixedincome_columns_dropdown",
                    options=[
                        {"label": "% Change from Avg Cost", "value": "% Change from Avg Cost"},
                        {"label": "1d %", "value": "1d %"},
                        {"label": "5d %", "value": "5d %"},
                        {"label": "1m %", "value": "1m %"},
                        {"label": "6m %", "value": "6m %"},
                        {"label": "12m %", "value": "12m %"},
                        {"label": "YTD%", "value": "YTD%"}
                    ],
                    placeholder="Choose filter column"), width=3),
                dbc.Col(
                    dcc.Dropdown(
                    id="fixedincome_conditions_dropdown",
                    options=[
                        {"label": "equal to", "value": "equal to"},
                        {"label": "less than", "value": "less than"},
                        {"label": "less than or equal to", "value": "less than or equal to"},
                        {"label": "greater than", "value": "greater than"},
                        {"label": "greater than or equal to", "value": "greater than or equal to"},
                    ],
                    placeholder="Choose condition"), width=3),
                dbc.Col(dbc.Input(type="number", id="fixedincome_percentage_amount", placeholder="Enter percentage amount"),width=3),
            ],row=True),

            dbc.FormGroup([
                dbc.Col(dbc.Label("Alternatives", html_for="alternatives"), style={'textAlign': 'right'}, width=2),
                dbc.Col(
                    dcc.Dropdown(
                    id="alternatives_columns_dropdown",
                    options=[
                        {"label": "Return on Contribution", "value": "Return on Contribution"}
                    ],
                    placeholder="Choose column"), width=3),
                dbc.Col(
                    dcc.Dropdown(
                    id="alternatives_conditions_dropdown",
                    options=[
                        {"label": "equal to", "value": "equal to"},
                        {"label": "less than", "value": "less than"},
                        {"label": "less than or equal to", "value": "less than or equal to"},
                        {"label": "greater than", "value": "greater than"},
                        {"label": "greater than or equal to", "value": "greater than or equal to"},
                    ],
                    placeholder="Choose filter condition"), width=3),
                dbc.Col(dbc.Input(type="number", id="alternatives_percentage_amount", placeholder="Enter percentage amount"),width=3),
            ],row=True),

            dbc.Row(dbc.Col(dbc.Button("Set Values", id='set_values_button', color="primary", outline=True), style={'textAlign': 'right'},width=11)),

        ], style={"height": "100%"}), width=8),
        dbc.Col(dbc.Card([
            # html.Div(html.H4("Latest Values Set to Monitor and Send Notifications"), style={'textAlign': 'center'}),
            html.Div(id='output_message', style={'textAlign': 'center'}),
            html.Br(),
            html.Div(id="set_values_table"),
        ]), width=4)
    ]),
    
    html.Br(),
    html.H6(children='Send Brief Monitoring Information to WhatsApp or Telegram', style={'textAlign': 'center','color': 'white','backgroundColor': "#003B70"}),
    # html.Hr(),
    # html.Div(html.H4("Send Brief Monitoring Information to WhatsApp or Telegram"), style={'textAlign': 'center'}),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Button("Send to WhatsApp", id='whatsapp_button', color="success", block=True),
            # html.Button('Send to WhatsApp', id='whatsapp_button'),
            html.H6(id='whatsapp_button_clicks')
        ],width=6),
        dbc.Col([
            dbc.Button("Send to Telegram", id='telegram_button', color="info", block=True),
            # html.Button('Send to Telegram', id='telegram_button'),
            html.H6(id='telegram_button_clicks')
        ],width=6),
    ]),
])


@app.callback(
    [Output('set_values_table','children'),
    Output('output_message', 'children')],
    [Input('set_values_button', 'n_clicks')],
    state=[
        State('equities_columns_dropdown', 'value'),
        State('equities_conditions_dropdown', 'value'),
        State('equities_percentage_amount', 'value'),
        State('fixedincome_columns_dropdown', 'value'),
        State('fixedincome_conditions_dropdown', 'value'),
        State('fixedincome_percentage_amount', 'value'),
        State('alternatives_columns_dropdown', 'value'),
        State('alternatives_conditions_dropdown', 'value'),
        State('alternatives_percentage_amount', 'value'),
    ]
)
def generate_set_values(n_clicks, equities_columns_dropdown, equities_conditions_dropdown, equities_percentage_amount,
        fixedincome_columns_dropdown, fixedincome_conditions_dropdown, fixedincome_percentage_amount,
        alternatives_columns_dropdown, alternatives_conditions_dropdown, alternatives_percentage_amount):

    set_values_df = pd.DataFrame(
        {
            "Asset Type": ["Equities", "Fixed Income", "Alternatives"],
            "Column Set": [equities_columns_dropdown, fixedincome_columns_dropdown, alternatives_columns_dropdown],
            "Filter Condition": [equities_conditions_dropdown, fixedincome_conditions_dropdown, alternatives_conditions_dropdown],
            "Percentage Amount Set": [equities_percentage_amount, fixedincome_percentage_amount, alternatives_percentage_amount]
        }
    )
    set_values_df.to_csv(r"set_values_df.csv", index = False)
    set_values_table = dbc.Table.from_dataframe(set_values_df, striped=True, bordered=True, hover=True, size='sm')

    if equities_columns_dropdown is None and fixedincome_columns_dropdown is None and alternatives_columns_dropdown is None:
        output_msg = html.I("No values have been set to monitor so far.")
    else:
        now = datetime.now()
        output_msg = html.I("Last updated: {}".format(now))

    return set_values_table, output_msg

@app.callback(
    Output('whatsapp_button_clicks', 'children'),
    [Input('whatsapp_button', 'n_clicks')])
def whatsapp_clicks(n_clicks):
    if n_clicks is not None:
        if is_thresholds_set():
            eq_clients_list, fi_clients_list, al_clients_list, eq_client_no, fi_client_no, al_client_no = return_values_for_msg()
            # print(eq_client_no, fi_client_no, al_client_no)
            normal_msg_text = return_normal_msg_text(eq_client_no, fi_client_no, al_client_no)
            send_whatsapp_message(normal_msg_text)
            # send_telegram_message(normal_msg_text)
        else:
            no_threshold_msg_text = return_no_threshold_msg_text()
            send_whatsapp_message(no_threshold_msg_text)
            # send_telegram_message(no_threshold_msg_text)
    return 'Send to WhatsApp Button has been clicked {} times'.format(n_clicks)

@app.callback(
    Output('telegram_button_clicks', 'children'),
    # [Input('telegram_button', 'n_clicks')])
    [Input('my_interval', 'n_intervals')])
# def telegram_clicks(n_clicks):
def telegram_clicks(n_intervals):
    if n_intervals is None:
        raise PreventUpdate
    else:
    # if n_clicks is not None:
        if is_thresholds_set():
            eq_clients_list, fi_clients_list, al_clients_list, eq_client_no, fi_client_no, al_client_no = return_values_for_msg()
            # print(eq_client_no, fi_client_no, al_client_no)
            if not is_same_as_last_update_lists(eq_clients_list, fi_clients_list, al_clients_list):
                normal_msg_text = return_normal_msg_text(eq_client_no, fi_client_no, al_client_no)
                # send_whatsapp_message(normal_msg_text)
                send_telegram_message(normal_msg_text)
        else:
            global first_time_threshold_set_check
            if first_time_threshold_set_check:
                no_threshold_msg_text = return_no_threshold_msg_text()
                # send_whatsapp_message(no_threshold_msg_text)
                send_telegram_message(no_threshold_msg_text)
                first_time_threshold_set_check = False

    return 'Send to Telegram Button has been clicked {} times'.format(n_intervals)


if __name__ == '__main__':
    app.run_server(debug=True)