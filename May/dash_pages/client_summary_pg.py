import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt

df = pd.read_csv('../TestDataManipulated.csv')

# datetime formatting
df['Position As of Date']= pd.to_datetime(df['Position As of Date']) 
df['Position As of Date'] = df['Position As of Date'].apply(lambda x: dt.datetime.strftime(x, '%Y-%d-%m'))
df['Position As of Date']= pd.to_datetime(df['Position As of Date']) 

client_names = df["Client Name"].unique()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

##### TO-DO List #####
# Select All/Clear All button for Base Numbers
# Banners for Total Assets/Liab, 1 month return, quarter return, annual return,
# Banners for risk profile
# Time Series chart for Total Assets & Liabilities over time
# 1w, 1m, 1y filter on Time Series chart
# Cash Interest Rates + Loan Rates

##### Excel Formulas #####
# Nominal Amount (USD) = Nominal Units*Current Price (or) 
# Nominal Amount (USD) = Nominal Units*Closing Price
# % Change from Avg Cost = ((Current Price-Average Cost)/Average Cost)*100 (or) 
# % Change from Avg Cost = ((Closing Price-Average Cost)/Average Cost)*100

# Estimated Profit/Loss = Nominal Amount (USD) - (Nominal Units*Average Cost)

card_risk_current = dbc.Card(
    [
        dbc.CardBody([
            html.H4("Risk Level x", className="card-title"),
            html.H6("Current Risk Level", className="card-subtitle"),
        ]),
    ],inverse=True,outline=False, color="info",
)
card_risk_target = dbc.Card(
    [
        dbc.CardBody([
            html.H4("Risk Level x", className="card-title"),
            html.H6("Target Risk Level", className="card-subtitle"),
        ]),
    ],inverse=True,outline=False, color="primary",
)
card_assets = dbc.Card(
    [
        dbc.CardBody(id='card_assets_value',
        # children=[
        #     html.H4("Total Assets", className="card-title"),
        #     html.H6("$xx.xxxM", className="card-subtitle"),
        # ]
        ),
    ],inverse=True,outline=False, color="success",
)
card_liab = dbc.Card(
    [
        dbc.CardBody(id='card_liab_value',
        # children=[
        #     html.H4("Total Liabilities", className="card-title"),
        #     html.H6("$xx.xxxM", className="card-subtitle"),
        # ]
        ),
    ],inverse=True,outline=False, color="danger",
)
card_month_return = dbc.Card(
    [
        dbc.CardBody([
            html.H4("$xx.xxxM", className="card-title"),
            html.H6("Monthly Returns", className="card-subtitle"),
        ]),
    ],
    color="dark",   # https://bootswatch.com/default/ for more card colors
    inverse=True,   # change color of text (black or white)
    outline=False,  # True = remove the block colors from the background and header
)
card_quarter_return = dbc.Card(
    [
        dbc.CardBody([
            html.H4("$xx.xxxM", className="card-title"),
            html.H6("Quarterly Returns", className="card-subtitle"),
        ]),
    ], 
    color="dark",   # https://bootswatch.com/default/ for more card colors
    inverse=True,   # change color of text (black or white)
    outline=False,  # True = remove the block colors from the background and header
)
card_year_return = dbc.Card(
    [
        dbc.CardBody([
            html.H4("$xx.xxxM", className="card-title"),
            html.H6("Annual Returns", className="card-subtitle"),
        ]),
    ], 
    color="dark",   # https://bootswatch.com/default/ for more card colors
    inverse=True,   # change color of text (black or white)
    outline=False,  # True = remove the block colors from the background and header
)

app.layout = html.Div([
    dbc.Row([dbc.Col([
                        html.H3("Client's Name:"),
                        dcc.Dropdown(
                        id='client_name_dropdown',
                        options=[
                            {'label': name, 'value': name} for name in client_names
                        ],
                        value=client_names[0]
                        )
                    ],
                    width={'size':3},
                    ),
            dbc.Col([
                        html.H3("Client's Base Numbers:"),
                        dcc.Checklist(
                        id='base_numbers_checklist',labelStyle={'display': 'inline-block'}
                        )
                    ],
                    width={'size':5},
                    ), 
            dbc.Col(card_risk_current, width=2),
            dbc.Col(card_risk_target, width=2),
            ]),

    html.Br(),
    dbc.Row([dbc.Col(card_assets, width=3),
             dbc.Col(card_liab, width=3),
             dbc.Col(card_month_return, width=2),
             dbc.Col(card_quarter_return, width=2),
             dbc.Col(card_year_return, width=2)], justify="around"),  # justify="start", "center", "end", "between", "around"
    dbc.Row([dbc.Col([dcc.Graph(id='asset_liab_timeseries')],
                    ),
            ]),
    dbc.Row([dbc.Col([dcc.Graph(id='asset_class_barchart')],
                    #style={'height': '500px'}
                    ),
            ]),
    dbc.Row([dbc.Col([dcc.Graph(id='asset_class_piechart')],
                    width={'size':6},
                    ),
            dbc.Col([dcc.Graph(id='asset_class_sunburst')],
                    width={'size':6},
                    ),
            ]),
    dbc.Row([dbc.Col([dcc.Graph(id='cash_loans_table')],
                    width={'size':5},
                    ),
            dbc.Col([dcc.Graph(id='cash_loans_barchart')],
                    width={'size':7},
                    ),
            ])
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
    Output('asset_liab_timeseries','figure'),
    [Input('base_numbers_checklist', 'value')]
) 
def asset_liab_timeseries(selected_base_numbers):
    client_data = df[df["Base Number"].isin(selected_base_numbers)]

    # this is based on assumption that all other assets other than loan are considered as "assets"
    client_data["Asset Class"][client_data["Asset Class"]!="Loans"] = "Others" 
    
    group_by_asset_class = client_data\
    .groupby(['Position As of Date','Asset Class'], as_index=False)\
    .agg({'Nominal Amount (USD)':'sum'})

    # this is based on assumption that all other assets other than loan are considered as "assets"
    group_by_asset_class["Asset Class"][group_by_asset_class["Asset Class"]=="Others"] = "Total Assets"
    group_by_asset_class["Asset Class"][group_by_asset_class["Asset Class"]=="Loans"] = "Total Liabilities"
    
    fig = px.area(group_by_asset_class, x="Position As of Date", y="Nominal Amount (USD)", 
    color = "Asset Class", color_discrete_sequence=['#dea5a4', '#779ecb'],
    labels={"Loans": "Total Liabilities", "Others": "Total Assets"},
    title = "Client's Total Assets & Liabilities over time")
    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=2, label="2d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    return fig

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
            'title': 'Pay Rate for {}'.format(client_name),
            'height': 500
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

@app.callback(
    [Output('card_assets_value','children'),
    Output('card_liab_value','children'),
    Output('cash_loans_table','figure')],
    [Input('base_numbers_checklist', 'value')]
) 
def cash_loans_table(selected_base_numbers):
    asset_classes = ['Investment Cash & Short Term Investments', 'Loans']
    client_data = df[df["Base Number"].isin(selected_base_numbers)]
    client_data = client_data[client_data["Asset Class"].isin(asset_classes)]
    client_data["Asset Class"].replace({"Investment Cash & Short Term Investments": "Cash"}, inplace=True)
    
    group_by_asset_class = client_data\
    .groupby(['CCY','Asset Class'], as_index=False)\
    .agg({'Nominal Amount (USD)':'sum'})

    transformed_group_by_asset_class = \
    group_by_asset_class.pivot(index='CCY', columns='Asset Class', values='Nominal Amount (USD)')\
    .reset_index().fillna(0)

    if 'Loans' not in transformed_group_by_asset_class.columns:
        transformed_group_by_asset_class["Loans"] = 0
    
    transformed_group_by_asset_class.insert(2,'Cash Interest Rate (%)', np.NaN) # to add in real interest rates
    transformed_group_by_asset_class['Loan Rate (%)'] = np.NaN # to add in real loan rates
    
    total_loans = transformed_group_by_asset_class.Loans.sum()
    total_cash = transformed_group_by_asset_class.Cash.sum()
    transformed_group_by_asset_class = transformed_group_by_asset_class.append({'CCY' : '<b>TOTAL</b>' , 'Cash' : f'<b>{total_cash}</b>', 'Loans' : f'<b>{total_loans}</b>'} , ignore_index=True)

    card_assets_value = [
            html.H4("Total Assets", className="card-title"),
            html.H6("${:.3f}M".format(total_cash/1000000), className="card-subtitle"),
        ]

    card_liab_value = [
            html.H4("Total Liabilities", className="card-title"),
            html.H6("${:.3f}M".format(total_loans/1000000), className="card-subtitle"),
        ]

    fig = go.Figure(data=[go.Table(
                header=dict(values=["<b>Currency</b>","<b>Cash (USD)</b>",
                "<b>Cash Interest Rate (%)</b>","<b>Loans (USD)</b>","<b>Loan Rate (%)</b>"],
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[transformed_group_by_asset_class.CCY, \
                transformed_group_by_asset_class.Cash,
                transformed_group_by_asset_class["Cash Interest Rate (%)"],
                transformed_group_by_asset_class.Loans,
                transformed_group_by_asset_class["Loan Rate (%)"]],
                        fill_color='lavender',
                        align='left'))
               ])

    return card_assets_value,card_liab_value,fig

@app.callback(
    Output('cash_loans_barchart','figure'),
    [Input('base_numbers_checklist', 'value')]
) 
def cash_loans_barchart(selected_base_numbers):
    asset_classes = ['Investment Cash & Short Term Investments', 'Loans']
    client_data = df[df["Base Number"].isin(selected_base_numbers)]
    client_data = client_data[client_data["Asset Class"].isin(asset_classes)]
    client_data["Asset Class"].replace({"Investment Cash & Short Term Investments": "Cash"}, inplace=True)
    group_by_asset_class = client_data\
    .groupby(['Asset Class','CCY'], as_index=False)\
    .agg({'Nominal Amount (USD)':'sum'})

    non_zero_df = group_by_asset_class.loc[group_by_asset_class['Nominal Amount (USD)'] != 0]

    fig = px.bar(non_zero_df, x="CCY", y="Nominal Amount (USD)",
            hover_data={"Nominal Amount (USD)":":.3f"},
            text="Nominal Amount (USD)",color='Asset Class', barmode='group')
    fig.update_layout(
    title="Cash vs Liabilities",
    xaxis_title="Currency",
    yaxis_title="Total Nominal Amount (USD)",
    legend_title="",
    )
    fig.update_traces(
        textposition='outside',
        texttemplate = "%{text:.2s}")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)