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

df = pd.read_csv('../Client.csv')

all_tickers = df["Ticker"]

### Initialize Dash app ###
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
'''
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Row([
        # Filter row 
            dbc.Col([
                dcc.Dropdown(
                        id='tickerID_filter',
                        options=[
                            {'label': level_num, 'value': level_num} for ticker in tickers
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
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
'''
