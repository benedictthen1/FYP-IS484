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

##### Excel Formulas #####
# Nominal Amount (USD) = Nominal Units*Current Price (or) 
# Nominal Amount (USD) = Nominal Units*Closing Price
# % Change from Avg Cost = ((Current Price-Average Cost)/Average Cost)*100 (or) 
# % Change from Avg Cost = ((Closing Price-Average Cost)/Average Cost)*100

# Estimated Original Amount Paid = Nominal Units*Average Cost
# Estimated Profit/Loss = Nominal Amount (USD) - (Nominal Units*Average Cost)
# % Profit/Loss Return = ((Estimated Profit/Loss) / Estimated Original Amount Paid)*100

# % Outstanding Amount = Outstanding Amount*100/Commitment Amount 
# % Return on Contribution = ((Distribution Amount/Contribution Amount)-1)*100
###########################

df = pd.read_csv('../TestDataManipulatedAllCols.csv')

### Change Date Format ###
df['Position As of Date']= pd.to_datetime(df['Position As of Date']) 
df['Position As of Date'] = df['Position As of Date'].apply(lambda x: dt.datetime.strftime(x, '%Y-%d-%m'))
df['Position As of Date']= pd.to_datetime(df['Position As of Date']) 

### Limit decimal places of all numeric columns in df ###
numeric_cols = df.select_dtypes([np.number]).columns.to_list()
decimals = 3
df[numeric_cols] = df[numeric_cols].apply(lambda x: round(x, decimals))

### Get all client names ###
client_names = df["Client Name"].unique()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Total Assets Value Card (This card is under Part 1, refer to app layout)
card_assets = dbc.Card(
    [
        dbc.CardBody(id='card_assets_value',
        ),
    ],inverse=True,outline=False, color="success",
)

# Total Liability Value Card (This card is under Part 1, refer to app layout)
card_liab = dbc.Card(
    [
        dbc.CardBody(id='card_liab_value',
        ),
    ],inverse=True,outline=False, color="danger",
)

# There will be 4 cards under Part 4, refer to app layout.
# 2 Left cards and 2 Right cards
# Custom Card Left 1
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

### The whole app layout ###
# There are 4 main parts on this app. #
# Part 1: Main Selection (This area might be replaced with your output. The selection here will affect the entire app.)
# Part 1 Content: Client's Name dropdown and Base Number multi-selections
# Part 2: Overall Performance & Pie Chart Breakdown
# Part 2 Content: 2 cards (Total Assets, Total Liab),
#                 Total Assets & Liab Timeseries chart, Asset Breakdown Piechart
# Part 3: Asset Type Selection (Same as choosing different tabs in Excel) 
# Part 3 Content: Asset Type Dropdown (Dropdown options here depends on your selections in Part 1)
# Part 4: Custom Section (This section will change accordingly based on selections in Part 1 and Part 3 
#                         but the layout of this section is the same across all options)
# Part 4 Content: 4 cards (2 Left Cards, 2 Right Card),
#                 1 chart (on the left), 1 table (on the right)

app.layout = html.Div([
    ### Part 1: Main Selection ###
    dbc.Row([
            dbc.Col([
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
                    width={'size':9},
                    ), 
            ]),

    html.Br(),

    ### Part 2: Overall Performance & Pie Chart Breakdown ###
    dbc.Row([
            dbc.Col(card_assets, width=3),
            dbc.Col(card_liab, width=3)
            ], justify="start"), # justify="start", "center", "end", "between", "around"
    dbc.Row([
            dbc.Col([dcc.Graph(id='asset_liab_timeseries')], width={'size':7},),
            dbc.Col([dcc.Graph(id='asset_class_piechart')], width={'size':5},),
            ]),

    ### Part 3: Asset Type Selection ###
    dbc.Row([
            dbc.Col([
                        html.H3("Choose Asset Type:"),
                        dcc.Dropdown(
                        id='client_asset_type_dropdown',
                        )
                    ],
                    width={'size':3},
                    ),
            ]),

    html.Br(),

    ### Part 4: Custom Section ###
    dbc.Row([
            dbc.Col(card_custom_left1, width=3),
            dbc.Col(card_custom_left2, width=3),
            dbc.Col(card_custom_right1, width=3),
            dbc.Col(card_custom_right2, width=3)
            ], justify="start"),
    dbc.Row([
            dbc.Col([dcc.Graph(id='selected_tab_chart')],
                    width={'size':6},
                    ),
            dbc.Col([dcc.Graph(id='selected_tab_table')],
                    width={'size':6},
                    ),
            ]),      
    ])

### Callback for Part 1: "Client's Base Numbers" multi-select section ###
# This callback will return the multi-select options and pre-select all base numbers based on selected client name. #
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

### Callback for Part 2: Overall Performance & Pie Chart Breakdown ###
# This callback will return the dropdown options and pre-selected value based on selected base numbers. #
@app.callback(
    [Output('card_assets_value','children'),
    Output('card_liab_value','children'),
    Output('asset_liab_timeseries','figure'),
    Output('asset_class_piechart','figure')],
    [Input('base_numbers_checklist', 'value')]
) 
def overall_section(selected_base_numbers):
    client_data = df[df["Base Number"].isin(selected_base_numbers)]
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

### Callback for Part 3: Asset Type Selection ("Choose Asset Type" dropdown) ###
# This callback will return the dropdown options and pre-selected value based on selected base numbers. #
@app.callback(
    [Output('client_asset_type_dropdown','options'),
    Output('client_asset_type_dropdown','value')],
    [Input('base_numbers_checklist', 'value')]
) 
def set_asset_class_dropdown(selected_base_numbers):
    client_data = df[df["Base Number"].isin(selected_base_numbers)]
    asset_classes = list(client_data["Asset Class"].unique())
    
    excel_tabs = ["EQUITIES","FIXED INCOME","ALTERNATIVE INVESTMENTS","CAPITAL MARKETS"]
    asset_dropdown_options_list = ["CASH & LIABILITIES"]
    for tab in excel_tabs:
        if tab in asset_classes:
            asset_dropdown_options_list.append(tab)
    
    asset_dropdown_options = [{'label': tab_option, 'value': tab_option} for tab_option in asset_dropdown_options_list]
    
    return asset_dropdown_options, asset_dropdown_options_list[0]

### Callback for Part 4: Custom Section (the whole section under "Choose Asset Type" dropdown) ###
# This whole area will change according to what's selected in Part 3 and Part 1. # 
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
    client_data = df[df["Base Number"].isin(selected_base_numbers)]
    
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
        print(df_merged)
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


if __name__ == '__main__':
    app.run_server(debug=True)