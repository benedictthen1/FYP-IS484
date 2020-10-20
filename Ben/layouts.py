import dash
import dash_core_components as dcc
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

ticker = yf.Ticker("aaapl")
hist = ticker.history(period="1y",interval="1d")
print(len(hist))

#balance_sheet = si.get_quote_table("aapl")
# balance_sheet = si.get_data("aapl")
# print(balance_sheet)

#IMPORT DATA & DATA MANIPULATION
df = pd.read_csv('TestData.csv',encoding='latin1')
df =df[df['Asset Class'].notnull()]

numeric_cols = ['% Change from Avg Cost','YTD%', '1d %', '5d %', '1m % ', '6m %', '12m %'] + ['Nominal Amount (USD)','Nominal Units','Nominal Amount (CCY)','Current Price','Closing Price', 'Average Cost']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col].astype("float")
    df[col] = df[col].round(2)
#print(df.columns)

#DASH APP
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

fig = go.Figure()
# fig.update_xaxes(showline=True, linewidth=1, linecolor='Grey', gridcolor='Grey')
# fig.update_yaxes(showline=False, linewidth=1, linecolor='Grey', gridcolor='Grey')

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

client_coy_table = html.Div([
    dash_table.DataTable(
        id='client_coy_table',
        sort_action='native',
        style_cell={'textAlign': 'center','textOverflow': 'ellipsis','font_size': '11px',},
        style_as_list_view=True,
        fixed_rows={'headers': True},
        style_table={'overflowY': 'auto','height': '345px',"width": '380px'},
        style_data={'maxWidth': '70px','minWidth': '70px'},
        style_header={'fontWeight': 'bold', 'height': 'auto','whiteSpace': 'normal','border': '1px solid grey'},
        #columns=[{"name": i, "id": i} for i in client_table.columns],
        #data=client_table.to_dict('records')
    )
])


app.layout = html.Div([

    html.Div([
    dcc.Input(id="input", type="text", placeholder="search ticker"),
    dbc.Button("Apply", color="dark",size="sm", id="search-button",n_clicks=0, className="mr-1"),
    ],className="search_style"),
    html.P(id = "price_date"),
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

            dbc.Button("1D", color="dark",size="sm", id="1d-button",n_clicks=0, className="mr-1"),
            dbc.Button("5D", color="dark",size="sm", id="5d-button",n_clicks=0, className="mr-1"),
            dbc.Button("1M", color="dark",size="sm", id="1m-button",n_clicks=0, className="mr-1"),
            dbc.Button("6M", color="dark",size="sm", id="6m-button",n_clicks=0, className="mr-1"),
            dbc.Button("1Y", color="dark",size="sm", id="1y-button",n_clicks=0, className="mr-1"),

            dcc.Graph(figure=fig, id="candle"),

        ],className="mini_container"),
    ], className="container-display"),

    #FINANCIAL BAR CHARTS [BOTTOM]
    html.Div([
        dcc.Graph(id="income_chart"),
    ],className="fin_bar_group"),
    html.Div([
        dcc.Graph(id="balance_chart"),
    ],className="fin_bar_group"),
    html.Div([
        dcc.Graph(id="cashflow_bar"),
    ],className="fin_bar_group")
])

##### CALLBACKS ######

#Metrics Banners
@app.callback([Output("ytd", "children"),Output("1d", "children"),Output("5d", "children"),Output("1m", "children"),
               Output("6m", "children"),Output("12m", "children")],
              [Input("search-button","n_clicks")],[State("input","value")])
def banner(search_btn,search):
    if search_btn:
        tdf = yf.Ticker(search)
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
            [Input("search-button","n_clicks")],[State("input","value")])
def coy_client_Table(search_btn,search):
    data = df
    if search_btn:
        #search = search.str.upper
        data = df
        data=df[df["Ticker"]==search]
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
    client_table = client_table[["Client Name","Nominal Amount (CCY)","Profit/Loss","Profit/Loss %"]]
    
    data =client_table.to_dict('records')
    columns=([{'name': i, 'id': i} for i in client_table.columns])

    return data,columns
    
    

#Cashflorw bar chart
@app.callback(Output("cashflow_bar", "figure"),
            [Input("search-button","n_clicks")],[State("input","value")])
def bar_chart_input(search_btn,search):
    if search_btn:
        cashflow = si.get_cash_flow(search)
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
    #fig4.update_xaxes(showline=False,zeroline=True,linewidth=1, linecolor='Black',tickfont=dict(size=10))
    return fig4

#balance sheet bar
@app.callback(Output("balance_chart", "figure"),
            [Input("search-button","n_clicks")],[State("input","value")])
def bs_chart_input(search_btn,search):
    if search_btn:
        balance_sheet = si.get_balance_sheet(search)
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
            [Input("search-button","n_clicks")],[State("input","value")])
def income_bar(search_btn,search):
    if search_btn:
        balance_sheet = si.get_income_statement(search)
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
    color[netincome<0]='red'
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

# Stats stock table
@app.callback([Output("stats_table", "columns"),Output("stats_table", "data"),Output("coy_desc","children")],
            [Input("search-button","n_clicks")],[State("input","value")])
def stats_table_input(search_btn,search):
    if search_btn:
        ndf = yf.Ticker(search)
        #print(ndf.info)
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


@app.callback([Output("candle","figure"),Output("coy_name","children"),Output("close_price","children"),Output("price_diff","children"),Output("price_date","children")],
              [Input("search-button","n_clicks"),Input("1d-button","n_clicks"),Input("5d-button","n_clicks"),Input("1m-button","n_clicks")],
              [State("input","value")])
def click(search_click,d1,d5,m1,search_input):
    
    if search_input:
        ndf= yf.Ticker(search_input)
        df = ndf.history(interval="1m",period="1d")
    else:
        ndf= yf.Ticker('aapl')
        df = ndf.history(interval="1m",period="1d")

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
    # Config graph layout
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


    fig = go.Figure(data=data, layout=layout)
    fig.update_xaxes(linewidth=0.5, linecolor='Grey', gridcolor='#D3D3D3')
    fig.update_layout(
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
    
    return fig, coy_name, close_price, price_diff,price_date


if __name__ == '__main__':
    app.run_server(debug=True)