import dash
import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt

from datetime import date,time, datetime, timedelta   

import requests 
import json

# chat_id = 387218772 # fill in your chat id here
chat_id = -376934065 # fill in your chat id here
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

msg_text = 'Test Importing Dash chart and sending thru tele.' # fill in a message here


# import os

# if not os.path.exists("images"):
#     os.mkdir("images")

df = pd.read_csv('../Client.csv')
risk_df = pd.read_csv('../RiskLevelsAllocation.csv')

################# Data Processing for Risky Client Information #########################
df['Position As of Date']= pd.to_datetime(df['Position As of Date']) 
# df['Position As of Date'] = df['Position As of Date'].apply(lambda x: dt.datetime.strftime(x, '%Y-%d-%m'))
# df['Position As of Date']= pd.to_datetime(df['Position As of Date']) 

latest_date = df["Position As of Date"].max()
latest_client_data = df[df['Position As of Date'] == latest_date]

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
#print(risk_analysis_df)

risk_levels = ["All Levels",1,2,3,4,5]

############ for telegram ################
pie_figure = px.pie(risk_analysis_df, values='Count', names='Current Risk Level',
                    title='Overall Current Risk Profiles Breakdown'
                ).update_traces(textposition='inside', textinfo='percent+label').update_layout(legend_title="Current Risk Level")

pie_figure.write_image("pie_figure.png")

photo_path = open('pie_figure.png', 'rb')


################# End of Data Processing for Risky Client Information #########################

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
msg_id = send_msg(chat_id, msg_text)
r = requests.post(base_url + 'sendPhoto', data={'chat_id': chat_id}, files={'photo': photo_path})
print(r.status_code)
app.layout = html.Div([
    dbc.Row([
            # This is Overall Current Risk Profiles Breakdown Piechart
            dbc.Col([dcc.Graph(id='current_risk_piechart',
                figure = px.pie(risk_analysis_df, values='Count', names='Current Risk Level',
                    title='Overall Current Risk Profiles Breakdown'
                ).update_traces(textposition='inside', textinfo='percent+label').update_layout(legend_title="Current Risk Level")
            )], width={'size':3},),

            # This is Target Status Breakdown Piechart
            dbc.Col([dcc.Graph(id='target_status_piechart',
                figure = px.pie(risk_analysis_df, values='Count', names='Target Status',
                    title='Target Status Breakdown'
                ).update_traces(textposition='inside', textinfo='percent+label')
            )], width={'size':3},),

            # This is Filter + Table
            dbc.Col([
                # This is Target Risk Level Filter for the Table below
                dcc.Dropdown(
                        id='target_risk_filter',
                        options=[
                            {'label': level_num, 'value': level_num} for level_num in risk_levels
                        ],
                        placeholder="Filter by Target Risk Level",
                        # value=risk_levels[0],
                        clearable=True),\
                # This is Risk Target Status Table (connected to callback for "data" in DataTable) 
                dash_table.DataTable(
                    id='risk_target_status_table',
                    columns = [{"name": i, "id": i} for i in risk_analysis_df[["Client Name","Current Risk Level","Target Risk Level"]].columns],
                    style_table={'border': 'thin lightgrey solid'},
                    style_header={'backgroundColor':'lightgrey','fontWeight':'bold'},
                    style_cell={'textAlign':'center'}
                )], 
                width={'size':6})
            ]),
])

# This callback is connected to Risk Target Status Table to return "data" in DataTable)
@app.callback(
    Output('risk_target_status_table','data'),
    [Input('target_risk_filter', 'value')]
) 
def risk_target_status_table(target_risk_level):
    #print(target_risk_level)
    risk_table_df = risk_analysis_df[["Client Name","Current Risk Level","Target Risk Level"]]
    if target_risk_level != "All Levels" and target_risk_level != None:
        risk_table_df = risk_table_df.loc[risk_table_df["Target Risk Level"] == target_risk_level]
    #print(risk_table_df)
    table_data = risk_table_df.to_dict('records')
    return table_data

if __name__ == '__main__':
    app.run_server(debug=True)