import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.express as px

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
    Client's Name:
    '''),
    dcc.Dropdown(
        id='client_name_dropdown',
        options=[
            {'label': name, 'value': name} for name in client_names
        ],
        value=client_names[0]
    ),
    html.Div(children='''
    Client's Base Numbers:
    '''),
    dcc.Checklist(
        id='base_numbers_checklist',labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id='asset_class_barchart'),
    dcc.Graph(id='asset_class_piechart'),
    dcc.Graph(id='asset_class_sunburst'),
    ])

@app.callback(
    Output('base_numbers_checklist','options'),
    [Input('client_name_dropdown', 'value')]
) 
def set_base_number_options(client_name):
    client_data = df.loc[df["Client Name"] == client_name]
    base_numbers = list(client_data["Base Number"].unique())
    return [{'label': base_number, 'value': base_number} for base_number in base_numbers]

@app.callback(
    Output('base_numbers_checklist','value'),
    [Input('client_name_dropdown', 'value')]
) 
def select_all_base_number_values(client_name):
    client_data = df.loc[df["Client Name"] == client_name]
    return list(client_data["Base Number"].unique())

@app.callback(
    Output('asset_class_barchart','figure'),
    [Input('client_name_dropdown', 'value'),Input('base_numbers_checklist', 'value')]
) 
def asset_class_barchart(client_name,selected_base_numbers):
    client_data = df[df["Base Number"].isin(selected_base_numbers)]
    group_by_asset_class = client_data\
    .groupby(['Asset Class'], as_index=False)\
    .agg({'Nominal Amount (USD)':'sum'})
    group_by_asset_class["Color"] = np.where(group_by_asset_class["Nominal Amount (USD)"]<0, 'red', 'green')
    return {
        'data': [
            {'x':group_by_asset_class['Asset Class'],
            'y':group_by_asset_class['Nominal Amount (USD)'],
            'type':'bar',
            'name':client_name,
            'marker': {
               'color': group_by_asset_class["Color"]
            }
           },
            ],
        'layout': {
            'title': 'Pay Rate for {}'.format(client_name)
        }
    }
    
@app.callback(
    Output('asset_class_piechart','figure'),
    [Input('base_numbers_checklist', 'value')]
) 
def asset_class_piechart(selected_base_numbers):
    client_data = df[df["Base Number"].isin(selected_base_numbers)]
    group_by_asset_class = client_data\
    .groupby(['Asset Class'], as_index=False)\
    .agg({'Nominal Amount (USD)':'sum'})

    return px.pie(group_by_asset_class, values='Nominal Amount (USD)', names='Asset Class',
             title="Client's Asset Class Breakdown",
             hover_data=['Nominal Amount (USD)'])
    #fig.update_traces(textinfo='percent+label')
    
    #return fig

@app.callback(
    Output('asset_class_sunburst','figure'),
    [Input('base_numbers_checklist', 'value')]
) 
def asset_class_sunburst(selected_base_numbers):
    client_data = df[df["Base Number"].isin(selected_base_numbers)]
    group_by_asset_class = client_data\
    .groupby(['Asset Class','Asset Sub Class'], as_index=False)\
    .agg({'Nominal Amount (USD)':'sum'})

    fig = px.sunburst(group_by_asset_class, path=['Asset Class', 'Asset Sub Class'], 
    values='Nominal Amount (USD)',
    title="Client's Asset Class-Sub Asset Class Breakdown")
    fig.update_traces(textinfo='percent parent+label')
    #fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)