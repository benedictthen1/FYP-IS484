import dash
import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
from datetime import date, timedelta

##### Formulas #####
# Exchange Rate (CCY to USD) = Nominal Amount (USD)/Nominal Amount (CCY)
# Nominal Amount (USD) = Nominal Units*Current Price*Exchange Rate (or) 
# Nominal Amount (USD) = Nominal Units*Closing Price*Exchange Rate
# % Change from Avg Cost = ((Current Price-Average Cost)/Average Cost)*100 (or) 
# % Change from Avg Cost = ((Closing Price-Average Cost)/Average Cost)*100

# Estimated Original Amount Paid = Nominal Units*Average Cost*Exchange Rate
# Estimated Profit/Loss = Nominal Amount (USD) - (Nominal Units*Average Cost*Exchange Rate)
# % Profit/Loss Return = ((Estimated Profit/Loss) / Estimated Original Amount Paid)*100

# % Outstanding Amount = Outstanding Amount*100/Commitment Amount 
# % Return on Contribution = ((Distribution Amount/Contribution Amount)-1)*100
###########################

df = pd.read_csv('../Client.csv')
risk_df = pd.read_csv('../RiskLevelsAllocation.csv')

### Change Date Format ###

df['Position As of Date'] = pd.to_datetime(df['Position As of Date'], errors='coerce').dt.strftime('%d/%m/%Y')
df['Position As of Date']= pd.to_datetime(df['Position As of Date'])
df['Maturity'] = pd.to_datetime(df['Maturity'], errors='coerce').dt.strftime('%d/%m/%Y')
df['Maturity']= pd.to_datetime(df['Maturity'])
df['Next Call Date'] = pd.to_datetime(df['Next Call Date'], errors='coerce').dt.strftime('%d/%m/%Y')
df['Next Call Date']= pd.to_datetime(df['Next Call Date'])
df['Dividend EX Date'] = pd.to_datetime(df['Dividend EX Date'], errors='coerce').dt.strftime('%m/%d/%Y')
df['Dividend EX Date']= pd.to_datetime(df['Dividend EX Date'])

# df['Position As of Date']= pd.to_datetime(df['Position As of Date']) 
# df['Position As of Date'] = df['Position As of Date'].apply(lambda x: dt.datetime.strftime(x, '%Y-%d-%m'))
# df['Position As of Date']= pd.to_datetime(df['Position As of Date']) 

### Limit decimal places of all numeric columns in df ###
numeric_cols = df.select_dtypes([np.number]).columns.to_list()
decimals = 3
df[numeric_cols] = df[numeric_cols].apply(lambda x: round(x, decimals))

### Get all client names ###
client_names = df["Client Name"].unique()

### Initialize Dash app ###
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# this function returns sign_string for the values on banners 
def return_sign_and_color_string(number):
    sign = ""
    color = "#003B70"
    if number > 0:
        sign = "+"
        color = "#61BBA0"
    elif number < 0:
        sign = "-"
        color = "#E17F79"
    return sign, color

def return_reminders_summary_table(table_columns, table_data, detailed_table_columns,detailed_table_data): 
    reminders_summary_table_content = [
        dash_table.DataTable(
            id='reminders_summary_table',
            columns = table_columns,
            data = table_data,
            style_table={'border': 'thin lightgrey solid'},
            style_header={'backgroundColor':'lightgrey','fontWeight':'bold'},
            style_cell={'textAlign':'left','width':'12%'}
            ),
        html.Br(),
        dbc.Button("Show more details", id="reminder_button", outline=True, color="secondary", size="sm", className="mr-1"),
        dbc.Modal(
            [
                dbc.ModalHeader("Reminders: Detailed Table of All Assets Due (today onwards)"),
                dbc.ModalBody(dbc.Row([
                        dash_table.DataTable(
                            id='reminders_detailed_table',
                            columns = detailed_table_columns,
                            data = detailed_table_data,
                            style_table={'border': 'thin lightgrey solid'},
                            style_header={'backgroundColor':'lightgrey','fontWeight':'bold'},
                            style_cell={'textAlign':'left','width':'12%'}
                            )
                        ])
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-reminder", className="ml-auto")
                ),
            ],
            id="reminder-modal",
            size="xl",
            scrollable=True,
        ),
        ]
    
    return reminders_summary_table_content

def return_reminders_tab_content(table_columns, table_data): 
    reminders_tab_content = dbc.Row(
        dbc.Col([dash_table.DataTable(
                id='reminders_summary_table',
                columns = table_columns,
                data = table_data,
                style_table={'border': 'thin lightgrey solid'},
                style_header={'backgroundColor':'lightgrey','fontWeight':'bold'},
                style_cell={'textAlign':'left','width':'12%'}
            )],   
        )
    )
        
    return reminders_tab_content

cash_liab_tab_content = html.Br(),\
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody(id='card_cash_liab_left1_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_cash_liab_left2_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_cash_liab_right1_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_cash_liab_right2_value')],color="dark",  inverse=True, outline=False),width=3),
        ], justify="start"
    ),\
    html.Br(),\
    dbc.Row([
        dbc.Col([dcc.Graph(id='cash_liab_chart')],
            width={'size':6},
            ),
        dbc.Col([
            dash_table.DataTable(
                id='cash_liab_table',
                style_table={'border': 'thin lightgrey solid'},
                style_header={'backgroundColor':'lightgrey','fontWeight':'bold'},
                style_cell={'textAlign':'left','width':'12%'}
                ),
            html.Br(),
            dbc.Button("Show more details", id="cash_liab_button", outline=True, color="secondary", size="sm", className="mr-1"),
            ],width={'size':6},
            ),
    ])

equities_tab_content = html.Br(),\
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody(id='card_equities_left1_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_equities_left2_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_equities_right1_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_equities_right2_value')],color="dark",  inverse=True, outline=False),width=3),
        ], justify="start"
    ),\
    html.Br(),\
    dbc.Row([
        dbc.Col([dcc.Graph(id='equities_chart')],
            width={'size':6},
            ),
        dbc.Col([
            dash_table.DataTable(
                id='equities_table',
                style_table={'border': 'thin lightgrey solid'},
                style_header={'backgroundColor':'lightgrey','fontWeight':'bold'},
                style_cell={'textAlign':'left','width':'12%'}
                ),
            html.Br(),
            dbc.Button("Show more details", id="equities_button", outline=True, color="secondary", size="sm", className="mr-1"),
            ],width={'size':6},
            ),
    ])

fixed_income_tab_content = html.Br(),\
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody(id='card_fixed_income_left1_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_fixed_income_left2_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_fixed_income_right1_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_fixed_income_right2_value')],color="dark",  inverse=True, outline=False),width=3),
        ], justify="start"
    ),\
    html.Br(),\
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
            id='credit_rating_scales_dropdown',
            options=[
                {'label': "S&P", 'value': "S&P"},
                {'label': "Moody's", 'value': "Moody's"},
                {'label': "Fitch", 'value': "Fitch"},
            ],
            # value=client_names["S&P"],
            placeholder="Select Credit Rating Scale (Default: S&P)",
            clearable=True
            ),
            dcc.Graph(id='fixed_income_chart')],
            width={'size':6},
            ),
        dbc.Col([
            dash_table.DataTable(
                id='fixed_income_table',
                style_table={'border': 'thin lightgrey solid'},
                style_header={'backgroundColor':'lightgrey','fontWeight':'bold'},
                style_cell={'textAlign':'left','width':'12%'}
                ),
            html.Br(),
            dbc.Button("Show more details", id="fixed_income_button", outline=True, color="secondary", size="sm", className="mr-1"),
            ],width={'size':6},
            ),
    ])

alternatives_tab_content = html.Br(),\
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody(id='card_alternatives_left1_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_alternatives_left2_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_alternatives_right1_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_alternatives_right2_value')],color="dark",  inverse=True, outline=False),width=3),
        ], justify="start"
    ),\
    html.Br(),\
    dbc.Row([
        dbc.Col([dcc.Graph(id='alternatives_chart')],
            width={'size':6},
            ),
        dbc.Col([
            dash_table.DataTable(
                id='alternatives_table',
                style_table={'border': 'thin lightgrey solid'},
                style_header={'backgroundColor':'lightgrey','fontWeight':'bold'},
                style_cell={'textAlign':'left','width':'12%'}
                ),
            html.Br(),
            dbc.Button("Show more details", id="alternatives_button", outline=True, color="secondary", size="sm", className="mr-1"),
            ],width={'size':6},
            ),
    ])

capital_markets_tab_content = html.Br(),\
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody(id='card_capital_markets_left1_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_capital_markets_left2_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_capital_markets_right1_value')],color="dark",  inverse=True, outline=False),width=3),
        dbc.Col(dbc.Card([dbc.CardBody(id='card_capital_markets_right2_value')],color="dark",  inverse=True, outline=False),width=3),
        ], justify="start"
    ),\
    html.Br(),\
    dbc.Row([
        dbc.Col([dcc.Graph(id='capital_markets_chart')],
            width={'size':6},
            ),
        dbc.Col([
            dash_table.DataTable(
                id='capital_markets_table',
                style_table={'border': 'thin lightgrey solid'},
                style_header={'backgroundColor':'lightgrey','fontWeight':'bold'},
                style_cell={'textAlign':'left','width':'12%'}
                ),
            html.Br(),
            dbc.Button("Show more details", id="capital_markets_button", outline=True, color="secondary", size="sm", className="mr-1"),
            ],width={'size':6},
            ),
    ])

reminders_tab_content = html.Br(),\
    dbc.Row([
        dash_table.DataTable(
            id='reminders_tab_table',
            style_table={'border': 'thin lightgrey solid'},
            style_header={'backgroundColor':'lightgrey','fontWeight':'bold'},
            style_cell={'textAlign':'left','width':'12%'}
            ),
    ])

# The whole app layout

app.layout = html.Div([
    dbc.Row([
        dbc.Col([ 
            html.H3("Client's Name: ",style={'color': 'white','text-align': 'left'}),
            dcc.Dropdown(
            id='client_name_dropdown',
            options=[
                {'label': name, 'value': name} for name in client_names
            ],
            value=client_names[0],
            clearable=False,
            style={'text-align': 'left'}
            ),
        ],width=3),
        dbc.Col([
            html.H3("Client's Base Numbers: ",style={'color': 'white','float': 'left'}),
            html.Div([
                dbc.Button('Clear All', id='base_num_clear_btn',outline=True,color="light",size="sm", n_clicks=0),
                dbc.Button('Select All', id='base_num_all_btn',outline=True,color="light",size="sm", n_clicks=0), 
                ],style={'text-align': 'right'}),
            dcc.Dropdown(id='base_numbers_checklist',placeholder="Select a Base Number",multi=True,style={'text-align': 'left'}),
            ],width=9),
        ],style={'backgroundColor': "#003B70"}),

    html.Br(),

    dbc.Row([
            dbc.Col(dbc.Card([dbc.CardBody(id='card_assets_value')],color="white", outline=False),width=2),
            dbc.Col(dbc.Card([dbc.CardBody(id='card_liab_value')],color="white", outline=False),width=2),
            dbc.Col(dbc.Card([dbc.CardBody(id='card_profit_loss_value')],color="white", outline=False),width=2),
            dbc.Col(dbc.Card([dbc.CardBody(id='card_current_risk_value')],color="white", outline=False),width=2),
            dbc.Col(dbc.Card([dbc.CardBody(id='card_target_risk_value')],color="white", outline=False),width=2),
            dbc.Col(dbc.Card([dbc.CardBody(id='card_reminders_value')],color="white", outline=False),width=2),
            ], justify="start"), # justify="start", "center", "end", "between", "around"
    
    html.Br(),

    # New Layout
    dbc.Row([
            dbc.Col(html.H5(children='Assets & Liabilities over time', style={'textAlign': 'center','color': 'white','backgroundColor': "#003B70"}),width=6),
            dbc.Col(html.H5(id='reminders_summary_title', style={'textAlign': 'center','color': 'white','backgroundColor': "#003B70"}),width=6),
            ]),
    dbc.Row([
            dbc.Col([
                dcc.Graph(id='asset_liab_timeseries')], width={'size':6}),
                html.Div(id = "reminders_summary_content", style={'backgroundColor': "white",'width':'50%'}),
            ]),
    html.Br(),
    dbc.Row([
            dbc.Col(html.H5(children='Current Assets & Liabilities Breakdown', style={'textAlign': 'center','color': 'white','backgroundColor': "#003B70"}),width=3),
            dbc.Col(html.H5(children='Current Profit/Loss Breakdown', style={'textAlign': 'center','color': 'white','backgroundColor': "#003B70"}),width=3),
            dbc.Col(html.H5(children='Risk Analysis', style={'textAlign': 'center','color': 'white','backgroundColor': "#003B70"}),width=6),
            ]),
    dbc.Row([
            dbc.Col([
                dcc.Graph(id='asset_class_piechart', style={"height": "100%"})], width={'size':3}),
            dbc.Col([
                dcc.Graph(id='profit_loss_breakdown_barchart', style={"height": "100%"})], width={'size':3}),
            dbc.Col([
                dbc.Row([
                        dbc.Col([dcc.Graph(id='current_risk_piechart')], width={'size':6}),
                        dbc.Col([dcc.Graph(id='target_risk_piechart')], width={'size':6}),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(html.H5(children='Risk Analysis: Current vs Target', style={'textAlign': 'center','color': 'white','backgroundColor': "#3A6790"}),width=8),
                    dbc.Col(html.H5(children='Risk Analysis: Amount to Target', style={'textAlign': 'center','color': 'white','backgroundColor': "#3A6790"}),width=4),
                    ]),
                dbc.Row([
                    dbc.Col([dcc.Graph(id='current_target_risk_barchart')], width={'size':8}),
                    dbc.Col([
                    dbc.Card([dbc.CardBody(id='cash_amount_to_target_card')],color="white", outline=False),
                    dbc.Card([dbc.CardBody(id='equities_amount_to_target_card')],color="white", outline=False),
                    dbc.Card([dbc.CardBody(id='fi_amount_to_target_card')],color="white", outline=False),
                    ], width={'size':4})
                
                ])
            ]),

        ]),
    html.Br(),
    dbc.Row([
            dbc.Col([
                dbc.Tabs([
                    dbc.Tab(label="CASH & LIABILITIES", tab_id="CASH & LIABILITIES",children=cash_liab_tab_content, style={'backgroundColor': "white"}),
                    dbc.Tab(label="EQUITIES", tab_id="EQUITIES",children=equities_tab_content, style={'backgroundColor': "white"}),
                    dbc.Tab(label="FIXED INCOME", tab_id="FIXED INCOME",children=fixed_income_tab_content, style={'backgroundColor': "white"}),
                    dbc.Tab(label="ALTERNATIVES", tab_id="ALTERNATIVES",children=alternatives_tab_content, style={'backgroundColor': "white"}),
                    dbc.Tab(label="CAPITAL MARKETS", tab_id="CAPITAL MARKETS",children=capital_markets_tab_content, style={'backgroundColor': "white"}),
                    dbc.Tab(label="REMINDERS", tab_id="REMINDERS",children= reminders_tab_content, style={'backgroundColor': "white"}),
                ])
            ])
        ]),  
],style={'backgroundColor': "#CED8E2"})

@app.callback(
    [Output('base_numbers_checklist','options'),
    Output('base_numbers_checklist','value')],
    [Input('client_name_dropdown', 'value'),
    Input("base_num_clear_btn", "n_clicks"),
    Input("base_num_all_btn","n_clicks")]
) 
def set_base_number_multi_selection(client_name,clear_all,select_all):
    client_data = df.loc[df["Client Name"] == client_name]
    base_numbers = list(client_data["Base Number"].unique())
    multi_select_options = [{'label': base_number, 'value': base_number} for base_number in base_numbers]
    
    checklist_value = base_numbers
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "base_num_clear_btn" in changed_id:
        checklist_value = []
    else:
        checklist_value = base_numbers
    return multi_select_options, checklist_value

@app.callback(
    [Output('card_assets_value','children'),
    Output('card_liab_value','children'),
    Output('asset_liab_timeseries','figure'),
    Output('asset_class_piechart','figure')],
    [Input('client_name_dropdown', 'value'),
    Input('base_numbers_checklist', 'value')]
) 
def overall_section(selected_client_name,selected_base_numbers):
    client_data = df.loc[df["Client Name"] == selected_client_name]
    
    if selected_base_numbers != []:
        client_data = df[df["Base Number"].isin(selected_base_numbers)]
    # client_data = df[df["Base Number"].isin(selected_base_numbers)]
    group_by_asset_class = client_data\
    .groupby(['Position As of Date','Asset Class'], as_index=False)\
    .agg({'Nominal Amount (USD)':'sum'})

    latest_date = group_by_asset_class["Position As of Date"].max()
    latest_piechart_data = group_by_asset_class[group_by_asset_class['Position As of Date'] == latest_date]

    # this is based on assumption that all other assets other than loan are considered as "assets"
    client_data["Asset Class"][client_data["Asset Class"]!="Loans"] = "Others" 
    
    group_by_date_asset_class = client_data\
    .groupby(['Position As of Date','Asset Class'], as_index=False)\
    .agg({'Nominal Amount (USD)':'sum'})

    # this is based on assumption that all other assets other than loan are considered as "assets"
    group_by_date_asset_class["Asset Class"][group_by_date_asset_class["Asset Class"]=="Others"] = "Total Assets"
    group_by_date_asset_class["Asset Class"][group_by_date_asset_class["Asset Class"]=="Loans"] = "Total Liabilities"

    latest_data = group_by_date_asset_class[group_by_date_asset_class['Position As of Date'] == latest_date]
    
    try:
        latest_total_cash = latest_data[latest_data["Asset Class"]=="Total Assets"]["Nominal Amount (USD)"].item()
    except:
        latest_total_cash = 0

    try:
        latest_total_loans = latest_data[latest_data["Asset Class"]=="Total Liabilities"]["Nominal Amount (USD)"].item()
    except:
        latest_total_loans = 0

    total_cash_sign, total_cash_color = return_sign_and_color_string(latest_total_cash)
    card_assets_value = [
            html.H5("Total Assets", style={"color":"#003B70"}),
            html.H2(children=total_cash_sign+"${:.3f}M".format(abs(latest_total_cash/1000000)), style={"color":total_cash_color}),
        ]
    total_loans_sign, total_loans_color = return_sign_and_color_string(abs(latest_total_loans)*(-1))
    card_liab_value = [
            html.H5("Total Liabilities", style={"color":"#003B70"}),
            html.H2(children="${:.3f}M".format(abs(latest_total_loans/1000000)), style={"color":total_loans_color}),
        ]
    
    time_series_fig = px.area(group_by_date_asset_class, x="Position As of Date", y="Nominal Amount (USD)", 
                                color = "Asset Class", color_discrete_sequence=['#dea5a4', '#779ecb'],)
                                # title = "Client's Total Assets & Liabilities over time")
    time_series_fig.update_traces(mode="markers+lines", hovertemplate=None)
    time_series_fig.update_layout(hovermode="x unified")
    time_series_fig.update_xaxes(
                                rangeslider_visible=True,
                                rangeselector=dict(
                                    buttons=list([
                                        dict(count=1, label="2d", step="day", stepmode="backward"),
                                        dict(count=6, label="1w", step="day", stepmode="backward"),
                                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                                        dict(count=1, label="1y", step="year", stepmode="backward"),
                                        dict(step="all")
                                        ])
                                    )
                                )

    pie_chart_fig = px.pie(latest_piechart_data, values='Nominal Amount (USD)', names='Asset Class',
                            # title="Client's Current Assets & Liabilities Breakdown",
                            hover_data=['Nominal Amount (USD)'])
    pie_chart_fig.update_layout(legend=dict(title=None, orientation="h", y=0, yanchor="bottom", x=0.5, xanchor="center"))

    return card_assets_value,card_liab_value,time_series_fig,pie_chart_fig

@app.callback(
    [Output('current_risk_piechart','figure'),
    Output('target_risk_piechart','figure'),
    Output('current_target_risk_barchart','figure'),
    Output('cash_amount_to_target_card','children'),
    Output('equities_amount_to_target_card','children'),
    Output('fi_amount_to_target_card','children'),
    Output('card_current_risk_value','children'),
    Output('card_target_risk_value','children')],
    [Input('client_name_dropdown', 'value'),
    Input('base_numbers_checklist', 'value')]
) 
def risk_analysis_section(selected_client_name,selected_base_numbers):
    client_data = df.loc[df["Client Name"] == selected_client_name]

    if selected_base_numbers != []:
        client_data = df[df["Base Number"].isin(selected_base_numbers)]
    # client_data = df[df["Base Number"].isin(selected_base_numbers)]
    latest_date = client_data["Position As of Date"].max()
    latest_client_data = client_data[client_data['Position As of Date'] == latest_date]

    latest_client_data["Asset Class"].replace({"Investment Cash & Short Term Investments": "CASH"}, inplace=True)
    risk_asset_classes = ["CASH", "FIXED INCOME", "EQUITIES"]
    risk_analysis_df = latest_client_data[latest_client_data["Asset Class"].isin(risk_asset_classes)]

    total_nominal_amount = risk_analysis_df['Nominal Amount (USD)'].sum()
    target_risk_level = risk_analysis_df["Target Risk Level"].iloc[0]

    #print("Target Risk Level:",target_risk_level,type(target_risk_level))
    target_risk_df = risk_df[risk_df['Level'] == target_risk_level]

    group_by_risk_asset_class = risk_analysis_df\
    .groupby(['Asset Class'], as_index=False)\
    .agg({'Nominal Amount (USD)':'sum'})
    
    group_by_risk_asset_class.rename(columns={"Nominal Amount (USD)": "Current Nominal Amount (USD)"}, inplace=True)

    if 'CASH' not in group_by_risk_asset_class['Asset Class']:
        new_row = {'Asset Class':'CASH', 'Current Nominal Amount (USD)':0}
        group_by_risk_asset_class = group_by_risk_asset_class.append(new_row, ignore_index=True)

    if 'EQUITIES' not in group_by_risk_asset_class['Asset Class']:
        new_row = {'Asset Class':'EQUITIES', 'Current Nominal Amount (USD)':0}
        group_by_risk_asset_class = group_by_risk_asset_class.append(new_row, ignore_index=True)

    if 'FIXED INCOME' not in group_by_risk_asset_class['Asset Class']:
        new_row = {'Asset Class':'FIXED INCOME', 'Current Nominal Amount (USD)':0}
        group_by_risk_asset_class = group_by_risk_asset_class.append(new_row, ignore_index=True)
    
    group_by_risk_asset_class = group_by_risk_asset_class.drop_duplicates(subset=['Asset Class'])

    group_by_risk_asset_class["Current Breakdown by Percentage"] = group_by_risk_asset_class['Current Nominal Amount (USD)']*100/total_nominal_amount
    # print(target_risk_df)
    
    group_by_risk_asset_class = group_by_risk_asset_class.merge(target_risk_df, on="Asset Class")
    group_by_risk_asset_class.rename(columns={"Breakdown by Percentage": "Target Breakdown by Percentage"}, inplace=True)
    # print(group_by_risk_asset_class)
    group_by_risk_asset_class["Target Nominal Amount (USD)"] = total_nominal_amount*(group_by_risk_asset_class['Target Breakdown by Percentage'])/100

    group_by_risk_asset_class["Amount to Target"] = group_by_risk_asset_class["Target Nominal Amount (USD)"] - group_by_risk_asset_class["Current Nominal Amount (USD)"]
    # print("Total Nominal Amount:",total_nominal_amount)
    # print(group_by_risk_asset_class)

    eq_only_risk_df = risk_df[risk_df["Asset Class"]=="EQUITIES"]
    input_num = group_by_risk_asset_class.loc[group_by_risk_asset_class['Asset Class'] == "EQUITIES", 'Current Breakdown by Percentage'].iloc[0]
    nearest_eq_df = eq_only_risk_df.iloc[(eq_only_risk_df['Breakdown by Percentage']-input_num).abs().argsort()[:1]]
    current_risk_level = nearest_eq_df['Level'].iloc[0]

    current_risk_pie_chart = go.Figure(data=[go.Pie(
            labels=group_by_risk_asset_class['Asset Class'],
            values=group_by_risk_asset_class['Current Nominal Amount (USD)'],
            #hover_data=['Current Nominal Amount (USD)'],
            hole=0.7,
            sort=False)
    ])
    current_risk_pie_chart.update_layout(
        # title_text="Current Risk Analysis",
        annotations=[dict(text=f'Current Risk Level<br><b>{current_risk_level}</b>',x=0.5, y=0.5, font_size=20,showarrow=False)],
        showlegend=True
        )
    
    target_risk_pie_chart = go.Figure(data=[go.Pie(
            labels=group_by_risk_asset_class['Asset Class'],
            values=group_by_risk_asset_class['Target Nominal Amount (USD)'],
            #hover_data=['Target Nominal Amount (USD)'],
            hole=0.7,
            sort=False)
    ])
    target_risk_pie_chart.update_layout(
                            # title_text="Target Risk Analysis",
                            annotations=[dict(text=f'Target Risk Level<br><b>{target_risk_level}</b>', x=0.5, y=0.5, font_size=20, showarrow=False)])

    # print(list(group_by_risk_asset_class["Asset Class"]))
    desc_order_group_by_risk_df = group_by_risk_asset_class.sort_values('Asset Class', ascending=False)

    current_target_risk_barchart = go.Figure()

    current_target_risk_barchart.add_trace(
        go.Bar(
            y=desc_order_group_by_risk_df["Asset Class"],
            x=desc_order_group_by_risk_df["Current Breakdown by Percentage"],
            # text=group_by_risk_asset_class["Current Breakdown by Percentage"],
            # textposition='outside',
            # texttemplate = "%{text:.2s}",
            orientation="h",
            name = "Current"
        )
    )

    current_target_risk_barchart.add_trace(
        go.Scatter(
            mode="markers", 
            y=desc_order_group_by_risk_df["Asset Class"], 
            x=desc_order_group_by_risk_df["Target Breakdown by Percentage"],
            marker_symbol="line-ns",
            marker_line_color="red",
            marker_line_width=4, 
            marker_size=50, 
            name = "Target"
        )
    )

    current_target_risk_barchart.update_layout(
    # title="Risk Analysis: Current vs Target",
    yaxis_title="Asset Class",
    xaxis_title="Percentage",
    legend_title="",
    )

    # table_columns = [{"name": i, "id": i} for i in group_by_risk_asset_class[["Asset Class","Amount to Target"]].columns]
    # table_data = group_by_risk_asset_class[["Asset Class","Amount to Target"]].to_dict('records')

    cash_amount_to_target = group_by_risk_asset_class.loc[group_by_risk_asset_class['Asset Class'] == "CASH", "Amount to Target"].iloc[0]
    equities_amount_to_target = group_by_risk_asset_class.loc[group_by_risk_asset_class['Asset Class'] == "EQUITIES", "Amount to Target"].iloc[0]
    fi_amount_to_target = group_by_risk_asset_class.loc[group_by_risk_asset_class['Asset Class'] == "FIXED INCOME", "Amount to Target"].iloc[0]

    cash_sign, cash_color = return_sign_and_color_string(cash_amount_to_target)
    equities_sign, equities_color = return_sign_and_color_string(equities_amount_to_target)
    fi_sign, fi_color = return_sign_and_color_string(fi_amount_to_target)

    cash_amount_to_target_card = [
            html.H3("CASH", style={"color":"#003B70"}),
            html.H3(children=cash_sign+'${:.2f}'.format(abs(cash_amount_to_target)), style={"color":cash_color}),
        ]
        
    equities_amount_to_target_card = [
            html.H3("EQUITIES", style={"color":"#003B70"}),
            html.H3(children=equities_sign+'${:.2f}'.format(abs(equities_amount_to_target)), style={"color":equities_color}),
        ]

    fi_amount_to_target_card = [
            html.H3("FIXED INCOME", style={"color":"#003B70"}),
            html.H3(children=fi_sign+'${:.2f}'.format(abs(fi_amount_to_target)), style={"color":fi_color}),
        ]


    if current_risk_level == target_risk_level:
        target_status_string = "(In Target)"
        color = "#61BBA0" # Pastel Green
    else:
        target_status_string = "(Out of Target)"
        color = "#E17F79" # Pastel Green

    current_risk_level_card = [
            html.H5("Current Risk Level", style={"color":"#003B70"}),
            html.H2(f"Level {current_risk_level} "+target_status_string, style={"color":color}),
        ]

    target_risk_level_card = [
            html.H5("Target Risk Level", style={"color":"#003B70"}),
            html.H2(f"Level {target_risk_level} ", style={"color":"#003B70"}),
        ]

    return current_risk_pie_chart,target_risk_pie_chart,current_target_risk_barchart,\
        cash_amount_to_target_card,equities_amount_to_target_card,fi_amount_to_target_card,\
        current_risk_level_card,target_risk_level_card

@app.callback(
    [
    Output('reminders_tab_table','columns'),
    Output('reminders_tab_table','data'),
    Output('reminders_summary_content','children'),
    Output('reminders_summary_title','children'),
    Output('card_reminders_value','children'),
    ],
    [Input('client_name_dropdown', 'value'),
    Input('base_numbers_checklist', 'value')]
) 
def reminders_section(selected_client_name,selected_base_numbers): # currently not based on latest data
    client_data = df.loc[df["Client Name"] == selected_client_name]
    
    if selected_base_numbers != []:
        client_data = df[df["Base Number"].isin(selected_base_numbers)]
    # client_data = df[df["Base Number"].isin(selected_base_numbers)]
    Eq_FI = ["EQUITIES","FIXED INCOME"]
    client_asset_classes = list(client_data["Asset Class"].unique())
    if any(asset in client_asset_classes for asset in Eq_FI):
        client_data = client_data[client_data["Asset Class"].isin(Eq_FI)]

        common_columns = ["Client Name","Base Number","Position As of Date","Asset Class","Asset Sub Class","Name","Ticker","CCY","Nominal Units","Nominal Amount (CCY)",
        "Nominal Amount (USD)","Current Price","Closing Price","Average Cost","% Change from Avg Cost","1d %","5d %","1m %","6m %","12m %","YTD%",
        "Sector","Country (Domicile)","Region (Largest Revenue)"]
        equities_columns = ["Citi rating","Citi TARGET","% to target","Market Consensus","12M Div Yield (%)",
        "P/E Ratio","P/B Ratio","EPS (Current Year)","EPS (Next Year)","YoY EPS Growth (%)","50D MA","200D MA","Profit Margin",
        "Company Description"]
        equities_date = ["Dividend EX Date"]
        # "CoCo Action","Duration" are left out in fixed_income_columns because Client.csv do not have them
        fixed_income_columns = ["Rank","Moodys R","S&P R","Fitch","Coupon","YTC","YTM","Coupon type","Issue Date"]
        fixed_income_date = ["Maturity","Next Call Date"]
        reminders_columns = common_columns + equities_columns + fixed_income_columns + equities_date + fixed_income_date
        reminders_columns_without_dates = common_columns + equities_columns + fixed_income_columns

        reminder_df = client_data[reminders_columns]
        # filter by latest date to avoid duplications
        latest_date = reminder_df["Position As of Date"].max()
        latest_reminder_df = reminder_df[reminder_df['Position As of Date'] == latest_date]

        melted_reminder_df = latest_reminder_df.melt(id_vars=reminders_columns_without_dates,var_name="Reminder Type",value_name="Date")
        
        melted_reminder_df['Date'] = melted_reminder_df['Date'].dt.date
        melted_reminder_df["Position As of Date"] = melted_reminder_df["Position As of Date"].dt.date
        
        melted_reminder_df = melted_reminder_df.drop_duplicates()
        today = date.today()
        melted_reminder_df["Days Left"] = (melted_reminder_df['Date'] - today).dt.days

        next_reminder_date =  today + timedelta(weeks=52) # change time accordingly here
        time_string = "1 Year" # change accordingly here also

        df_next_reminder = melted_reminder_df[(melted_reminder_df['Date'] <= next_reminder_date) & (melted_reminder_df['Date'] >= today)]
        # df_all_reminder = melted_reminder_df[melted_reminder_df['Date'] >= today]
        df_next_reminder = df_next_reminder[["Name","Reminder Type","Date","Days Left"]]
        # print(df_next_reminder)
        df_next_reminder = df_next_reminder.drop_duplicates()

        df_next_reminder.sort_values("Date", inplace=True, ascending=True)
        # print(df_next_reminder)
        # print(df_next_reminder.info())
        df_all_reminder = melted_reminder_df[melted_reminder_df['Date'] >= today]

        df_all_reminder = df_all_reminder.drop_duplicates()

        df_all_reminder.sort_values("Date", inplace=True, ascending=True)

        all_reminders_count = len(df_all_reminder.index)
        
        if all_reminders_count != 0:
            reminder_tab_table_columns = [{"name": i, "id": i} for i in df_all_reminder.columns]
            reminder_tab_table_data = df_all_reminder.to_dict('records')
        else:
            reminder_tab_table_columns = []
            reminder_tab_table_data = []

        reminders_count_1m = len(df_next_reminder.index)

        reminders_summary_title = f'Reminders: Assets Due in {time_string}'

        if reminders_count_1m != 0:
            table_columns = [{"name": i, "id": i} for i in df_next_reminder.columns]
            table_data = df_next_reminder.to_dict('records')
            reminders_summary_content = return_reminders_summary_table(table_columns,table_data,reminder_tab_table_columns,reminder_tab_table_data)
            color = "#E17F79" #Pastel Red
        else:
            reminders_summary_content = f"There are no Assets due in {time_string}."
            color = "#003B70" #Dark Blue
            reminder_tab_table_columns = [{"name": f"There are no Assets due in {time_string}.", "id": "nan"}]
            reminder_tab_table_data = []

    else:
        reminders_count_1m = 0
        color = "#003B70" #Dark Blue
        reminders_summary_content = "Selected Client or Base Number has no relevant Assets to remind."
        reminder_tab_table_columns = [{"name": "Selected Client or Base Number has no relevant Assets to remind.", "id": "nan"}]
        reminder_tab_table_data = []

    card_reminders_value = [
            html.H5("Asset Reminders", style={"color":"#003B70"}),
            html.H2(f"{reminders_count_1m} (Due in {time_string})", style={"color":color}),
        ]


    return reminder_tab_table_columns, reminder_tab_table_data, reminders_summary_content,reminders_summary_title,card_reminders_value


@app.callback(
    Output("reminder-modal", "is_open"),
    [Input("reminder_button", "n_clicks"), Input("close-reminder", "n_clicks")],
    [State("reminder-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    [Output('profit_loss_breakdown_barchart','figure'),
    Output('card_profit_loss_value','children')],
    [Input('client_name_dropdown', 'value'),
    Input('base_numbers_checklist', 'value')]
) 
def profit_loss_section(selected_client_name,selected_base_numbers):
    client_data = df.loc[df["Client Name"] == selected_client_name]

    if selected_base_numbers != []:
        client_data = df[df["Base Number"].isin(selected_base_numbers)]
    # client_data = df[df["Base Number"].isin(selected_base_numbers)]
    latest_date = client_data["Position As of Date"].max()
    latest_client_data = client_data[client_data['Position As of Date'] == latest_date]

    client_asset_classes = list(latest_client_data["Asset Class"].unique())
    pl_asset_classes = ["EQUITIES","FIXED INCOME","ALTERNATIVE INVESTMENTS"]

    profit_loss_breakdown_barchart = px.bar()
    total_profit_loss = 0

    if any(asset in client_asset_classes for asset in pl_asset_classes):

        Eq_FI = ["EQUITIES","FIXED INCOME"]
        Eq_FI_df = latest_client_data[latest_client_data["Asset Class"].isin(Eq_FI)]
        Alt_df = latest_client_data[latest_client_data["Asset Class"]=="ALTERNATIVE INVESTMENTS"]

        Eq_FI_df = Eq_FI_df[["Client Name","Base Number","Asset Class","Estimated Profit/Loss"]]
        Alt_df = Alt_df[["Client Name","Base Number","Asset Class","Distribution Amount","Estimated Profit/Loss"]]

        Alt_Distribution_boolean = pd.notnull(Alt_df["Distribution Amount"])
        Alt_Distribution_df = Alt_df[Alt_Distribution_boolean]
        #print(Alt_Distribution_df.tail())
        Alt_Distribution_df = Alt_Distribution_df[["Client Name","Base Number","Asset Class","Distribution Amount"]][Alt_Distribution_df["Distribution Amount"]!=0]
        #print(Alt_Distribution_df.tail())
        Alt_Distribution_df.rename(columns={"Distribution Amount": "Estimated Profit/Loss"}, inplace=True)
        #print(Eq_FI_df.shape)
        #print(Alt_Distribution_df.shape)

        Alt_Profit_Loss_boolean = pd.isnull(Alt_df["Distribution Amount"])
        Alt_Profit_Loss_NA_df = Alt_df[["Client Name","Base Number","Asset Class","Estimated Profit/Loss"]][Alt_Profit_Loss_boolean]
        #print(Alt_Profit_Loss_NA_df.shape)
        Alt_Profit_Loss_zero_df = Alt_df[["Client Name","Base Number","Asset Class","Estimated Profit/Loss"]][Alt_df["Distribution Amount"]==0]
        #print(Alt_Profit_Loss_zero_df.shape)

        frames = [Eq_FI_df,Alt_Distribution_df,Alt_Profit_Loss_NA_df,Alt_Profit_Loss_zero_df]
        Profit_Loss_df = pd.concat(frames,ignore_index=True)
        #print(Profit_Loss_df.tail())
        #print(Profit_Loss_df.shape)

        decimals = 3
        Profit_Loss_df['Estimated Profit/Loss'] = Profit_Loss_df['Estimated Profit/Loss'].apply(lambda x: round(x, decimals))
        #print(Profit_Loss_df.head())
        total_profit_loss = Profit_Loss_df['Estimated Profit/Loss'].sum()

        group_by_PL_asset_class = Profit_Loss_df\
        .groupby(['Asset Class'], as_index=False)\
        .agg({'Estimated Profit/Loss':'sum'})

        group_by_PL_asset_class["Color"] = np.where(group_by_PL_asset_class["Estimated Profit/Loss"]<0, '#E17F79', '#3A6790')
        # print(group_by_PL_asset_class)
        profit_loss_breakdown_barchart = px.bar(
            group_by_PL_asset_class, x="Asset Class", y="Estimated Profit/Loss",
            hover_data={"Estimated Profit/Loss":":.3f"},
            text="Estimated Profit/Loss",color = "Color", color_discrete_sequence=group_by_PL_asset_class["Color"].unique())
        profit_loss_breakdown_barchart.update_layout(
            # title="Client's Current Profit/Loss Breakdown",
            xaxis_title="By Asset Class",
            yaxis_title="Profit/Loss",
            legend_title="",
            showlegend=False
            )
        profit_loss_breakdown_barchart.update_traces(
            textposition='outside',
            texttemplate = "%{text:.2s}")

    sign, color = return_sign_and_color_string(total_profit_loss)

    card_profit_loss_value = [
            html.H5("Current Profit/Loss", style={"color":"#003B70"}),
            html.H2(children=sign+"${:.3f}M".format(abs(total_profit_loss/1000000)), style={"color":color}),
        ]

    return profit_loss_breakdown_barchart,card_profit_loss_value


@app.callback(
    [Output("card_cash_liab_left1_value", "children"),
    Output("card_cash_liab_left2_value", "children"),
    Output("card_cash_liab_right1_value", "children"),
    Output("card_cash_liab_right2_value", "children"),
    Output("cash_liab_chart", "figure"),
    Output("cash_liab_table", "columns"),
    Output("cash_liab_table", "data")],
    [Input('client_name_dropdown', 'value'),
    Input('base_numbers_checklist', 'value')]
)
def render_cash_liab_tab_content_values(selected_client_name,selected_base_numbers):
    client_data = df.loc[df["Client Name"] == selected_client_name]
    
    if selected_base_numbers != []:
        client_data = df[df["Base Number"].isin(selected_base_numbers)]
    # client_data = df[df["Base Number"].isin(selected_base_numbers)]
    client_asset_classes = list(client_data["Asset Class"].unique())
    asset_classes = ['Investment Cash & Short Term Investments', 'Loans']

    if any(asset in client_asset_classes for asset in asset_classes):
        
        client_data = client_data[client_data["Asset Class"].isin(asset_classes)]
        client_data["Asset Class"].replace({"Investment Cash & Short Term Investments": "Cash"}, inplace=True)

        latest_date = client_data["Position As of Date"].max()
        latest_client_data = client_data[client_data['Position As of Date'] == latest_date]
        
        group_by_asset_class = latest_client_data\
        .groupby(['CCY','Asset Class'], as_index=False)\
        .agg({'Nominal Amount (USD)':'sum',
        'Loan / Cash Rate to client':'max'})
        #print(group_by_asset_class)
        transformed_group_by_asset_class = \
        group_by_asset_class.pivot(index='CCY', columns='Asset Class', values='Nominal Amount (USD)')\
        .reset_index().fillna(0)
        #print(transformed_group_by_asset_class)
        transformed_group_by_rate = \
        group_by_asset_class.pivot(index='CCY', columns='Asset Class', values='Loan / Cash Rate to client')\
        .reset_index().fillna(0).rename(columns={"Cash":"Cash Rate","Loans":"Loans Rate"})
        df_merged = pd.merge(transformed_group_by_asset_class, transformed_group_by_rate, on=["CCY"])
        #print(df_merged)
        non_zero_cash_loan_df = group_by_asset_class.loc[group_by_asset_class['Nominal Amount (USD)'] != 0]

        if 'Loans' not in df_merged.columns:
            df_merged["Loans"] = 0

        if 'Loans Rate' not in df_merged.columns:
            df_merged["Loans Rate"] = "-"
        
        cash_count = np.count_nonzero(df_merged["Cash"], axis=0)
        loans_count = np.count_nonzero(df_merged["Loans"], axis=0)

        total_loans = df_merged.Loans.sum()
        total_cash = df_merged.Cash.sum()
        df_merged = df_merged.append({'CCY' : 'TOTAL' , \
            'Cash' : total_cash, 'Loans' : total_loans,\
            'Cash Rate':'-', 'Loans Rate' : '-'} , ignore_index=True)

        # table_columns = [{"name": i, "id": i} for i in df_merged[["CCY","Cash","Cash Rate","Loans","Loans Rate"]].columns]
        # table_data = df_merged[["CCY","Cash","Cash Rate","Loans","Loans Rate"]].to_dict('records')
       
        table_columns = [{"name": i, "id": i} for i in df_merged.columns]
        table_data = df_merged.to_dict('records')

        cash_loan_barchart = px.bar(non_zero_cash_loan_df, x="CCY", y="Nominal Amount (USD)",
                hover_data={"Nominal Amount (USD)":":.3f"},
                text="Nominal Amount (USD)",color='Asset Class', barmode='group')
        cash_loan_barchart.update_layout(
        title="Cash vs Liabilities",
        xaxis_title="Currency",
        yaxis_title="Total Nominal Amount (USD)",
        legend_title="",
        )
        cash_loan_barchart.update_traces(
            textposition='outside',
            texttemplate = "%{text:.2s}")
        
        
        no_of_cash_CCY_card = [
            html.H5("Number of CCY (Cash)"),
            html.H2(f"{cash_count}"),
        ]
        no_of_loan_CCY_card = [
            html.H5("Number of CCY (Loans)"),
            html.H2(f"{loans_count}"),
        ]
        total_cash_sign, total_cash_color = return_sign_and_color_string(total_cash)
        if total_cash == 0 or np.isnan(total_cash): 
            total_cash_color = "white"
            total_cash = 0
        total_cash_value_card = [
            html.H5("Total Cash"),
            html.H2(total_cash_sign+"${:.3f}M".format(abs(total_cash/1000000)), style={"color":total_cash_color}),
        ]
        total_loans_sign, total_loans_color = return_sign_and_color_string(abs(total_loans)*(-1))
        if total_loans == 0 or np.isnan(total_loans): 
            total_loans_color = "white"
            total_loans = 0
        total_loan_value_card = [
            html.H5("Total Loans"),
            html.H2("${:.3f}M".format(abs(total_loans/1000000)), style={"color":total_loans_color}),
        ]
        card_custom_left1_value = total_cash_value_card
        card_custom_left2_value = total_loan_value_card
        card_custom_right1_value = no_of_cash_CCY_card
        card_custom_right2_value = no_of_loan_CCY_card
        selected_tab_chart = cash_loan_barchart
        selected_tab_table_columns = table_columns
        selected_tab_table_data = table_data
    else:
        card_custom_left1_value = []
        card_custom_left2_value = []
        card_custom_right1_value = []
        card_custom_right2_value = []
        selected_tab_chart = go.Figure()
        selected_tab_table_columns = [{"name": "Selected Client or Base Number has no information for CASH & LIABILITIES.", "id": "nan"}]
        selected_tab_table_data = []

    return card_custom_left1_value, card_custom_left2_value, card_custom_right1_value, card_custom_right2_value, selected_tab_chart, selected_tab_table_columns, selected_tab_table_data

@app.callback(
    [Output("card_equities_left1_value", "children"),
    Output("card_equities_left2_value", "children"),
    Output("card_equities_right1_value", "children"),
    Output("card_equities_right2_value", "children"),
    Output("equities_chart", "figure"),
    Output("equities_table", "columns"),
    Output("equities_table", "data")],
    [Input('client_name_dropdown', 'value'),
    Input('base_numbers_checklist', 'value')]
)
def render_equities_tab_content_values(selected_client_name,selected_base_numbers):
    client_data = df.loc[df["Client Name"] == selected_client_name]
    
    if selected_base_numbers != []:
        client_data = df[df["Base Number"].isin(selected_base_numbers)]
    # client_data = df[df["Base Number"].isin(selected_base_numbers)]
    client_asset_classes = list(client_data["Asset Class"].unique())

    if "EQUITIES" in client_asset_classes:
        client_equity_data = client_data[client_data["Asset Class"]=="EQUITIES"]
        client_equity_data["Exchange Rate"] = client_equity_data["Nominal Amount (USD)"]/client_equity_data["Nominal Amount (CCY)"]
        client_equity_data["Original Amount Paid"] = client_equity_data["Nominal Units"]*client_equity_data["Average Cost"]*client_equity_data["Exchange Rate"]
        #print("Nominal Amount (USD)",client_equity_data["Nominal Amount (USD)"])
        client_equity_data["Estimated Profit/Loss"] = client_equity_data["Nominal Amount (USD)"]-client_equity_data["Original Amount Paid"]
        client_equity_data["% Profit/Loss"] = client_equity_data["Estimated Profit/Loss"]*100/client_equity_data["Original Amount Paid"]

        group_by_date_equity = client_equity_data.\
        groupby(['Position As of Date'])["Original Amount Paid", "Estimated Profit/Loss"].\
        apply(lambda x : x.sum()).reset_index()

        group_by_date_equity["% Profit/Loss"] = group_by_date_equity["Estimated Profit/Loss"]*100/group_by_date_equity["Original Amount Paid"]

        equity_daily_percentage_fig = px.line(group_by_date_equity,x="Position As of Date", y="% Profit/Loss", 
                    text="Estimated Profit/Loss", title="Daily % Profit/Loss")
        equity_daily_percentage_fig.update_traces(
                    textposition="top center",
                    texttemplate = "%{text:.2s}")
        
        latest_date = group_by_date_equity["Position As of Date"].max()
        latest_group_by_date_data = group_by_date_equity[group_by_date_equity['Position As of Date'] == latest_date].reset_index(drop=True)
        # print(latest_group_by_date_data)
        
        latest_total_profit_loss = latest_group_by_date_data.at[0,'Estimated Profit/Loss']
        latest_total_return_percentage = latest_group_by_date_data.at[0,'% Profit/Loss']
        # print(latest_total_profit_loss)

        latest_data = client_equity_data[client_equity_data['Position As of Date'] == latest_date]
        equity_latest_table_df = latest_data[["Name","Ticker","Estimated Profit/Loss","% Profit/Loss","Citi rating"]]
        
        equity_latest_table_df.sort_values("% Profit/Loss", inplace=True, ascending=True)
        # print(equity_latest_table_df)
        #buy_count = equity_latest_table_df[equity_latest_table_df["Citi rating"]=="buy"].count()
        buy_count = equity_latest_table_df[equity_latest_table_df["Citi rating"] == "buy"].count()[0]
        sell_count = equity_latest_table_df[equity_latest_table_df["Citi rating"] == "sell"].count()[0]
        # print(type(buy_count))
        # print(f"No. of buy: {buy_count}")

        table_columns = [{"name": i, "id": i} for i in equity_latest_table_df.columns]
        table_data = equity_latest_table_df.to_dict('records')

        no_of_buy_card = [
            html.H5("Number of Buy"),
            html.H2(f"{buy_count}"),
        ]
        no_of_sell_card = [
            html.H5("Number of Sell"),
            html.H2(f"{sell_count}"),
        ]
        total_pl_sign, total_pl_color = return_sign_and_color_string(latest_total_profit_loss)
        if latest_total_profit_loss == 0 or np.isnan(latest_total_profit_loss): 
            total_pl_color = "white"
            latest_total_profit_loss = 0
        total_profit_loss_card = [
            html.H5("Total Profit/Loss"),
            html.H2(total_pl_sign+"${:.3f}M".format(abs(latest_total_profit_loss/1000000)), style={"color":total_pl_color}),
        ]
        total_return_sign, total_return_color = return_sign_and_color_string(latest_total_return_percentage)
        if latest_total_return_percentage == 0 or np.isnan(latest_total_return_percentage): 
            total_return_color = "white"
            latest_total_return_percentage = 0
        total_return_percentage_card = [
            html.H5("% Total Return"),
            html.H2(total_return_sign+"{:.3f}%".format(abs(latest_total_return_percentage)), style={"color":total_return_color}),
        ]
        card_custom_left1_value = total_profit_loss_card
        card_custom_left2_value = total_return_percentage_card
        card_custom_right1_value = no_of_buy_card
        card_custom_right2_value = no_of_sell_card
        selected_tab_chart = equity_daily_percentage_fig
        selected_tab_table_columns = table_columns
        selected_tab_table_data = table_data
    else:
        card_custom_left1_value = []
        card_custom_left2_value = []
        card_custom_right1_value = []
        card_custom_right2_value = []
        selected_tab_chart = go.Figure()
        selected_tab_table_columns = [{"name": "Selected Client or Base Number has no information for EQUITIES.", "id": "nan"}]
        selected_tab_table_data = []

    return card_custom_left1_value, card_custom_left2_value, card_custom_right1_value, card_custom_right2_value, selected_tab_chart, selected_tab_table_columns, selected_tab_table_data

@app.callback(
    [Output("card_fixed_income_left1_value", "children"),
    Output("card_fixed_income_left2_value", "children"),
    Output("card_fixed_income_right1_value", "children"),
    Output("card_fixed_income_right2_value", "children"),
    Output("fixed_income_chart", "figure"),
    Output("fixed_income_table", "columns"),
    Output("fixed_income_table", "data")],
    [Input('client_name_dropdown', 'value'),
    Input('base_numbers_checklist', 'value'),
    Input('credit_rating_scales_dropdown', 'value')]
)
def render_fixed_income_tab_content_values(selected_client_name,selected_base_numbers,selected_credit_rating):
    client_data = df.loc[df["Client Name"] == selected_client_name]
    
    if selected_base_numbers != []:
        client_data = df[df["Base Number"].isin(selected_base_numbers)]
    # client_data = df[df["Base Number"].isin(selected_base_numbers)]
    client_asset_classes = list(client_data["Asset Class"].unique())

    if "FIXED INCOME" in client_asset_classes:
        SP_rating_dict = {
            "AAA" : "Prime",
            "AA+" : "High Grade",
            "AA" : "High Grade",
            "AA-" : "High Grade",
            "A+" : "Upper Medium Grade",
            "A" : "Upper Medium Grade",
            "A-" : "Upper Medium Grade",
            "BBB+" : "Lower Medium Grade",
            "BBB" : "Lower Medium Grade",
            "BBB-" : "Lower Medium Grade",
            "BB+" : "Non Investment Grade Speculative",
            "BB" : "Non Investment Grade Speculative",
            "BB-" : "Non Investment Grade Speculative",
            "B+" : "Highly Speculative",
            "B" : "Highly Speculative",
            "B-" : "Highly Speculative",
            "CCC+" : "Substantial Risks",
            "CCC" : "Extremely Speculative"
        }
        Moody_rating_dict = {
            "Aaa" : "Prime",
            "Aa1" : "High Grade",
            "Aa2" : "High Grade",
            "Aa3" : "High Grade",
            "A1" : "Upper Medium Grade",
            "A2" : "Upper Medium Grade",
            "A3" : "Upper Medium Grade",
            "Baa1" : "Lower Medium Grade",
            "Baa2" : "Lower Medium Grade",
            "Baa3" : "Lower Medium Grade",
            "Ba1" : "Non Investment Grade Speculative",
            "Ba2" : "Non Investment Grade Speculative",
            "Ba3" : "Non Investment Grade Speculative",
            "B1" : "Highly Speculative",
            "B2" : "Highly Speculative",
            "B3" : "Highly Speculative",
            "Caa1" : "Substantial Risks",
            "Caa2" : "Extremely Speculative"
        }
        Fitch_rating_dict = SP_rating_dict

        client_fi_data = client_data[client_data["Asset Class"]=="FIXED INCOME"]
        client_fi_data["Exchange Rate"] = client_fi_data["Nominal Amount (USD)"]/client_fi_data["Nominal Amount (CCY)"]
        client_fi_data["Original Amount Paid"] = client_fi_data["Nominal Units"]*client_fi_data["Average Cost"]*client_fi_data["Exchange Rate"]
        client_fi_data["Estimated Profit/Loss"] = client_fi_data["Nominal Amount (USD)"]-client_fi_data["Original Amount Paid"]
        client_fi_data["% Profit/Loss"] = client_fi_data["Estimated Profit/Loss"]*100/client_fi_data["Original Amount Paid"]

        group_by_date_fi = client_fi_data.groupby(['Position As of Date'])["Original Amount Paid", "Estimated Profit/Loss"].apply(lambda x : x.sum()).reset_index()

        group_by_date_fi["% Profit/Loss"] = group_by_date_fi["Estimated Profit/Loss"]*100/group_by_date_fi["Original Amount Paid"]
                    
        # rating_selection = ["S&P", "Moody's", "Fitch"]
        selected_rating = "S&P"
        if selected_credit_rating != None:
            selected_rating = selected_credit_rating

        excel_column_mapping = {
            "S&P": "S&P R",
            "Moody's": "Moodys R",
            "Fitch": "Fitch",
            }
        rating_dict_mapping = {
            "S&P": SP_rating_dict,
            "Moody's": Moody_rating_dict,
            "Fitch": Fitch_rating_dict,
            }
        risk_level_mapping = {
            "Prime":"Low Risk",
            "High Grade":"Low Risk",
            "Upper Medium Grade":"Medium Risk",
            "Lower Medium Grade":"Medium Risk",
            "Non Investment Grade Speculative":"High Risk",
            "Highly Speculative":"High Risk",
            "Substantial Risks":"High Risk",
            "Extremely Speculative":"High Risk"
        }
        selected_dict = rating_dict_mapping[selected_rating]
        selected_excel_col = excel_column_mapping[selected_rating]
        
        # client_fi_data["Client Credit Rating"] = selected_dict[client_fi_data[selected_excel_col]]
        client_fi_data["Client Credit Rating"] = client_fi_data[selected_excel_col].apply(lambda x: selected_dict[x])
        # client_fi_data["Risk Level"] = risk_level_mapping[client_fi_data["Client Credit Rating"]]
        client_fi_data["Risk Level"] = client_fi_data["Client Credit Rating"].apply(lambda x: risk_level_mapping[x])

        group_by_date_credit_rate = client_fi_data.groupby(['Position As of Date','Client Credit Rating']).size().reset_index(name='counts')

        latest_date = group_by_date_credit_rate["Position As of Date"].max()
        latest_group_by_date_data = group_by_date_credit_rate[group_by_date_credit_rate['Position As of Date'] == latest_date].reset_index(drop=True)
        
        # print(group_by_date_fi)
        latest_total_profit_loss = group_by_date_fi.loc[group_by_date_fi['Position As of Date'] == latest_date, 'Estimated Profit/Loss'].iloc[0]
        latest_total_return_percentage = group_by_date_fi.loc[group_by_date_fi['Position As of Date'] == latest_date, '% Profit/Loss'].iloc[0]

        credit_rating_barchart = px.bar(latest_group_by_date_data, 
                                x='Client Credit Rating', y='counts', color='Client Credit Rating',
                                text='counts',
                                title = "Current Credit Rating Counts by "+selected_rating)

        credit_rating_barchart.update_traces(
            textposition='outside')

        latest_data = client_fi_data[client_fi_data['Position As of Date'] == latest_date]

        medium_risk_count = latest_data[latest_data["Risk Level"] == "Medium Risk"].count()[0]
        high_risk_count = latest_data[latest_data["Risk Level"] == "High Risk"].count()[0]

        fi_latest_table_df = latest_data[["Name","Ticker","Estimated Profit/Loss","% Profit/Loss",
                            "Client Credit Rating","Maturity","Next Call Date"]]
        
        fi_latest_table_df.sort_values("% Profit/Loss", inplace=True, ascending=True)

        table_columns = [{"name": i, "id": i} for i in fi_latest_table_df.columns]
        table_data = fi_latest_table_df.to_dict('records')

        no_of_medium_risks_card = [
            html.H5("Number of Medium Risks"),
            html.H2(f"{medium_risk_count}", style={"color":"#E17F79"}),
        ]
        no_of_high_risks_card = [
            html.H5("Number of High Risks"),
            html.H2(f"{high_risk_count}", style={"color":"#E17F79"}),
        ]
        total_pl_sign, total_pl_color = return_sign_and_color_string(latest_total_profit_loss)
        if latest_total_profit_loss == 0 or np.isnan(latest_total_profit_loss): 
            total_pl_color = "white"
            latest_total_profit_loss = 0
        total_profit_loss_card = [
            html.H5("Total Profit/Loss"),
            html.H2(total_pl_sign+"${:.3f}M".format(abs(latest_total_profit_loss/1000000)), style={"color":total_pl_color}),
        ]

        total_return_sign, total_return_color = return_sign_and_color_string(latest_total_return_percentage)
        if latest_total_return_percentage == 0 or np.isnan(latest_total_return_percentage): 
            total_return_color = "white"
            latest_total_return_percentage = 0
        total_return_percentage_card = [
            html.H5("% Total Return"),
            html.H2(total_return_sign+"{:.3f}%".format(abs(latest_total_return_percentage)), style={"color":total_return_color}),
        ]
        card_custom_left1_value = total_profit_loss_card
        card_custom_left2_value = total_return_percentage_card
        card_custom_right1_value = no_of_medium_risks_card
        card_custom_right2_value = no_of_high_risks_card
        selected_tab_chart = credit_rating_barchart
        selected_tab_table_columns = table_columns
        selected_tab_table_data = table_data
    else: 
        card_custom_left1_value = []
        card_custom_left2_value = []
        card_custom_right1_value = []
        card_custom_right2_value = []
        selected_tab_chart = go.Figure()
        selected_tab_table_columns = [{"name": "Selected Client or Base Number has no information for FIXED INCOME.", "id": "nan"}]
        selected_tab_table_data = []

    return card_custom_left1_value, card_custom_left2_value, card_custom_right1_value, card_custom_right2_value, selected_tab_chart, selected_tab_table_columns, selected_tab_table_data

@app.callback(
    [Output("card_alternatives_left1_value", "children"),
    Output("card_alternatives_left2_value", "children"),
    Output("card_alternatives_right1_value", "children"),
    Output("card_alternatives_right2_value", "children"),
    Output("alternatives_chart", "figure"),
    Output("alternatives_table", "columns"),
    Output("alternatives_table", "data")],
    [Input('client_name_dropdown', 'value'),
    Input('base_numbers_checklist', 'value')]
)
def render_alternatives_tab_content_values(selected_client_name,selected_base_numbers):
    client_data = df.loc[df["Client Name"] == selected_client_name]
    
    if selected_base_numbers != []:
        client_data = df[df["Base Number"].isin(selected_base_numbers)]
    # client_data = df[df["Base Number"].isin(selected_base_numbers)]
    client_asset_classes = list(client_data["Asset Class"].unique())

    if "ALTERNATIVE INVESTMENTS" in client_asset_classes:
        client_ai_data = client_data[client_data["Asset Class"]=="ALTERNATIVE INVESTMENTS"]
        
        client_ai_data["% Outstanding Amount"] = client_ai_data["Outstanding Commitment"]*100/client_ai_data["Commitment Amount"]
        client_ai_data["% Return on Contribution"] = ((client_ai_data["Distribution Amount"]/client_ai_data["Contribution Amount"])-1)*100

        group_by_date_ai = client_ai_data.\
        groupby(['Position As of Date'])["Contribution Amount", "Distribution Amount"].\
        apply(lambda x : x.sum()).reset_index()

        group_by_date_ai["% Total Return on Contribution"] = ((group_by_date_ai["Distribution Amount"]/group_by_date_ai["Contribution Amount"])-1)*100

        ai_daily_percentage_fig = px.line(group_by_date_ai,x="Position As of Date", y="% Total Return on Contribution", 
                    text="Distribution Amount", title="Daily % Total Return on Contribution")
        ai_daily_percentage_fig.update_traces(
                    textposition="top center",
                    texttemplate = "%{text:.2s}")

        latest_date = group_by_date_ai["Position As of Date"].max()
        latest_group_by_date_data = group_by_date_ai[group_by_date_ai['Position As of Date'] == latest_date].reset_index(drop=True)
        latest_total_distribution_amount = latest_group_by_date_data.at[0,'Distribution Amount']
        latest_total_return_contribution = latest_group_by_date_data.at[0,'% Total Return on Contribution']

        latest_data = client_ai_data[client_ai_data['Position As of Date'] == latest_date]
        ai_latest_table_df = latest_data[["Asset Sub Class","Name","Commitment Amount","Contribution Amount","% Outstanding Amount","Distribution Amount","% Return on Contribution"]]
        
        ai_latest_table_df.sort_values("% Return on Contribution", inplace=True, ascending=True)
        negative_returns_count = np.sum((ai_latest_table_df["% Return on Contribution"] < 0).values.ravel())
        positive_returns_count = np.sum((ai_latest_table_df["% Return on Contribution"] > 0).values.ravel())
        # print(negative_returns_count)
        # print(positive_returns_count)

        table_columns = [{"name": i, "id": i} for i in ai_latest_table_df.columns]
        table_data = ai_latest_table_df.to_dict('records')

        no_of_positive_returns_card = [
            html.H5("Number of Positive Returns"),
            html.H2(f"{positive_returns_count}", style={"color":"#61BBA0"}),
        ]
        no_of_negative_returns_card = [
            html.H5("Number of Negative Returns"),
            html.H2(f"{negative_returns_count}", style={"color":"#E17F79"}),
        ]
        total_dis_sign, total_dis_color = return_sign_and_color_string(latest_total_distribution_amount)
        if latest_total_distribution_amount == 0 or np.isnan(latest_total_distribution_amount): 
            total_dis_color = "white"
            latest_total_distribution_amount = 0

        total_distribution_card = [
            html.H5("Total Distribution Amount"),
            html.H2(total_dis_sign+"${:.3f}M".format(abs(latest_total_distribution_amount/1000000)), style={"color":total_dis_color}),
        ]
        total_return_sign, total_return_color = return_sign_and_color_string(latest_total_return_contribution)
        if latest_total_return_contribution == 0 or np.isnan(latest_total_return_contribution): 
            total_return_color = "white"
            latest_total_return_contribution = 0

        # print(latest_total_return_contribution)
        total_return_contribution_card = [
            html.H5("% Total Return on Contribution"),
            html.H2(total_return_sign+"{:.3f}%".format(abs(latest_total_return_contribution)), style={"color":total_return_color}),
        ]
        card_custom_left1_value = total_distribution_card
        card_custom_left2_value = total_return_contribution_card
        card_custom_right1_value = no_of_positive_returns_card
        card_custom_right2_value = no_of_negative_returns_card
        selected_tab_chart = ai_daily_percentage_fig
        selected_tab_table_columns = table_columns
        selected_tab_table_data = table_data
        
    else:
        card_custom_left1_value = []
        card_custom_left2_value = []
        card_custom_right1_value = []
        card_custom_right2_value = []
        selected_tab_chart = go.Figure()
        selected_tab_table_columns = [{"name": "Selected Client or Base Number has no information for ALTERNATIVE INVESTMENTS.", "id": "nan"}]
        selected_tab_table_data = []

    return card_custom_left1_value, card_custom_left2_value, card_custom_right1_value, card_custom_right2_value, selected_tab_chart, selected_tab_table_columns, selected_tab_table_data

@app.callback(
    [Output("card_capital_markets_left1_value", "children"),
    Output("card_capital_markets_left2_value", "children"),
    Output("card_capital_markets_right1_value", "children"),
    Output("card_capital_markets_right2_value", "children"),
    Output("capital_markets_chart", "figure"),
    Output("capital_markets_table", "columns"),
    Output("capital_markets_table", "data")],
    [Input('client_name_dropdown', 'value'),
    Input('base_numbers_checklist', 'value')]
)
def render_capital_markets_tab_content_values(selected_client_name,selected_base_numbers):
    client_data = df.loc[df["Client Name"] == selected_client_name]
    
    if selected_base_numbers != []:
        client_data = df[df["Base Number"].isin(selected_base_numbers)]
    # client_data = df[df["Base Number"].isin(selected_base_numbers)]
    client_asset_classes = list(client_data["Asset Class"].unique())

    if "CAPITAL MARKETS" in client_asset_classes:
        client_cm_data = client_data[client_data["Asset Class"]=="CAPITAL MARKETS"]
        
        group_by_date_cm = client_cm_data.\
        groupby(['Position As of Date'])["Nominal Amount (CCY)", "Nominal Amount (USD)"].\
        apply(lambda x : x.sum()).reset_index()
    
        daily_cm_fig = go.Figure()

        daily_cm_fig.add_trace(
            go.Bar(
                x=group_by_date_cm["Position As of Date"],
                y=group_by_date_cm["Nominal Amount (USD)"],
                text=group_by_date_cm["Nominal Amount (USD)"],
                textposition='outside',
                texttemplate = "%{text:.2s}",
                name="Nominal Amount (USD)"
            ))

        daily_cm_fig.add_trace(
            go.Scatter(
                x=group_by_date_cm["Position As of Date"],
                y=group_by_date_cm["Nominal Amount (CCY)"],
                text=group_by_date_cm["Nominal Amount (CCY)"],
                textposition='top center',
                texttemplate = "%{text:.2s}",
                name="Nominal Amount (CCY)"
            ))
        
        daily_cm_fig.update_layout(
        title="Daily Capital Market Nominal Amount",
        xaxis_title="Date",
        yaxis_title="Nominal Amount",
        legend_title="",
        )

        latest_date = group_by_date_cm["Position As of Date"].max()
        latest_group_by_date_data = group_by_date_cm[group_by_date_cm['Position As of Date'] == latest_date].reset_index(drop=True)
        latest_total_nominal_amount = latest_group_by_date_data.at[0,'Nominal Amount (USD)']
        
        latest_data = client_cm_data[client_cm_data['Position As of Date'] == latest_date]
        cm_latest_table_df = latest_data[["Asset Sub Class","Trade Number","Nominal Amount (CCY)","Nominal Amount (USD)"]]
        cm_latest_table_df.sort_values("Nominal Amount (USD)", inplace=True, ascending=True)
        
        no_of_asset_sub_class = len(latest_data["Asset Sub Class"].unique())

        negative_values_count = np.sum((cm_latest_table_df["Nominal Amount (USD)"] < 0).values.ravel())
        positive_values_count = np.sum((cm_latest_table_df["Nominal Amount (USD)"] > 0).values.ravel())

        table_columns = [{"name": i, "id": i} for i in cm_latest_table_df.columns]
        table_data = cm_latest_table_df.to_dict('records')

        no_of_positive_values_card = [
            html.H5("Number of Positive Trades"),
            html.H2(f"{positive_values_count}", style={"color":"#61BBA0"}),
        ]
        no_of_negative_values_card = [
            html.H5("Number of Negative Trades"),
            html.H2(f"{negative_values_count}", style={"color":"#E17F79"}),
        ]
        total_nominal_sign, total_nominal_color = return_sign_and_color_string(latest_total_nominal_amount)
        if latest_total_nominal_amount == 0 or np.isnan(latest_total_nominal_amount): 
            total_nominal_color = "white"
            latest_total_nominal_amount = 0
        total_nominal_amount_card = [
            html.H5("Total Nominal Amount (USD)"),
            html.H2(total_nominal_sign+"${:.3f}M".format(abs(latest_total_nominal_amount/1000000)), style={"color":total_nominal_color}),
        ]
        no_of_sub_assets_card = [
            html.H5("Number of Different Sub Assets"),
            html.H2(f"{no_of_asset_sub_class}"),
        ]
        card_custom_left1_value = total_nominal_amount_card
        card_custom_left2_value = no_of_sub_assets_card
        card_custom_right1_value = no_of_positive_values_card
        card_custom_right2_value = no_of_negative_values_card
        selected_tab_chart = daily_cm_fig
        selected_tab_table_columns = table_columns
        selected_tab_table_data = table_data       
    
    else:
        card_custom_left1_value = []
        card_custom_left2_value = []
        card_custom_right1_value = []
        card_custom_right2_value = []
        selected_tab_chart = go.Figure()
        selected_tab_table_columns = [{"name": "Selected Client or Base Number has no information for CAPITAL MARKETS.", "id": "nan"}]
        selected_tab_table_data = []

    return card_custom_left1_value, card_custom_left2_value, card_custom_right1_value, card_custom_right2_value, selected_tab_chart, selected_tab_table_columns, selected_tab_table_data


if __name__ == '__main__':
    app.run_server(debug=True)
    app.config['suppress_callback_exceptions'] = True