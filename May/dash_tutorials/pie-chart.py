import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

import pandas_datareader.data as web
import datetime

df = pd.read_csv('../TestData.csv')
#print(df.head())

#print(df["Client Name"].unique())
client_names = df["Client Name"].unique()
# data = df.loc[df["Client Name"] == 'ER250686760']
# #print(data)
# group_by_asset_class = data\
#     .groupby(['Asset Class'], as_index=False)\
#     .agg({'Nominal Amount (USD)':'sum'})

# print(group_by_asset_class)

app = dash.Dash()

app.layout = html.Div(children=[
    html.Div(children='''
    Client's Asset Class Chart
    '''),
    dcc.Dropdown(
        id='client_name_dropdown',
        options=[
            {'label': name, 'value': name} for name in client_names
        ],
        value=client_names[0]
    ),
    dcc.Graph(id='asset_class_barchart')
    ])

@app.callback(
    Output('asset_class_barchart','figure'),
    [Input('client_name_dropdown', 'value')]
)

def asset_class_barchart(client_name):
    client_data = df.loc[df["Client Name"] == client_name]
    group_by_asset_class = client_data\
    .groupby(['Asset Class'], as_index=False)\
    .agg({'Nominal Amount (USD)':'sum'})

    return {
        'data': [
            {'x':group_by_asset_class['Asset Class'],'y':group_by_asset_class['Nominal Amount (USD)'],'type':'bar','name':client_name},
            ],
        'layout': {
            'title': 'Pay Rate for {}'.format(client_name)
        }
    }

if __name__ == '__main__':
    app.run_server(debug=True)