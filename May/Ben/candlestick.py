import dash
import dash_core_components as dcc
import dash_table
import pandas as pd
import dash_html_components as html
import numpy as np
from dash.dependencies import Output, Input
import plotly.graph_objects as go
import yfinance as yf
import plotly.express as px
from datetime import datetime



df= yf.Ticker("d05.si")
df = df.history(start="2020-09-07", end="2020-09-08",interval="1m")
print(df)
df = df.transpose()


df = df.reset_index().rename(columns={'index': 'Indicator'})

df = pd.melt(df,id_vars=['Indicator'],var_name="date",value_name="rate")
df = df[df['Indicator']!="volume"]
#print(df[:15])

# ass = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
# print(ass)

#DASH APP
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Interval(
        id = "my_interval",
        n_intervals=0,
        interval=60*1000,
    ),

    dcc.Graph(id="world_finance"),

])

@app.callback(
    Output('world_finance',"figure"),
    [Input("my_interval","n_intervals")]
)

def update_graph(n):
    df= yf.Ticker("d05.si")
    df = df.history(start="2020-09-07", end="2020-09-08",interval="1m")
    df = df[["Open","Close","High","Low"]]
    df = df.transpose()
    df = df.reset_index().rename(columns={'index': 'Indicator'})
    df = pd.melt(df,id_vars=['Indicator'],var_name="date",value_name="rate")
    df = df[df['Indicator']!="volume"]

    line_chart = px.line(df,x= "date",y= "rate",color = "Indicator",title = "WORLD STOCK BIHJ")

    line_chart.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=1, label="1min", step="minute", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    return (line_chart)

if __name__ == '__main__':
    app.run_server(debug=True)