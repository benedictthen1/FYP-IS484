import dash
import dash_core_components as dcc
import dash_table
import pandas as pd
import dash_html_components as html
import numpy as np
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
import yfinance as yf
import plotly.express as px
from datetime import datetime, timedelta
from pytz import timezone
import dash_bootstrap_components as dbc

fig = go.Figure()

df= yf.Ticker('aapl')
d1 = df.history(interval= "60m",period="1mo")
d1["Datetime"] = d1.index.strftime("%d/%m/%Y, %H:%M:%S")
print(d1)

print("CHAGOAGMAOGMSAOGMSAOGMSMGOASMGOSAMGOSA")
test =  d1["Datetime"].index.strftime("%h %d").unique()[::5]
print(test)

#DASH APP
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Input(id="input", type="text", placeholder="search ticker"),
    html.Button(id="submit-btn",n_clicks=0,children="apply"),
    dcc.Dropdown(
        id="timeline_dropdown",
        options=[
            {'label': '1D', 'value': '1d'},
            {'label': '5D', 'value': '5d'},
            {'label': '1M', 'value': '1m'},
        ],
        value='1d'
    ),
    dcc.Graph(figure=fig, id="candle"),
])

############################# CALL BACKS #######################
@app.callback(Output("candle","figure"),
              [Input("submit-btn","n_clicks"),Input("timeline_dropdown","value")],[State("input","value")])
def stock(n_clicks,time_value,input_value):
    if not input_value:
        df= yf.Ticker('aapl')
    else:
        df= yf.Ticker(str(input_value))

    #today = pd.datetime.today().date()
    #back_day = datetime.today().date() - timedelta(days=5)

    if time_value == "1d":
        df = df.history(interval="1m",period="1d")
    elif time_value == "5d":
        df = df.history(interval="5m",period="5d")
    elif time_value == "1m":
        df = df.history(interval= "60m",period="1mo")

    df["Datetime"] = df.index.strftime("%d/%m/%Y, %H:%M:%S")
    #x=df.index.strftime("%Y/%m/%d")
    #df = df.tail(389)

    trace1 = {
    'x': df.Datetime,
    'open': df.Open,
    'close': df.Close,
    'high': df.High,
    'low': df.Low,
    'type': 'candlestick',
    'name': input_value,
    'showlegend': False
    }

    avg_30 = df.Close.rolling(window=30, min_periods=1).mean()
    avg_50 = df.Close.rolling(window=50, min_periods=1).mean()
    df["Average"] = df.Close.mean().round(2)

    trace2 = {'x': df.Datetime,'y': avg_30,
        'type': 'scatter',
        'mode': 'lines',
        'line': {'width': 1.5,'color': 'blue'},
        'name': 'MA30'
    }

    trace3 = {
        'x': df.Datetime,'y': avg_50,
        'type': 'scatter',
        'mode': 'lines',
        'line': {'width': 1.5,'color': 'orange'},
        'name': 'MA50'
    }

    trace4 = {
        'x': df.Datetime,'y': df.Average,
        'type': 'scatter',
        'mode': 'lines',
        'line': {'dash': 'dash','width': 1.5,'color': 'Grey'},
        'name': 'Mean'
    }

    data = [trace1,trace2,trace3,trace4]
    # Config graph layout
    layout = go.Layout({
        'title': {
            'text': str(input_value) + ' Stock',
            'font': {
                'size': 15
            }
        },
        'plot_bgcolor': '#2E2E2E'
    })
    
    #dates =  df["Datetime"].index.strftime("%d/%m/%Y").unique()
    if time_value == "1d":
        dates =  ["10 AM","11 AM","12 PM","1 PM","2 PM","3 PM"]
        spaces = [30,88,148,205,270,330]
    elif time_value == "5d":
        dates =  df["Datetime"].index.strftime("%d/%m/%Y").unique()
        spaces = [40, 115, 190, 270, 350]
    elif time_value == "1m":
        dates =  df["Datetime"].index.strftime("%h %d").unique()[::5]
        spaces = [1, 40, 70, 100, 135]
    #print(dates, date_len)

    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(
        xaxis_rangeslider_visible=False,autosize=False, width=1000,height=500, yaxis_showgrid=False, 
        xaxis = dict(
            #title = 'date',
            showticklabels = True,
            showgrid=False,
            tickmode = 'array',
            tickvals = spaces,
            ticktext = dates
            ),
     )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)