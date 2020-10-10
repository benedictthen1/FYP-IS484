import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import dash_html_components as html
import numpy as np
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
import yfinance as yf
import dash_bootstrap_components as dbc
import plotly.express as px
from datetime import datetime, timedelta
from pytz import timezone
import yahoo_fin.stock_info as si
import datetime as dt
import pathlib

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server
app.config["suppress_callback_exceptions"] = True

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

df = pd.read_csv(DATA_PATH.joinpath("TestData.csv"),encoding='latin1')
df =df[df['Asset Class'].notnull()]

numeric_cols = ['% Change from Avg Cost','YTD%', '1d %', '5d %', '1m % ', '6m %', '12m %'] + ['Nominal Amount (USD)','Nominal Units','Nominal Amount (CCY)','Current Price','Closing Price', 'Average Cost']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col].astype("float")
    df[col] = df[col].round(2)
print(df.columns)

#IMPORT MAY DATA FOR CLIENT SIDE
cdf = pd.read_csv(DATA_PATH.joinpath("TestDataManipulatedAllCols.csv"),encoding='latin1')

### Change Date Format ###
cdf['Position As of Date']= pd.to_datetime(cdf['Position As of Date']) 
cdf['Position As of Date'] = cdf['Position As of Date'].apply(lambda x: dt.datetime.strftime(x, '%Y-%d-%m'))
cdf['Position As of Date']= pd.to_datetime(cdf['Position As of Date']) 

### Limit decimal places of all numeric columns in df ###
numeric_cols = cdf.select_dtypes([np.number]).columns.to_list()
decimals = 3
cdf[numeric_cols] = cdf[numeric_cols].apply(lambda x: round(x, decimals))

### Get all client names ###
client_names = cdf["Client Name"].unique()

#Client Table 
# df = df[df["Asset Class"].isin(["EQUITIES","ALTERNATIVE INVESTMENTS","CAPITAL MARKETS","FIXED INCOME"])]
df = df[df["Asset Class"].isin(["EQUITIES"])]

# Column name in postgreSQL: "Estimated Profit/Loss" 
df["Profit/Loss"] = (df["Current Price"] - df["Average Cost"]) * df["Nominal Units"]
#df["Profit/Loss %"] = df["Profit/Loss"]/(df["Current Price"]*df["Nominal Units"]) * 100
client_table = df.groupby(["Client Name"])[["Profit/Loss","Nominal Amount (CCY)"]].sum().reset_index()
client_table["Profit/Loss"] = client_table["Profit/Loss"].round(2)
client_table["Nominal Amount (CCY)"] = client_table["Nominal Amount (CCY)"].round(2)
client_table["Profit/Loss %"] = client_table["Profit/Loss"]/client_table["Nominal Amount (CCY)"]*100
client_table["Profit/Loss %"] = client_table["Profit/Loss %"].round(1)
client_table["Nominal Amount"] = client_table["Nominal Amount (CCY)"]
client_table = client_table[["Client Name","Nominal Amount","Profit/Loss","Profit/Loss %"]]
client_table = client_table.sort_values("Profit/Loss %")

#Stock Market Table 
company_df = df[["Client Name","Asset Class","Name","Ticker","YTD%","1d %","5d %","1m % ","6m %","12m %"]]
company_df = company_df[company_df["Asset Class"]== "EQUITIES"]
count_client = company_df.groupby(["Name"])["Client Name"].nunique().reset_index(name="No of Client").sort_values("Name")

company_df2 = df[["Asset Class","Name","Ticker","YTD%","1d %","5d %","1m % ","6m %","12m %"]]
company_df2= company_df2.drop_duplicates().sort_values("Name")

company_df_final = pd.merge(count_client,company_df2,on="Name")
company_df_final = company_df_final[["Name","Ticker","No of Client","1d %"]]
company_df_final = company_df_final.sort_values('1d %')

def discrete_background_color_bins(client_table, n_bins=6, columns= ['Profit/Loss %']):
    import colorlover
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    df_numeric_columns = client_table[columns]

    df_max = df_numeric_columns.max().max()
    df_min = df_numeric_columns.min().min()
    ranges = [
        ((df_max - df_min) * i) + df_min
        for i in bounds
    ]
    ranges = np.linspace(df_min-1, df_max+1, num=10)
    ranges = ranges.astype(int)
    print(ranges)
    #ranges = [-100, -75,-50, -25 ,-10 ,0, 10, 25, 50, 75, 100]
    #ranges = np.arange(df_min, df_max,100).tolist()

    styles = []
    colours = ['rgb(215,25,28)','rgb(215,25,28)', 'rgb(201,122,44)','rgb(201,122,44)',
    'rbg(209, 206, 29)','rbg(214, 201, 54)','rgb(26,150,65)']
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        backgroundColor = colours[i-1]
        # #print("BACKGROUND " + str(backgroundColor))
        # #color = 'white' if i > len(bounds) / 2. else 'inherit'
        # #color = 'white'
        color = 'inherit'
        backgroundColor = colorlover.scales[str(n_bins)]['div']['RdYlGn'][i - 1]
        # color = 'white' if i > len(bounds) / 2. else 'inherit'

        for column in df_numeric_columns:
            styles.append({
                'if': {
                    'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                    ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                    'column_id': column
                },
                'backgroundColor': backgroundColor,
                'color': color
            })

    return (styles)
print(df.columns)
(styles) = discrete_background_color_bins(client_table)
(styles2) = discrete_background_color_bins(company_df_final,columns=['1d %'])

#print(client_table)

client_dtable = html.Div([
    dash_table.DataTable(
        id='client_table',
        sort_action='native',
        style_cell={'textAlign': 'left','textOverflow': 'ellipsis','border': '1px solid black'},
        style_data_conditional=styles,
        style_as_list_view=True,
        fixed_rows={'headers': True},
        style_table={'overflowY': 'auto','height': '345px',"width": '615px'},
        style_data={'maxWidth': '80px','minWidth': '80px'},
        style_header={'fontWeight': 'bold', 'height': 'auto','whiteSpace': 'normal','border': '1px solid black'},
        columns=[{"name": i, "id": i} for i in client_table.columns],
        data=client_table.to_dict('records')
    )
])

coy_table = html.Div([
    dash_table.DataTable(
        id='coy_table',
        sort_action='native',
        style_cell={'textAlign': 'left','textOverflow': 'ellipsis','border': '1px solid black'},
        style_data_conditional=styles2,
        style_as_list_view=True,
        fixed_rows={'headers': True},
        style_table={'overflowY': 'auto','height': '345px',"width":"600px"},
        style_header={'fontWeight': 'bold', 'height': 'auto','whiteSpace': 'normal','border': '1px solid grey'},
        style_data={'maxWidth': '120px','minWidth': '120px'},
        columns=[{"name": i, "id": i} for i in company_df_final.columns],
        data=company_df_final.to_dict('records')
    )
])

client_coy_table = html.Div([
    dash_table.DataTable(
        id='client_coy_table',
        sort_action='native',
        style_cell={'textAlign': 'center','textOverflow': 'ellipsis','font_size': '11px','border': '1px solid black'},
        style_as_list_view=True,
        fixed_rows={'headers': True},
        style_table={'overflowY': 'auto','height': '345px',"width": '380px'},
        style_data={'maxWidth': '70px','minWidth': '70px'},
        style_header={'fontWeight': 'bold', 'height': 'auto','whiteSpace': 'normal','border': '1px solid grey'},
        #columns=[{"name": i, "id": i} for i in client_table.columns],
        #data=client_table.to_dict('records')
    )
])
#candlestick initiation
candle = go.Figure()

#Ticker Statistic Information Table
stats_table = html.Div([
    dash_table.DataTable(
        id='stats_table',
        style_header = {'display': 'none'},
        style_cell={'textAlign': 'left','backgroundColor': "#f9f9f9",},
        style_as_list_view=True,
        style_table={'overflowY': 'auto','height': '345px'},
        #columns=[{"name": i, "id": i} for i in df.columns],
        #data=df.to_dict('records'))
    )
])

#CARD ASSET AND LIAB
card_assets = dbc.Card([
    dbc.CardBody(id='card_assets_value'),
],inverse=True,outline=False, color="success"),

# Total Liability Value Card (This card is under Part 1, refer to app layout)
card_liab = dbc.Card([
    dbc.CardBody(id='card_liab_value'),
],inverse=True,outline=False, color="danger"),

# card custom my foot
card_custom_left1 = dbc.Card(
    [
        dbc.CardBody(id='card_custom_left1_value',
        ),
    ],color="dark",  inverse=True, outline=False,
)

# Custom Card Left 2
card_custom_left2 = dbc.Card(
    [
        dbc.CardBody(id='card_custom_left2_value',
        ),
    ],color="dark",  inverse=True, outline=False,
)

# Custom Card Right 1
card_custom_right1 = dbc.Card(
    [
        dbc.CardBody(id='card_custom_right1_value',
        ),
    ],color="dark",  inverse=True, outline=False,
)

# Custom Card Right 2
card_custom_right2 = dbc.Card(
    [
        dbc.CardBody(id='card_custom_right2_value',
        ),
    ],color="dark",  inverse=True, outline=False,
)

# APP LAYOUT
layout = html.Div([
  
    # Top Banners Metrics
    html.Div([
        html.Div([html.H2("120"),html.H6("Total Clients")],className="client_metrics"),
        html.Div([html.H2("29"),html.H6("Losing Clients")],className="client_metrics"),
        html.Div([html.H2("89"),html.H6("Profiting Clients")],className="client_metrics"),
        html.Div([html.H2("23"),html.H6("Client to remind")],className="client_metrics"),
        html.Div([html.H2("16"),html.H6("Risky Clients")],className="client_metrics"),
    ],id="banner_group"),

    html.Div([
    html.Div([
        html.H2("Client Performance"),
        client_dtable,
    ],id="top_client_table"),

    # html.Div([
    #     dcc.Graph(id="client_asset_bar"),
    # ]),

    html.Div([
        html.H2("Stocks Performance"),
        coy_table,
    ],id="top_coy_table"),
    ],id="combine_home_tables"),
    #CLIENT MODAL
    dbc.Modal([
        dbc.ModalHeader("Client Portfolio Information"),
        dbc.ModalBody(
            html.Div([
                
                #html.H3(id="client_select"),
                # Total Assets Value Card (This card is under Part 1, refer to app layout)

                dbc.Row([
                    dbc.Col([
                        html.H3("Client's Name:"),
                        dcc.Dropdown(
                            id='client_name_dropdown',
                            options=[{'label': name, 'value': name} for name in client_names],
                            value=client_names[0])
                     ],width={'size':3},
                    ),
                    dbc.Col([
                        html.H3("Client's Base Numbers:"),
                        dcc.Checklist(
                            id='base_numbers_checklist',labelStyle={'display': 'inline-block'}
                    )],width={'size':9},
                    ), 
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(card_assets, width=3),
                    dbc.Col(card_liab, width=3)
                ], justify="start"),

                dbc.Row([
                    dbc.Col([dcc.Graph(id='asset_liab_timeseries')], width={'size':7},),
                    dbc.Col([dcc.Graph(id='asset_class_piechart')], width={'size':5},),
                ]),

                dbc.Row([
                    dbc.Col([
                        html.H3("Choose Asset Type:"),
                        dcc.Dropdown(id='client_asset_type_dropdown')
                    ],width={'size':3},),
                ]),
                html.Br(),

                dbc.Row([
                    dbc.Col(card_custom_left1, width=3),
                    dbc.Col(card_custom_left2, width=3),
                    dbc.Col(card_custom_right1, width=3),
                    dbc.Col(card_custom_right2, width=3)
                ], justify="start"),
                dbc.Row([
                    dbc.Col([dcc.Graph(id='selected_tab_chart')],
                            width={'size':6},),
                    dbc.Col([dcc.Graph(id='selected_tab_table')],
                            width={'size':6},),
                ]),  

                html.Br(),


            ],id="client_modal_table"), 
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-scroll", className="ml-auto")
        ),
    ],id="client_modal",scrollable=True,size="xl",
        style={"max-width": "none", "width": "95%"},
    ),

    #FINANCE MODAL
    dbc.Modal([
        dbc.ModalHeader([
            html.Div([
                html.H5("Stocks Information"),
                #dbc.Button("Close", id="close-body-scroll", className="ml-auto")
            ],id="modal_header"),
        ]),
        dbc.ModalBody(html.Div([
            #Ticker Search Box
            html.Div([
                dcc.Input(id="input", type="text", placeholder="search ticker"),
                dbc.Button("Apply", color="dark",size="sm", id="search-button",n_clicks=0, className="mr-1"),
                ],className="search_style"),
            html.P(id = "price_date"),

            #Ticker Price Banner
            html.Div([
                html.Div([
                    html.H5(id ="coy_name"),
                    html.Div([
                        html.H6(id = "close_price"),
                        html.H6(id = "price_diff"),
                    ],id = "tic_price_info"),
           
                ],id="ticker_info_table"),

                html.Div([html.Div(id="ytd"),html.H6("YTD %")],className="tick_metrics"),
                html.Div([html.Div(id="1d"),html.H6("1D %")],className="tick_metrics"),
                html.Div([html.Div(id="5d"),html.H6("5D %")],className="tick_metrics"),
                html.Div([html.Div(id="1m"),html.H6("1M %")],className="tick_metrics"),
                html.Div([html.Div(id="6m"),html.H6("6M %")],className="tick_metrics"),
                html.Div([html.Div(id="12m"),html.H6("12M %")],className="tick_metrics"),
        
            ],className="container-display"),

            #Initiation the Tabs
            html.Div([
                html.Div([
                    dbc.Tabs([
                        dbc.Tab(
                            label="Statistics", 
                            tab_id="tab-1",
                            children=html.Div(className='control-tab',children = [
                                stats_table
                            ]),
                        ),
                        dbc.Tab(
                        label="Clients", 
                        tab_id="tab-2",
                        children=html.Div(className='control-tab',children = [
                            client_coy_table
                        ]),
                        ),
                        dbc.Tab(label="News", tab_id="tab-3"),
                        dbc.Tab(
                            label="Desc", 
                            tab_id="tab-4",
                            children=html.Div(className='control-tab',children = [
                                html.P(id="coy_desc")
                            ]),
                        ),
                    ],
                    id="tabs",
                    active_tab="tab-1",
                
                    ),
                ],className='tabs_group'),

                html.Div([
                    #Candle stick top buttons
                    dbc.Button("1D", color="dark",size="sm", id="1d-button",n_clicks=0, className="mr-1"),
                    dbc.Button("5D", color="dark",size="sm", id="5d-button",n_clicks=0, className="mr-1"),
                    dbc.Button("1M", color="dark",size="sm", id="1m-button",n_clicks=0, className="mr-1"),
                    dbc.Button("6M", color="dark",size="sm", id="6m-button",n_clicks=0, className="mr-1"),
                    dbc.Button("1Y", color="dark",size="sm", id="1y-button",n_clicks=0, className="mr-1"),
                    #Candlestick
                    dcc.Graph(figure=candle, id="candle"),

                ],className="mini_container"),
            ], className="container-display"),

            #BAR CHARTS
            html.Div([
                dcc.Graph(id="income_chart"),
            ],className="fin_bar_group"),
            html.Div([
                dcc.Graph(id="balance_chart"),
            ],className="fin_bar_group"),
            html.Div([
                dcc.Graph(id="cashflow_bar"),
            ],className="fin_bar_group")


        ],id="fin_modal_table")),
        dbc.ModalFooter(dbc.Button("Close", id="close-body-scroll", className="ml-auto")),
        ],id="fin_modal",scrollable=True,size="xl",
        style={"max-width": "none", "width": "95%"},
    ),

])

#================================================== CALLBACKS =============================================================================
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

#Click on Table cell to activate Finance Modal
app.callback(Output("fin_modal", "is_open"),
            [Input("coy_table","selected_cells"),Input("close-body-scroll", "n_clicks")],
            [State("fin_modal", "is_open")],)(toggle_modal)

# #Information pass in Finance Modal
# @app.callback(Output("tic_select", "children"),
#             [Input("coy_table","selected_cells"),Input("coy_table","derived_virtual_data")])
# def toggle_details(t1, t2):
#     if t1:
#         row_num = t1[0]["row"]
#         col_name = t2[row_num]["Ticker"]
#         ticker = yf.Ticker(col_name)
#         return col_name

#Click on Table cell to activate Client Modal
app.callback(Output("client_modal", "is_open"),
            [Input("client_table","selected_cells"),Input("close-scroll", "n_clicks")],
            [State("client_modal", "is_open")],)(toggle_modal)

#Information pass in Client Modal
# @app.callback(Output("client_select", "children"),
#             [Input("client_table","selected_cells"),Input("client_table","derived_virtual_data")])
# def toggle_details2(t1, t2):
#     if t1:
#         row_num = t1[0]["row"]
#         col_name = t2[row_num]["Client Name"]
#         return col_name

# #Client Asset class breakdown
# @app.callback(Output("client_asset_bar", "figure"),
#             [Input("client_table","selected_cells"),Input("client_table","derived_virtual_data")])
# def client_asset_bar(table_input1,table_input2):
#     if table_input1:
#         row_num = table_input1[0]["row"]
#         client_name = table_input2[row_num]["Client Name"]

#         cdata = df[df["Client Name"]== client_name]
#         cdata["Profit/Loss"] = cdata["Profit/Loss"].round(2)
#         cdata = cdata.groupby(["Asset Class"])[["Profit/Loss","Nominal Amount (CCY)"]].sum().reset_index()
#         # client_table["Nominal Amount (CCY)"] = client_table["Nominal Amount (CCY)"].round(2)
#         # client_table["Profit/Loss %"] = client_table["Profit/Loss"]/client_table["Nominal Amount (CCY)"]*100
#         # client_table["Profit/Loss %"] = client_table["Profit/Loss %"].round(1)
#         # client_table = client_table[["Client Name","Nominal Amount (CCY)","Profit/Loss","Profit/Loss %"]]

#         print("TEST")
#         print(cdata)

#         fig = go.Figure(data=[
#         go.Bar(name='Total Asset', y=cdata["Asset Class"], x=cdata["Profit/Loss"],orientation='h',marker_color="green", text = cdata["Profit/Loss"],textfont_size=8,  textposition='outside',),
        
#         ])
#     return fig

################################################## FINANCE POP UP PAGE  ##########################################################################
#Ticker Banner Metrics
@app.callback([Output("ytd", "children"),Output("1d", "children"),Output("5d", "children"),Output("1m", "children"),
               Output("6m", "children"),Output("12m", "children")],
              [Input("search-button","n_clicks"),Input("coy_table","selected_cells"),Input("coy_table","derived_virtual_data")],
              [State("input","value")])
def banner(search_btn,table_input1,table_input2,search):
    if search_btn:
        tdf = yf.Ticker(search)
    elif table_input1:
        row_num = table_input1[0]["row"]
        col_name = table_input2[row_num]["Ticker"]
        tdf= yf.Ticker(col_name)
    else:
        tdf = yf.Ticker("aapl")

    hist = tdf.history(period="1mo",interval="1d")
    d1 = ((hist["Close"].iloc[-1] - hist["Close"].iloc[-2])/hist["Close"].iloc[-1]*100).round(2)
    d5 = ((hist["Close"].iloc[-1] - hist["Close"].iloc[-6])/hist["Close"].iloc[-1]*100).round(2)
    m1 = ((hist["Close"].iloc[-1] - hist["Close"].iloc[1])/hist["Close"].iloc[-1]*100).round(2)
    hist2 = tdf.history(period="6mo")
    m6 = ((hist2["Close"].iloc[-1] - hist2["Close"].iloc[1])/hist2["Close"].iloc[-1]*100).round(2)
    hist3 = tdf.history(period="1y")
    y1 = ((hist3["Close"].iloc[-1] - hist3["Close"].iloc[1])/hist3["Close"].iloc[-1]*100).round(2)
    hist4 = tdf.history(period="ytd")
    ytd = ((hist4["Close"].iloc[-1] - hist4["Close"].iloc[1])/hist4["Close"].iloc[-1]*100).round(2)
  
    return ytd,d1,d5,m1,m6,y1

#Clients invested in the company table
@app.callback([Output("client_coy_table", "data"),Output("client_coy_table","columns")],
            [Input("search-button","n_clicks"),Input("coy_table","selected_cells"),Input("coy_table","derived_virtual_data")],
            [State("input","value")])
def coy_client_Table(search_btn,table_input1,table_input2,search):
    data = df
    if search_btn:
        #search = search.str.upper
        data = df
        data=df[df["Ticker"]==search]
    elif table_input1:
        data = df
        row_num = table_input1[0]["row"]
        col_name = table_input2[row_num]["Ticker"]
        data=df[df["Ticker"]==col_name]
    else:
        data = df
        data=df[df["Ticker"]=="AAPL"]
    
    data = data[data["Asset Class"]== "EQUITIES"]
    data["Profit/Loss"] = (data["Current Price"] - data["Average Cost"]) * data["Nominal Units"]
    #df["Profit/Loss %"] = df["Profit/Loss"]/(df["Current Price"]*df["Nominal Units"]) * 100
    client_table = data.groupby(["Client Name"])[["Profit/Loss","Nominal Amount (CCY)"]].sum().reset_index()
    client_table["Profit/Loss"] = client_table["Profit/Loss"].round(2)
    client_table["Nominal Amount (CCY)"] = client_table["Nominal Amount (CCY)"].round(2)
    client_table["Profit/Loss %"] = client_table["Profit/Loss"]/client_table["Nominal Amount (CCY)"]*100
    client_table["Profit/Loss %"] = client_table["Profit/Loss %"].round(1)
    client_table["Nominal Amount"] = client_table["Nominal Amount (CCY)"]
    client_table = client_table[["Client Name","Nominal Amount","Profit/Loss","Profit/Loss %"]]
    
    data =client_table.to_dict('records')
    columns=([{'name': i, 'id': i} for i in client_table.columns])

    return data,columns

#Stats Stock Table 
@app.callback([Output("stats_table", "columns"),Output("stats_table", "data"),Output("coy_desc","children")],
            [Input("search-button","n_clicks"),Input("coy_table","selected_cells"),Input("coy_table","derived_virtual_data")],
            [State("input","value")])
def stats_table_input(search_btn,table_input1,table_input2,search):
    if search_btn:
        ndf = yf.Ticker(search)
        #print(ndf.info)
    elif table_input1:
        row_num = table_input1[0]["row"]
        col_name = table_input2[row_num]["Ticker"]
        ndf= yf.Ticker(col_name)
    else:
        ndf = yf.Ticker("aapl")
    stock = ndf.info
    data = {'Metrcs Name':  ['Close', 'Open', "Ask", "52wk High", "52wk Low", "Volume", "Volume Average",
                             'Market Cap','Beta','PE ratio','PEG Ratio','EPS','Dividend Yield', 'Profit Margin', 'Earning Quar Growth'],
            'Metrics values': [stock["previousClose"], stock["open"], stock["ask"],stock["fiftyTwoWeekHigh"],stock["fiftyTwoWeekLow"],
                            stock["volume"],stock["averageVolume10days"],stock['marketCap'],stock['beta'],stock["forwardPE"],stock["pegRatio"],stock['trailingEps'],
                            stock['dividendYield'],stock['profitMargins'],stock['earningsQuarterlyGrowth']],
                            }
    data = pd.DataFrame(data, columns = ['Metrcs Name', 'Metrics values'])
    columns=([{'name': i, 'id': i} for i in data.columns])
    data=data.to_dict('records')
    dec = stock['longBusinessSummary']
    return columns, data, dec

#Ticker Price and CandleStick callbacks.
@app.callback([Output("candle","figure"),Output("coy_name","children"),Output("close_price","children"),Output("price_diff","children"),Output("price_date","children")],
              [Input("search-button","n_clicks"),Input("1d-button","n_clicks"),Input("5d-button","n_clicks"),Input("1m-button","n_clicks")
              ,Input("coy_table","selected_cells"),Input("coy_table","derived_virtual_data")],
              [State("input","value")])
def click(search_click,d1,d5,m1,table_input1,table_input2,search_input):
    
    if search_input:
        ndf= yf.Ticker(search_input)
        df = ndf.history(interval="1m",period="1d")
    elif table_input1:
        row_num = table_input1[0]["row"]
        col_name = table_input2[row_num]["Ticker"]
        ndf= yf.Ticker(col_name)
        df = ndf.history(interval="1m",period="1d")
    else:
        ndf= yf.Ticker("aapl")
        df = ndf.history(interval="1m",period="1d")

    #Ticker Price callback (top-left)
    coy_name = str(ndf.info['shortName']) + " (" + str(ndf.info['symbol']) + ")"
    hist = ndf.history(interval="1m",period="1d").tail()
    close_price = hist["Close"].iloc[[4]]
    price_diff_raw = round(float(hist["Close"].iloc[[4]])-float(hist["Close"].iloc[[3]]),2)
    price_diff_per = round(price_diff_raw/float(hist["Close"].iloc[[4]]) * 100,2)
    price_diff = str(price_diff_raw) + " (" + str(price_diff_per) + "%)"
    hist["date"] = hist.index
    hist["date"] = hist["date"].dt.date
    price_date = "Last Updated: " + str(hist["date"].tail(1)).split(" ")[0].split("e")[2]

    #candle stick
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    
    if "1d-button" in changed_id:
        df = ndf.history(interval="1m",period="1d")
    elif "5d-button" in changed_id:
        df = ndf.history(interval="5m",period="5d")
    elif "1m-button" in changed_id:
        df = ndf.history(interval= "60m",period="1mo")

    df["Datetime"] = df.index.strftime("%d/%m/%Y, %H:%M:%S")

    trace1 = {'x': df.Datetime,'open': df.Open,'close': df.Close,'high': df.High,'low': df.Low,
        'type': 'candlestick','name': "placeholder",'showlegend': False}

    avg_30 = df.Close.rolling(window=30, min_periods=1).mean()
    avg_50 = df.Close.rolling(window=50, min_periods=1).mean()
    df["Average"] = df.Close.mean().round(2)

    trace2 = {'x': df.Datetime,'y': avg_30,'type': 'scatter','mode': 'lines',
        'line': {'width': 1.5,'color': 'blue'},'name': 'MA30'}

    trace3 = {'x': df.Datetime,'y': avg_50,'type': 'scatter','mode': 'lines',
        'line': {'width': 1.5,'color': 'orange'},'name': 'MA50'}

    trace4 = {'x': df.Datetime,'y': df.Average,'type': 'scatter','mode': 'lines',
        'line': {'dash': 'dash','width': 1.5,'color': 'Grey'},'name': 'Mean'}

    data = [trace1,trace2,trace3,trace4]
    layout = go.Layout({
        'plot_bgcolor': '#f9f9f9',
        'paper_bgcolor': '#f9f9f9',
        'margin': {'t': 13, 'l': 10, "b": 1, "r":10},
        #'legend': {'x':0.7, 'y':0.95, 'orientation':"h"}
    })
    
    dates =  ["10 AM","11 AM","12 PM","1 PM","2 PM","3 PM"]
    spaces = [30,88,148,205,270,330]
        
    if "1d-button" in changed_id:
        dates =  ["10 AM","11 AM","12 PM","1 PM","2 PM","3 PM"]
        spaces = [30,88,148,205,270,330]
    elif "5d-button" in changed_id:
        dates =  df["Datetime"].index.strftime("%d/%m/%Y").unique()
        spaces = [40, 115, 190, 270, 350]
    elif "1m-button" in changed_id:
        dates =  df["Datetime"].index.strftime("%h %d").unique()[::5]
        spaces = [1, 40, 70, 100, 135]


    candle = go.Figure(data=data, layout=layout)
    candle.update_xaxes(linewidth=0.5, linecolor='Grey', gridcolor='#D3D3D3')
    candle.update_layout(
        xaxis_rangeslider_visible=False,autosize=False, height = 370,width=900, yaxis_showgrid=False, 
        xaxis = dict(
            #title = 'date',
            showticklabels = True,
            showgrid=True,
            tickmode = 'array',
            tickvals = spaces,
            ticktext = dates
            ),
    )
    

    return candle, coy_name, close_price, price_diff,price_date

#Cashflow Bar Chart
@app.callback(Output("cashflow_bar", "figure"),
            [Input("search-button","n_clicks"),Input("coy_table","selected_cells"),Input("coy_table","derived_virtual_data")],
            [State("input","value")])
def bar_chart_input(search_btn,table_input1,table_input2,search):
    if search_btn:
        cashflow = si.get_cash_flow(search)
        cf = cashflow.T
    elif table_input1:
        row_num = table_input1[0]["row"]
        col_name = table_input2[row_num]["Ticker"]
        cashflow = si.get_cash_flow(col_name)
        cf = cashflow.T
    else:
        cashflow = si.get_cash_flow("aapl")
        cf = cashflow.T

    cf["date"] = cf.index
    date= cf["date"].dt.year
    op = (cf["totalCashFromOperatingActivities"]/1000000000).astype(float).round(2)
    invest = (cf["totalCashflowsFromInvestingActivities"]/1000000000).astype(float).round(2)
    fin = (cf["totalCashFromFinancingActivities"]/1000000000).astype(float).round(2)

    color, color2, color3 = np.array(['rgb(255,255,255)']*op.shape[0]), np.array(['rgb(255,255,255)']*invest.shape[0]), np.array(['rgb(255,255,255)']*fin.shape[0])
    color[op<0],  color2[invest<0],  color3[fin<0]='crimson','crimson','crimson'
    color[op>=0], color2[invest>=0],  color3[fin>=0]='green','green','green'

    fig4 = go.Figure(data=[
        go.Bar(name='Operating', x=date, y=cf["totalCashFromOperatingActivities"],marker=dict(color=color.tolist()), text = op,textfont_size=8, textposition='outside',),
        go.Bar(name='Investing', x=date, y=cf["totalCashflowsFromInvestingActivities"],marker=dict(color=color2.tolist()),  text = invest,textfont_size=8, textposition='outside',),
        go.Bar(name='Financing', x=date, y=cf["totalCashFromFinancingActivities"],marker=dict(color=color3.tolist()),  text = fin,textfont_size=8, textposition='outside',),
    ])
    # Change the bar mode
    fig4.update_layout(barmode='group',title_text='Cash Flow',title_x=0.5,width = 444,margin=dict(t=70,b=20,l=55,r=40),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    fig4.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1,xanchor="right",x=0.85,font=dict(size=9,),))
    return fig4

#Balance Sheet Bar
@app.callback(Output("balance_chart", "figure"),
            [Input("search-button","n_clicks"),Input("coy_table","selected_cells"),Input("coy_table","derived_virtual_data")],
            [State("input","value")])
def bs_chart_input(search_btn,table_input1,table_input2,search):
    if search_btn:
        balance_sheet = si.get_balance_sheet(search)
        bs = balance_sheet.T
    elif table_input1:
        row_num = table_input1[0]["row"]
        col_name = table_input2[row_num]["Ticker"]
        balance_sheet = si.get_balance_sheet(col_name)
        bs = balance_sheet.T
    else:
        balance_sheet = si.get_balance_sheet("aapl")
        bs = balance_sheet.T

    bs["date"] = bs.index
    date= bs["date"].dt.year
    ta = (bs["totalAssets"]/1000000000).astype(float).round(2)
    tl = (bs["totalLiab"]/1000000000).astype(float).round(2)

    # color=np.array(['rgb(255,255,255)']*ta.shape[0])
    # color[ta<0]='red'
    # color[ta>=0]='green'

    fig3 = go.Figure(data=[
        go.Bar(name='Total Asset', x=date, y=bs["totalAssets"],marker_color="green", text = ta,textfont_size=8,  textposition='outside',),
        go.Bar(name='Total Liability', x=date, y=bs["totalLiab"],marker_color="crimson",  text = tl,textfont_size=8,  textposition='outside',),
    ])
    # Change the bar mode
    fig3.update_layout(barmode='group',width = 444,title_text='Asset vs Liability',title_x=0.5,margin=dict(t=70,b=20,l=55,r=40),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    fig3.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1,xanchor="right",x=0.75,font=dict(size=9,),))
    return fig3


#income statement bar
@app.callback(Output("income_chart", "figure"),
            [Input("search-button","n_clicks"),Input("coy_table","selected_cells"),Input("coy_table","derived_virtual_data")],
            [State("input","value")])
def income_bar(search_btn,table_input1,table_input2,search):
    if search_btn:
        balance_sheet = si.get_income_statement(search)
        bs = balance_sheet.T
    elif table_input1:
        row_num = table_input1[0]["row"]
        col_name = table_input2[row_num]["Ticker"]
        balance_sheet = si.get_income_statement(col_name)
        bs = balance_sheet.T
    else:
        balance_sheet = si.get_income_statement("aapl")
        bs = balance_sheet.T
    # print(bs.columns)
    # print(bs)
    bs["date"] = bs.index

    date= bs["date"].dt.year
    netincome = (bs["netIncome"]/1000000000).astype(float).round(2)
    totalrev = (bs["totalRevenue"]/1000000000).astype(float).round(2)
    opincome = (bs["operatingIncome"]/1000000000).astype(float).round(2)

    color=np.array(['rgb(255,255,255)']*netincome.shape[0])
    color[netincome<0]='crimson'
    color[netincome>=0]='green'

    fig2 = go.Figure(data=[
        go.Bar(name='Net Income', x=date, y=bs["netIncome"],marker=dict(color=color.tolist()), text = netincome,textfont_size=8, textposition='outside'),
        go.Bar(name='Total Revenue', x=date, y=bs["totalRevenue"], text = totalrev,textfont_size=8, textposition='outside',visible='legendonly'),
        go.Bar(name='Operating Income', x=date, y=bs["operatingIncome"], text = opincome,textfont_size=8, textposition='outside',visible='legendonly')
    ])
    # Change the bar mode
    fig2.update_layout(barmode='group',width = 444,title_text='Income Statement',title_x=0.5,margin=dict(t=70,b=20,l=55,r=40),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    fig2.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1,xanchor="right",x=0.95,font=dict(size=9,),))
    
    return fig2

######### MAY CLIENT PAGE CALLBACKS ##########################################################################
@app.callback(Output('client_name_dropdown','value'),
              [Input("client_table","selected_cells"),Input("client_table","derived_virtual_data")])
def link(t1,t2):
    if t1:
        row_num = t1[0]["row"]
        col_name = t2[row_num]["Client Name"]
        return col_name
    else:
        return client_names[0]

@app.callback(
    [Output('base_numbers_checklist','options'),
    Output('base_numbers_checklist','value')],
    [Input('client_name_dropdown', 'value')]
) 
def set_base_number_multi_selection(client_name):
    client_data = df.loc[df["Client Name"] == client_name]
    base_numbers = list(client_data["Base Number"].unique())
    multi_select_options = [{'label': base_number, 'value': base_number} for base_number in base_numbers]
    return multi_select_options, base_numbers

@app.callback(
    [Output('card_assets_value','children'),
    Output('card_liab_value','children'),
    Output('asset_liab_timeseries','figure'),
    Output('asset_class_piechart','figure')],
    [Input('base_numbers_checklist', 'value')]
) 
def overall_section(selected_base_numbers):
    client_data = cdf[cdf["Base Number"].isin(selected_base_numbers)]
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

    card_assets_value = [
            html.H4("Total Assets", className="card-title"),
            html.H6("${:.3f}M".format(latest_total_cash/1000000), className="card-subtitle"),
        ]

    card_liab_value = [
            html.H4("Total Liabilities", className="card-title"),
            html.H6("${:.3f}M".format(latest_total_loans/1000000), className="card-subtitle"),
        ]
    
    time_series_fig = px.area(group_by_date_asset_class, x="Position As of Date", y="Nominal Amount (USD)", 
                                color = "Asset Class", color_discrete_sequence=['#dea5a4', '#779ecb'],
                                title = "Client's Total Assets & Liabilities over time")
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
                            title="Current Client's Asset Class Breakdown",
                            hover_data=['Nominal Amount (USD)'])

    return card_assets_value,card_liab_value,time_series_fig,pie_chart_fig

@app.callback(
    [Output('client_asset_type_dropdown','options'),
    Output('client_asset_type_dropdown','value')],
    [Input('base_numbers_checklist', 'value')]
) 
def set_asset_class_dropdown(selected_base_numbers):
    client_data = cdf[cdf["Base Number"].isin(selected_base_numbers)]
    asset_classes = list(client_data["Asset Class"].unique())
    
    excel_tabs = ["EQUITIES","FIXED INCOME","ALTERNATIVE INVESTMENTS","CAPITAL MARKETS"]
    asset_dropdown_options_list = ["CASH & LIABILITIES"]
    for tab in excel_tabs:
        if tab in asset_classes:
            asset_dropdown_options_list.append(tab)
    
    asset_dropdown_options = [{'label': tab_option, 'value': tab_option} for tab_option in asset_dropdown_options_list]
    
    return asset_dropdown_options, asset_dropdown_options_list[0]

@app.callback(
    [Output('card_custom_left1_value','children'),
    Output('card_custom_left2_value','children'),
    Output('card_custom_right1_value','children'),
    Output('card_custom_right2_value','children'),
    Output('selected_tab_chart','figure'),
    Output('selected_tab_table','figure')],
    [Input('base_numbers_checklist', 'value'),
    Input('client_asset_type_dropdown', 'value')]
) 
def custom_section(selected_base_numbers,selected_tab):
    client_data = cdf[cdf["Base Number"].isin(selected_base_numbers)]
    
    if selected_tab == "CASH & LIABILITIES":
        asset_classes = ['Investment Cash & Short Term Investments', 'Loans']
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
        .reset_index().fillna('-').rename(columns={"Cash":"Cash Rate","Loans":"Loans Rate"})
        df_merged = pd.merge(transformed_group_by_asset_class, transformed_group_by_rate, on=["CCY"])
        #print(df_merged)
        non_zero_cash_loan_df = group_by_asset_class.loc[group_by_asset_class['Nominal Amount (USD)'] != 0]

        if 'Loans' not in df_merged.columns:
            df_merged["Loans"] = 0

        if 'Loans Rate' not in df_merged.columns:
            df_merged["Loans Rate"] = "-"
        
        cash_count = np.count_nonzero(df_merged["Cash"], axis=0)
        loans_count = np.count_nonzero(df_merged["Loans"], axis=0)
        # print(f"cash_count: {cash_count}")
        # print("loans_count:",loans_count)

        total_loans = df_merged.Loans.sum()
        total_cash = df_merged.Cash.sum()
        df_merged = df_merged.append({'CCY' : '<b>TOTAL</b>' , \
            'Cash' : f'<b>{total_cash}</b>', 'Loans' : f'<b>{total_loans}</b>',\
            'Cash Rate':'<b>-</b>', 'Loans Rate' : '<b>-</b>'} , ignore_index=True)


        cash_loan_table = go.Figure(data=[go.Table(
                    header=dict(values=["<b>Currency</b>","<b>Cash (USD)</b>",
                                    "<b>Loans (USD)</b>","<b>Cash Rate (%)</b>","<b>Loan Rate (%)</b>"],
                                fill_color='paleturquoise',
                                align='left'),
                    cells=dict(values=[df_merged.CCY, \
                    df_merged.Cash,
                    df_merged.Loans,
                    df_merged["Cash Rate"],
                    df_merged["Loans Rate"]],
                            fill_color='lavender',
                            align='left'))
                ])

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
            html.H4("Number of CCY (Cash)", className="card-title"),
            html.H6(f"{cash_count}", className="card-subtitle"),
        ]
        no_of_loan_CCY_card = [
            html.H4("Number of CCY (Loans)", className="card-title"),
            html.H6(f"{loans_count}", className="card-subtitle"),
        ]
        total_cash_value_card = [
            html.H4("Total Cash", className="card-title"),
            html.H6("${:.3f}M".format(total_cash/1000000), className="card-subtitle"),
        ]
        total_loan_value_card = [
            html.H4("Total Loans", className="card-title"),
            html.H6("${:.3f}M".format(total_loans/1000000), className="card-subtitle"),
        ]
        card_custom_left1_value = total_cash_value_card
        card_custom_left2_value = total_loan_value_card
        card_custom_right1_value = no_of_cash_CCY_card
        card_custom_right2_value = no_of_loan_CCY_card
        selected_tab_chart = cash_loan_barchart
        selected_tab_table = cash_loan_table
    
    elif selected_tab == "EQUITIES" or selected_tab == "FIXED INCOME":
        client_equity_data = client_data[client_data["Asset Class"]==selected_tab]
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
        #latest_total_profit_loss =group_by_date_equity.loc[(group_by_date_equity["Position As of Date"]==latest_date),"Estimated Profit/Loss"]
        #latest_total_profit_loss = pd.to_numeric(latest_group_by_date_data.loc["Estimated Profit/Loss"])
        #latest_total_amount_paid = latest_group_by_date_data["Original Amount Paid"]
        latest_total_profit_loss = latest_group_by_date_data.at[0,'Estimated Profit/Loss']
        latest_total_return_percentage = latest_group_by_date_data.at[0,'% Profit/Loss']
        # print(latest_total_profit_loss)
        # print("${:.3f}M".format(latest_total_profit_loss/1000000))

        latest_data = client_equity_data[client_equity_data['Position As of Date'] == latest_date]
        equity_latest_table_df = latest_data[["Name","Estimated Profit/Loss","% Profit/Loss","Citi rating"]]
        
        equity_latest_table_df.sort_values("% Profit/Loss", inplace=True, ascending=True)
        # print(equity_latest_table_df)
        #buy_count = equity_latest_table_df[equity_latest_table_df["Citi rating"]=="buy"].count()
        buy_count = equity_latest_table_df[equity_latest_table_df["Citi rating"] == "buy"].count()[0]
        sell_count = equity_latest_table_df[equity_latest_table_df["Citi rating"] == "sell"].count()[0]
        # print(type(buy_count))
        # print(f"No. of buy: {buy_count}")


        equity_latest_table = go.Figure(data=[go.Table(
                    header=dict(values=["<b>Company Name</b>","<b>Profit/Loss</b>",
                                    "<b>% Profit/Loss</b>","<b>Citi rating</b>"],
                                fill_color='paleturquoise',
                                align='left'),
                    cells=dict(values=[equity_latest_table_df.Name, \
                    equity_latest_table_df["Estimated Profit/Loss"],
                    equity_latest_table_df["% Profit/Loss"],
                    equity_latest_table_df["Citi rating"]],
                            fill_color='lavender',
                            align='left'))
                ])

        no_of_buy_card = [
            html.H4("Number of Buy", className="card-title"),
            html.H5(f"{buy_count}", className="card-subtitle"),
        ]
        no_of_sell_card = [
            html.H4("Number of Sell", className="card-title"),
            html.H5(f"{sell_count}", className="card-subtitle"),
        ]
        total_profit_loss_card = [
            html.H4("Total Profit/Loss", className="card-title"),
            html.H5("${:.3f}M".format(latest_total_profit_loss/1000000), className="card-subtitle"),
        ]
        total_return_percentage_card = [
            html.H4("% Total Return", className="card-title"),
            html.H5("{:.3f}%".format(latest_total_return_percentage), className="card-subtitle"),
        ]
        card_custom_left1_value = total_profit_loss_card
        card_custom_left2_value = total_return_percentage_card
        card_custom_right1_value = no_of_buy_card
        card_custom_right2_value = no_of_sell_card
        selected_tab_chart = equity_daily_percentage_fig
        selected_tab_table = equity_latest_table
    
    # elif selected_tab == "FIXED INCOME":

    #     # Credit Rating Dictionaries
    #     SP_rating_dict = {
    #         "AAA" : "Prime",
    #         "AA+" : "High Grade",
    #         "AA" : "High Grade",
    #         "AA-" : "High Grade",
    #         "A+" : "Upper Medium Grade",
    #         "A" : "Upper Medium Grade",
    #         "A-" : "Upper Medium Grade",
    #         "BBB+" : "Lower Medium Grade",
    #         "BBB" : "Lower Medium Grade",
    #         "BBB-" : "Lower Medium Grade",
    #         "BB+" : "Non Investment Grade Speculative",
    #         "BB" : "Non Investment Grade Speculative",
    #         "BB-" : "Non Investment Grade Speculative",
    #         "B+" : "Highly Speculative",
    #         "B" : "Highly Speculative",
    #         "B-" : "Highly Speculative",
    #         "CCC+" : "Substantial Risks",
    #         "CCC" : "Extremely Speculative"
    #     }
    #     Moody_rating_dict = {
    #         "Aaa" : "Prime",
    #         "Aa1" : "High Grade",
    #         "Aa2" : "High Grade",
    #         "Aa3-" : "High Grade",
    #         "A1" : "Upper Medium Grade",
    #         "A2" : "Upper Medium Grade",
    #         "A3" : "Upper Medium Grade",
    #         "Baa1" : "Lower Medium Grade",
    #         "Baa2" : "Lower Medium Grade",
    #         "Baa3" : "Lower Medium Grade",
    #         "Ba1" : "Non Investment Grade Speculative",
    #         "Ba2" : "Non Investment Grade Speculative",
    #         "Ba3" : "Non Investment Grade Speculative",
    #         "B1" : "Highly Speculative",
    #         "B2" : "Highly Speculative",
    #         "B3" : "Highly Speculative",
    #         "Caa1" : "Substantial Risks",
    #         "Caa2" : "Extremely Speculative"
    #     }
    #     Fitch_rating_dict = SP_rating_dict

    #     client_fi_data = client_data[client_data["Asset Class"]==selected_tab]
    #     client_fi_data["Exchange Rate"] = client_fi_data["Nominal Amount (USD)"]/client_fi_data["Nominal Amount (CCY)"]
    #     client_fi_data["Original Amount Paid"] = client_fi_data["Nominal Units"]*client_fi_data["Average Cost"]*client_fi_data["Exchange Rate"]
    #     client_fi_data["Estimated Profit/Loss"] = client_fi_data["Nominal Amount (USD)"]-client_fi_data["Original Amount Paid"]
    #     client_fi_data["% Profit/Loss"] = client_fi_data["Estimated Profit/Loss"]*100/client_fi_data["Original Amount Paid"]

    #     group_by_date_fi = client_fi_data.groupby(['Position As of Date'])["Original Amount Paid", "Estimated Profit/Loss"].apply(lambda x : x.sum()).reset_index()

    #     group_by_date_fi["% Profit/Loss"] = group_by_date_fi["Estimated Profit/Loss"]*100/group_by_date_fi["Original Amount Paid"]

    #     fi_daily_percentage_fig = px.line(group_by_date_fi,x="Position As of Date", y="% Profit/Loss", 
    #                 text="Estimated Profit/Loss", title="Daily % Profit/Loss")
    #     fi_daily_percentage_fig.update_traces(
    #                 textposition="top center",
    #                 texttemplate = "%{text:.2s}")
                    
    #     rating_selection = ["S&P", "Moody's", "Fitch"]
    #     selected_rating = "S&P"
    #     excel_column_mapping = {
    #         "S&P": "S&P R",
    #         "Moody's": "Moodys R",
    #         "Fitch": "Fitch",
    #         }
    #     rating_dict_mapping = {
    #         "S&P": SP_rating_dict,
    #         "Moody's": Moody_rating_dict,
    #         "Fitch": Fitch_rating_dict,
    #         }
    #     risk_level_mapping = {
    #         "Prime":"Low Risk",
    #         "High Grade":"Low Risk",
    #         "Upper Medium Grade":"Medium Risk",
    #         "Lower Medium Grade":"Medium Risk",
    #         "Non Investment Grade Speculative":"High Risk",
    #         "Highly Speculative":"High Risk",
    #         "Substantial Risks":"High Risk",
    #         "Extremely Speculative":"High Risk"
    #     }
    #     selected_dict = rating_dict_mapping[selected_rating]
    #     selected_excel_col = excel_column_mapping[selected_rating]
        
    #     client_fi_data["Client Credit Rating"] = selected_dict[client_fi_data[selected_excel_col]]
    #     client_fi_data["Risk Level"] = risk_level_mapping[client_fi_data["Client Credit Rating"]]

    #     group_by_date_credit_rate = client_fi_data.groupby(['Position As of Date','Client Credit Rating']).size().reset_index(name='counts')

    #     latest_date = group_by_date_credit_rate["Position As of Date"].max()
    #     latest_group_by_date_data = group_by_date_credit_rate[group_by_date_credit_rate['Position As of Date'] == latest_date].reset_index(drop=True)

    #     latest_total_profit_loss = latest_group_by_date_data.at[0,'Estimated Profit/Loss']
    #     latest_total_return_percentage = latest_group_by_date_data.at[0,'% Profit/Loss']

    #     credit_rating_barchart = px.bar(latest_group_by_date_data, 
    #                             x='Client Credit Rating', y='counts', color='Client Credit Rating',
    #                             title = "Current Credit Rating Counts")

    #     latest_data = client_fi_data[client_fi_data['Position As of Date'] == latest_date]

    #     medium_risk_count = latest_data[latest_data["Risk Level"] == "Medium Risk"].count()[0]
    #     high_risk_count = latest_data[latest_data["Risk Level"] == "High Risk"].count()[0]

    #     fi_latest_table_df = latest_data[["Name","Estimated Profit/Loss","% Profit/Loss",
    #                         "Client Credit Rating","Maturity","Next Call Date"]]
        
    #     fi_latest_table_df.sort_values("% Profit/Loss", inplace=True, ascending=True)

    #     fi_latest_table = go.Figure(data=[go.Table(
    #                 header=dict(values=["<b>Company Name</b>","<b>Profit/Loss</b>",
    #                                 "<b>% Profit/Loss</b>","<b>Client Credit Rating</b>",
    #                                 "<b>Maturity</b>","<b>Next Call Date</b>"],
    #                             fill_color='paleturquoise',
    #                             align='left'),
    #                 cells=dict(values=[fi_latest_table_df.Name, 
    #                 fi_latest_table_df["Estimated Profit/Loss"],
    #                 fi_latest_table_df["% Profit/Loss"],
    #                 fi_latest_table_df["Client Credit Rating"],
    #                 fi_latest_table_df["Maturity"],
    #                 fi_latest_table_df["Next Call Date"],],
    #                         fill_color='lavender',
    #                         align='left'))
    #             ])

    #     no_of_medium_risks_card = [
    #         html.H4("Number of Medium Risks", className="card-title"),
    #         html.H5(f"{medium_risk_count}", className="card-subtitle"),
    #     ]
    #     no_of_high_risks_card = [
    #         html.H4("Number of High Risks", className="card-title"),
    #         html.H5(f"{high_risk_count}", className="card-subtitle"),
    #     ]
    #     total_profit_loss_card = [
    #         html.H4("Total Profit/Loss", className="card-title"),
    #         html.H5("${:.3f}M".format(latest_total_profit_loss/1000000), className="card-subtitle"),
    #     ]
    #     total_return_percentage_card = [
    #         html.H4("% Total Return", className="card-title"),
    #         html.H5("{:.3f}%".format(latest_total_return_percentage), className="card-subtitle"),
    #     ]
    #     card_custom_left1_value = total_profit_loss_card
    #     card_custom_left2_value = total_return_percentage_card
    #     card_custom_right1_value = no_of_medium_risks_card
    #     card_custom_right2_value = no_of_high_risks_card
    #     selected_tab_chart = credit_rating_barchart
    #     selected_tab_table = fi_latest_table  

    elif selected_tab == "ALTERNATIVE INVESTMENTS":
        client_ai_data = client_data[client_data["Asset Class"]==selected_tab]
        
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
        ai_latest_table_df = latest_data[["Asset Sub Class","Name","Commitment Amount","Contribution Amount","% Outstanding Amount","% Return on Contribution"]]
        
        ai_latest_table_df.sort_values("% Return on Contribution", inplace=True, ascending=True)
        negative_returns_count = np.sum((ai_latest_table_df["% Return on Contribution"] < 0).values.ravel())
        positive_returns_count = np.sum((ai_latest_table_df["% Return on Contribution"] > 0).values.ravel())
        # print(negative_returns_count)
        # print(positive_returns_count)
        ai_latest_table = go.Figure(data=[go.Table(
                    header=dict(values=["<b>Asset Sub Class</b>","<b>Company Name</b>",
                                    "<b>Commitment Amount</b>","<b>Contribution Amount</b>",
                                    "<b>% Outstanding Amount</b>","<b>% Return on Contribution</b>"],
                                fill_color='paleturquoise',
                                align='left'),
                    cells=dict(values=[ai_latest_table_df["Asset Sub Class"], 
                    ai_latest_table_df.Name, 
                    ai_latest_table_df["Commitment Amount"], 
                    ai_latest_table_df["Contribution Amount"], 
                    ai_latest_table_df["% Outstanding Amount"], 
                    ai_latest_table_df["% Return on Contribution"], ],
                            fill_color='lavender',
                            align='left'))
                ])

        no_of_positive_returns_card = [
            html.H4("Number of Positive Returns", className="card-title"),
            html.H5(f"{positive_returns_count}", className="card-subtitle"),
        ]
        no_of_negative_returns_card = [
            html.H4("Number of Negative Returns", className="card-title"),
            html.H5(f"{negative_returns_count}", className="card-subtitle"),
        ]
        total_distribution_card = [
            html.H4("Total Distribution Amount", className="card-title"),
            html.H5("${:.3f}M".format(latest_total_distribution_amount/1000000), className="card-subtitle"),
        ]
        total_return_contribution_card = [
            html.H4("% Total Return on Contribution", className="card-title"),
            html.H5("{:.3f}%".format(latest_total_return_contribution), className="card-subtitle"),
        ]
        card_custom_left1_value = total_distribution_card
        card_custom_left2_value = total_return_contribution_card
        card_custom_right1_value = no_of_positive_returns_card
        card_custom_right2_value = no_of_negative_returns_card
        selected_tab_chart = ai_daily_percentage_fig
        selected_tab_table = ai_latest_table

    else: # "CAPITAL MARKETS"
        client_cm_data = client_data[client_data["Asset Class"]==selected_tab]
        
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

        cm_latest_table = go.Figure(data=[go.Table(
                    header=dict(values=["<b>Asset Sub Class</b>","<b>Trade Number</b>",
                                    "<b>Nominal Amount (CCY)</b>","<b>Nominal Amount (USD)</b>"],
                                fill_color='paleturquoise',
                                align='left'),
                    cells=dict(values=[cm_latest_table_df["Asset Sub Class"], 
                    cm_latest_table_df["Trade Number"], 
                    cm_latest_table_df["Nominal Amount (CCY)"], 
                    cm_latest_table_df["Nominal Amount (USD)"]],
                            fill_color='lavender',
                            align='left'))
                ])

        no_of_positive_values_card = [
            html.H4("Number of Positive Trades", className="card-title"),
            html.H5(f"{positive_values_count}", className="card-subtitle"),
        ]
        no_of_negative_values_card = [
            html.H4("Number of Negative Trades", className="card-title"),
            html.H5(f"{negative_values_count}", className="card-subtitle"),
        ]
        total_nominal_amount_card = [
            html.H4("Total Nominal Amount (USD)", className="card-title"),
            html.H5("${:.3f}M".format(latest_total_nominal_amount/1000000), className="card-subtitle"),
        ]
        no_of_sub_assets_card = [
            html.H4("Number of Different Sub Assets", className="card-title"),
            html.H5(f"{no_of_asset_sub_class}", className="card-subtitle"),
        ]
        card_custom_left1_value = total_nominal_amount_card
        card_custom_left2_value = no_of_sub_assets_card
        card_custom_right1_value = no_of_positive_values_card
        card_custom_right2_value = no_of_negative_values_card
        selected_tab_chart = daily_cm_fig
        selected_tab_table = cm_latest_table

    return card_custom_left1_value, card_custom_left2_value,\
        card_custom_right1_value,card_custom_right2_value,\
        selected_tab_chart, selected_tab_table