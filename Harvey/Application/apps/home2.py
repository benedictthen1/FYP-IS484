import dash 
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import plotly.express as px
import pandas as pd
import numpy as np
import pathlib
from app import app
import datetime as dt
import dash_table
import calendar
import plotly.graph_objs as go

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

tdf = pd.read_csv(DATA_PATH.joinpath("TestData.csv"),encoding='latin1')
numeric_cols = ['% Change from Avg Cost','YTD%', '1d %', '5d %', '1m % ', '6m %', '12m %'] + ['Nominal Amount (USD)','Nominal Units','Nominal Amount (CCY)','Current Price','Closing Price', 'Average Cost']
for col in numeric_cols:
    tdf[col] = pd.to_numeric(tdf[col], errors="coerce")
    tdf[col].astype("float")
    tdf[col] = tdf[col].round(2)

#Reminder Dataset
rdf = pd.read_csv(DATA_PATH.joinpath("Client.csv"),encoding='latin1')
rdf = rdf[["Name","Asset Class", "Dividend EX Date","Maturity","Next Call Date"]]
rdf = rdf[rdf["Asset Class"].isin(["FIXED INCOME","EQUITIES"])]
rdf = rdf.melt(id_vars=["Name", "Asset Class"], 
               var_name="Reminder Type", 
               value_vars=["Dividend EX Date","Maturity","Next Call Date"],
            value_name="Date")

rdf['Date'].replace(' ', np.nan, inplace=True)
rdf.dropna(subset = ["Date"], inplace=True)
rdf = rdf.drop_duplicates()
rdf['Date'] = pd.to_datetime(rdf['Date'], format='%d/%m/%Y') 
today = dt.datetime.today().strftime('%d/%m/%Y') 
today = pd.to_datetime(today,format='%d/%m/%Y')
rdf["Days Left"] = rdf["Date"] - today
rdf = rdf[rdf["Days Left"]>= dt.timedelta(days=1)]
rdf = rdf.sort_values(by='Days Left')
rdf["Date"] = rdf['Date'].dt.date
rdf["Days Left"] = rdf["Days Left"].dt.days.astype('int16')
#print(rdf[rdf["Reminder Type"] == "Next Call Date"])

#client in company (reminder)
rdf2 = pd.read_csv(DATA_PATH.joinpath("Client.csv"),encoding='latin1')
rdf2 = rdf2[rdf2["Asset Class"].isin(["FIXED INCOME","EQUITIES"])]
rdf2 = rdf2[["Position As of Date","Client Name", "Name", "Nominal Units", "Nominal Amount (CCY)","Nominal Amount (USD)","Estimated Profit/Loss","% Profit/Loss Return"]]

client_perf_bar=px.bar()
coy_perf_bar=px.bar()

remind_table = html.Div([
    dash_table.DataTable(
        id='remind_table',
        sort_action='native',
        style_cell={'textAlign': 'center','textOverflow': 'ellipsis','border': '1px solid black','font_size': '10px','padding': '5px'},
        #style_data_conditional=styles2,
        style_as_list_view=True,
        fixed_rows={'headers': True},
        style_table={'overflowY': 'auto','height': '202px','border': 'thin lightgrey solid'},
        style_header={'fontWeight': 'bold', 'height': 'auto','whiteSpace': 'normal','border': '1px solid grey','backgroundColor':'#f2f2f2'},
        style_data={'minWidth': '120px','maxWidth': '120px'},
        columns=[{"name": i, "id": i} for i in rdf.columns],
        data=rdf.to_dict('records'),
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in rdf.to_dict('rows')
        ],
    )
])

client_remind_table = html.Div([
    dash_table.DataTable(
        id='c_remind_table',
        sort_action='native',
        style_cell={'textAlign': 'center','textOverflow': 'ellipsis','border': '1px solid black','font_size': '10px','padding': '5px'},
        #style_data_conditional=styles2,
        style_as_list_view=True,
        fixed_rows={'headers': True},
        style_table={'overflowY': 'auto','height': '217px','border': 'thin lightgrey solid'},
        style_header={'fontWeight': 'bold', 'height': 'auto','whiteSpace': 'normal','border': '1px solid grey'},
        style_data={'minWidth': '90px','maxWidth': '90px'},
        columns=[{"name": i, "id": i} for i in rdf2.columns],
        data=rdf2.to_dict('records'),
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in rdf2.to_dict('rows')
        ],
    )
])

#cal remind table
cal_coy_remind_table = html.Div([
    dash_table.DataTable(
        id='cal_coy_remind_table',
        sort_action='native',
        style_cell={'textAlign': 'center','textOverflow': 'ellipsis','border': '1px solid black','font_size': '10px','padding': '5px'},
        #style_data_conditional=styles2,
        style_as_list_view=True,
        fixed_rows={'headers': True},
        style_table={'overflowY': 'auto','height': '217px',"width":"850px"},
        style_header={'fontWeight': 'bold', 'height': 'auto','whiteSpace': 'normal','border': '1px solid grey'},
        style_data={'minWidth': '90px','maxWidth': '90px'},
        columns=[{"name": i, "id": i} for i in rdf.columns],
        data=rdf.to_dict('records'),
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in rdf.to_dict('rows')
        ],
    )
])


#RISK CLIENT DATASET 
hrisk_df = pd.read_csv(DATA_PATH.joinpath("Client.csv"),encoding='latin1')
rlv_df = pd.read_csv(DATA_PATH.joinpath("RiskLevelsAllocation.csv"),encoding='latin1')

hrisk_df['Position As of Date']= pd.to_datetime(hrisk_df['Position As of Date']) 

latest_date = hrisk_df["Position As of Date"].max()
latest_client_data = hrisk_df[hrisk_df['Position As of Date'] == latest_date]

latest_client_data["Asset Class"].replace({"Investment Cash & Short Term Investments": "CASH"}, inplace=True)
risk_asset_classes = ["CASH", "FIXED INCOME", "EQUITIES"]
risk_analysis_df = latest_client_data[latest_client_data["Asset Class"].isin(risk_asset_classes)]

group_by_risk_asset_class = risk_analysis_df\
.groupby(['Client Name','Asset Class'], as_index=True)\
.agg({'Nominal Amount (USD)':'sum'})
group_by_risk_asset_class["%"] = group_by_risk_asset_class.groupby(level=0).apply(lambda x:  100*x / x.sum())
group_by_risk_asset_class = group_by_risk_asset_class.reset_index()

transformed_risk_analysis_df = \
    group_by_risk_asset_class.pivot(index='Client Name', columns='Asset Class', values='%')\
    .fillna(0)

stacked_risk_analysis_df = transformed_risk_analysis_df.stack().reset_index()
# rename last column
stacked_risk_analysis_df.set_axis([*stacked_risk_analysis_df.columns[:-1], 'Current Nominal Amount (%)'], axis=1, inplace=True)

client_target_risk_df = latest_client_data[["Client Name","Target Risk Level"]]
client_target_risk_df = client_target_risk_df.drop_duplicates()

stacked_risk_analysis_df = stacked_risk_analysis_df[stacked_risk_analysis_df["Asset Class"] == "EQUITIES"]
risk_analysis_df = pd.merge(stacked_risk_analysis_df,client_target_risk_df,on="Client Name")

hrisk_df = rlv_df[rlv_df["Asset Class"]=="EQUITIES"]
#print(hrisk_df)

risk_analysis_df["Current Risk Level"] = risk_analysis_df['Current Nominal Amount (%)'].apply(lambda x: hrisk_df.iloc[(hrisk_df['Breakdown by Percentage']-x).abs().argsort()[:1]]['Level'].iloc[0])

risk_analysis_df['Target Status'] = np.where(risk_analysis_df['Target Risk Level']==risk_analysis_df['Current Risk Level'], 'In Target', 'Out of Target')

risk_analysis_df['Count'] = 1


risk_levels = ["All Levels",1,2,3,4,5]



#CALENDER 
year = dt.datetime.now().year
month = dt.datetime.now().month

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return dt.date(year, month, day)

d1 = dt.date(year, month, 1)
d2 = add_months(d1,3) - dt.timedelta(1)
delta = d2 - d1

dates_in_year = [d1 + dt.timedelta(i) for i in range(delta.days+1)] #gives me a list with datetimes for each day a year
weekdays_in_year = [i.weekday() for i in dates_in_year] #gives [0,1,2,3,4,5,6,0,1,2,3,4,5,6,…] (ticktext in xaxis dict translates this to weekdays
weeknumber_of_dates = [i.strftime("%b-W%V") for i in dates_in_year] #gives [1,1,1,1,1,1,1,2,2,2,2,2,2,2,…] name is self-explanatory
z = np.random.randint(4, size=(len(dates_in_year)))
z[0:15] = 0
z[40:54] = 0
z[70:88] = 0

text = [str(i) for i in dates_in_year] 
text[10] = str(dates_in_year[10]) + "<br> Maturity: MSFT <br> Next Call: STARBUCKS CORP"
colorscale=[[0.00, "#eeeeee"], [0.5, "#191970"], [0.75, "red"], [1, "#3CB371"]]

cal_data = [go.Heatmap(x = weeknumber_of_dates, y = weekdays_in_year, z = z, text=text, hoverinfo="text",
    xgap=12, ygap=5, showscale=False, colorscale=colorscale)]

cal_layout = go.Layout(
    height=186.5,
    yaxis=dict(
        showline = False, showgrid = False, zeroline = False,
        tickmode="array", ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], tickvals=[0,1,2,3,4,5,6]),
    xaxis=dict(showline = False, showgrid = False, zeroline = False,),
    font={"size":8, "color":"black"}, plot_bgcolor=("#f9f9f9"), margin = dict(t=40),
)

cal_fig = go.Figure(data=cal_data, layout=cal_layout)
cal_fig.update_layout(margin=dict(l=60, r=40, t=40, b=0, pad=5),paper_bgcolor="#f9f9f9",
                      title={'text': "Reminders for Next 3 months",'y':0.95,'x':0.5,'xanchor': 'center','yanchor': 'top'})
cal_fig.update_xaxes(side="top")

layout = html.Div([

    dcc.Location(id='url2', refresh=True),
    dcc.Location(id='url3', refresh=True),

    # Top Banners Metrics
    html.Div([
        html.Div([html.H3(["120"],className="ban_values"),html.P(["Total Clients"],className="ban_title")],className="client_metrics"),
        html.Div([html.H3(["31"],className="ban_values"),html.P(["Losing Clients"],className="ban_title")],className="client_metrics"),
        html.Div([html.H3(["89"],className="ban_values"),html.P(["Profiting Clients"],className="ban_title")],className="client_metrics"),
        html.Div([html.H3(["23"],className="ban_values"),html.P(["Client to remind"],className="ban_title")],className="client_metrics"),
        html.Div([html.H3(["16"],className="ban_values"),html.P(["Risky Clients"],className="ban_title")],className="client_metrics"),
    ],id="banner_group"),

    dbc.Row([
        dbc.Col([
        html.H5(["Performance Breakdown"],className="perf_bread_title"),
        html.Div([
            dbc.Tabs([

                dbc.Tab(label="Client", tab_id="tab-1", children=html.Div(children = [
                    dcc.Dropdown(
                        id='client_perf_dropdown',
                        options=[
                            {'label': 'Top Performance', 'value': 'top'},
                            {'label': 'Bottom Performance', 'value': 'bottom'},
                            {'label': 'All', 'value': 'all'}
                        ],value='top', style=dict(width='55%')
                    ),
                    
                    dcc.Loading(html.Div([dcc.Graph(id="client_bar-graph",figure=client_perf_bar)],className="perfbar_table")),
                ])),

                dbc.Tab(label="Company", tab_id="tab-2", children=html.Div(children = [

                    html.Div([
                    dcc.Dropdown(
                        id='coy_perf_dropdown',
                        options=[
                            {'label': 'Top Performance', 'value': 'top'},
                            {'label': 'Bottom Performance', 'value': 'bottom'},
                            {'label': 'All', 'value': 'all'}
                        ],value='top', style=dict(width="55%")
                    ),

                    dcc.Dropdown(
                        id='coy_time_dropdown',
                        options=[
                            {'label': '1D %', 'value': '1d %'},
                            {'label': '5D %', 'value': '5d %'},
                            {'label': '1M %', 'value': '1m % '},
                            {'label': '6M %', 'value': '6m %'},
                            {'label': '12M %', 'value': '12m %'},
                            {'label': 'YTD', 'value': 'YTD%'}
                        ],value='1d %', style=dict(width='40%')
                    ),
                    ],id="combine_coy_dropdown"),

                     dcc.Loading(html.Div([dcc.Graph(id="coy_bar-graph",figure=coy_perf_bar)],className="perfbar_table")),
                ])),
            #dcc.Graph(id='pie2', figure={}),
            ],id="tabs", active_tab="tab-1",), #tabs
        ],id="connectgraph"),
        ],width=4),

        dbc.Col([
            html.H5(["Reminders"],className="perf_bread_title"),
        html.Div([
            
            html.Div([
                dbc.Tabs([
                    dbc.Tab(label="Table View", tab_id="tab-1", children=html.Div(children = [
                        dcc.Dropdown(
                            id='remind_dropdown',
                            options = [{'label': i, 'value': i} for i in rdf["Reminder Type"].unique()],
                            placeholder="Filter by Reminder Type",
                            style={'width':'42%'},
                        ),
                    
                        dbc.Row([
                            dbc.Col([
                                html.Div([html.H5(["10"],className="remind_ban_values"),html.P(["Upcoming reminders (3mth)"],className="remind_ban_title")],className="remind_metrics"),
                                html.Div([html.H5(["4"],className="remind_ban_values"),html.P(["Upcoming Dividens Dates"],className="remind_ban_title")],className="remind_metrics"),
                                html.Div([html.H5(["5"],className="remind_ban_values"),html.P(["Upcoming Issue Dates"],className="remind_ban_title")],className="remind_metrics"),
                                html.Div([html.H5(["8"],className="remind_ban_values"),html.P(["Upcoming Next Call Dates"],className="remind_ban_title")],className="remind_metrics"),
                        ],width=3),

                            dbc.Col([
                                 dcc.Loading(remind_table),
                            ],width=9)
                        ],justify="center"),

                        dbc.Collapse([
                            html.Div([
                                dbc.Button("Close", color="primary", id="left", className="mr-1"),
                                html.H6(["Clients that have invested in this company:"],id="client_invest_title"),
                            ],id="clients_coy_btn_combine"),
                            html.Div([client_remind_table],id="client_remind_cover"),
                        ],id="remind-collapse"),
      
                ])),

                dbc.Tab(label="Calendar View", tab_id="tab-2", children=html.Div(children = [
                    dcc.Loading(dcc.Graph(id="cal_heatmap", figure=cal_fig, config={"displayModeBar": False})),
                    html.Div([
                        dbc.Badge("Next Call", color="success", id="remind_btn1"),
                        dbc.Badge("Dividen", color="danger", id="remind_btn2"),
                        dbc.Badge("Maturity", color="info", id="remind_btn3"),
                    ],id="remind_btn_grp"),

                    dbc.Collapse([
                        dbc.Button("Close", color="primary", id="left2", className="mr-1"),
                        html.Div([cal_coy_remind_table],id="client_remind_cover"),
                    ],id="cal-collapse"),

                ])),

                ],id="tabs2", active_tab="tab-1",), #end of tabs
            ],id="top_right_table"),

            html.H5(["Risk Profiling"],className="perf_bread_title"),
            html.Div([
                html.Div([
                dbc.Row([
                    dbc.Col([
                    dcc.Graph(id='current_risk_piechart', figure = px.pie(risk_analysis_df, values='Count', names='Current Risk Level',
                        width=215, height=245,color_discrete_sequence=px.colors.sequential.RdBu, hole=.5
                        ).update_traces(textposition='inside', textinfo='percent+label').update_layout(title={'text': "Risk Profile Breakdown",'y':0.95,'x':0.5,
                        'xanchor': 'center','yanchor': 'top'},legend_title="Level",
                        font=dict(size=9), margin=dict(l=21, r=21, t=5, b=5),paper_bgcolor='#f9f9f9',plot_bgcolor='#f9f9f9',
                        legend=dict(orientation="h",yanchor="bottom",y=0.01,xanchor="right",x=1))),
                    ],width=3),

                    dbc.Col([
                    dcc.Graph(id='target_status_piechart',
                    figure = px.pie(risk_analysis_df, values='Count', names='Target Status', hole=.5,
                        width=215, height=245,color_discrete_sequence=px.colors.sequential.RdBu
                        ).update_traces(textposition='inside', textinfo='percent').update_layout(
                        title={'text': "Target Status Breakdown",'y':0.95,'x':0.5,
                        'xanchor': 'center','yanchor': 'top'},
                        font=dict(size=9), margin=dict(l=21, r=21, t=5, b=5),paper_bgcolor='#f9f9f9',plot_bgcolor='#f9f9f9',
                        legend=dict(orientation="h",yanchor="bottom",y=0.01,xanchor="right",x=1,font=dict(size=7)))),
                    ],width=3),

                    dbc.Col([
                    html.Div([
                    dcc.Dropdown(
                        id='target_risk_filter',
                        options=[{'label': level_num, 'value': level_num} for level_num in risk_levels],
                        placeholder="Filter by Target Risk Level",
                        clearable=True),
                    dcc.Loading(

                    dash_table.DataTable(
                        id='risk_target_status_table',
                        columns = [{"name": i, "id": i} for i in risk_analysis_df[["Client Name","Current Risk Level","Target Risk Level"]].columns],
                        style_as_list_view=True,
                        fixed_rows={'headers': True},
                        style_table={'overflowY': 'auto','height': '180px','border': 'thin lightgrey solid'},
                        style_header={'fontWeight': 'bold', 'height': 'auto','whiteSpace': 'normal','border': '1px solid grey','backgroundColor':'#f2f2f2','fontWeight':'bold'},
                        style_data={'minWidth': '80px','maxWidth': '80px'},
                        style_cell={'textAlign':'center','border': '1px solid black','font_size': '10px','padding': '5px'},
                        sort_action='native',
                    ))
                ],id="risk_table")
                ],width=6),
                ],justify="center"),
                ],id="risk_pie_combine"),

            ],id="btn_right_table")

        ],id="testtableright")
        ],width=7)

    ],justify="center",style={'marginLeft': "-3%", 'marginRight': "-3%"}),
])


#CALLBACKSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
@app.callback(
    Output("cal-collapse", "is_open"),
    [Input("cal_heatmap","clickData"),Input("left2", "n_clicks")],
    [State("cal-collapse", "is_open")],
)
def toggle_left(d1, left2,is_open):
    if d1:
        return not is_open
    
    if left2: 
        return not is_open
    return is_open

@app.callback(
    Output("cal_coy_remind_table", "data"),Input("cal_heatmap","clickData"))
def client_coy_remind_table_link(data):
    if data:
        data = data["points"][0]["text"]
        split = data.split(":")
        temp_hold = []
        for i in split:
            split2 = i.split("<br>")
            for a in split2: 
                if a.isupper():
                    temp_hold.append(a.strip())
        
        data = rdf[rdf["Name"].isin(temp_hold)]
        f_final = data.to_dict('record')
 
        return f_final

@app.callback(
    Output("remind-collapse", "is_open"),
    [Input("remind_table","selected_cells"),Input("remind_table", "n_clicks"),Input("left", "n_clicks")],
    [State("remind-collapse", "is_open")],
)
def toggle_left2(d1, d2, btn, is_open):
    if d1:
        return not is_open

    if btn: 
        return not is_open
    return is_open

@app.callback(
    Output("c_remind_table", "data"),
    [Input("remind_table","selected_cells"),Input("remind_table","derived_virtual_data")])
def client_remind_table_link(t1, t2):
    if t1:
        row_num = t1[0]["row"]
        col_name = t2[row_num]["Name"]
        data = rdf2[rdf2["Name"]==col_name]
    else:
        data = rdf2.head(1)

    f_data = data.sort_values('Position As of Date').groupby(['Client Name','Name']).tail(1)
    f_final = f_data.to_dict('record')
    return f_final

@app.callback(Output('url2', 'pathname'),
              [Input('coy_bar-graph', 'clickData')])
def change_coy_link(data):
    if data:
        pathname = '/apps/stocks' 
        return pathname

@app.callback(Output('url3', 'pathname'),
              [Input('client_bar-graph', 'clickData')])
def change_client_link(data):
    if data:
        pathname = '/apps/client' 
        return pathname

@app.callback(Output('coy_session', 'data'),
             [Input('coy_bar-graph', 'clickData')])
def coy_store(data):
    if data:
        #print(data)
        clk = data['points'][0]['customdata'][0]
        #print(clk)
        return {'test': clk}

@app.callback(Output('client_session', 'data'),
             [Input('client_bar-graph', 'clickData')])
def client_store(data):
    if data:
        clk = data['points'][0]['hovertext']
        return {'test': clk}

@app.callback(Output("client_bar-graph", "figure"),
            [Input("client_perf_dropdown","value")])
def client_perf_value(value):
    data = tdf[tdf["Asset Class"].isin(["EQUITIES","ALTERNATIVE INVESTMENTS","FIXED INCOME"])]
    data["Profit/Loss"] = (data["Current Price"] - data["Average Cost"]) * data["Nominal Units"]
    client_table = data.groupby(["Client Name"])[["Profit/Loss","Nominal Amount (CCY)"]].sum().reset_index()
    client_table["Profit/Loss"] = client_table["Profit/Loss"].round(2)
    client_table["Nominal Amount (CCY)"] = client_table["Nominal Amount (CCY)"].round(2)
    client_table["Profit/Loss %"] = client_table["Profit/Loss"]/client_table["Nominal Amount (CCY)"]*100
    client_table["Profit/Loss %"] = client_table["Profit/Loss %"].round(1)
    client_table["Nominal Amount"] = client_table["Nominal Amount (CCY)"]
    client_table = client_table[["Client Name","Nominal Amount","Profit/Loss","Profit/Loss %"]].sort_values("Profit/Loss %")
    
    
    client_table['Nominal Amount']= client_table['Nominal Amount'].apply(lambda x : "{:,}".format(x))

    if value == "top":
        client_table = client_table[client_table["Profit/Loss"] > 0]
        client_table['Profit/Loss'] = client_table['Profit/Loss'].apply(lambda x : "{:,}".format(x))
        client_perf_bar = px.bar(client_table, x="Profit/Loss %", y="Client Name",orientation= "h", hover_name="Client Name", text='Profit/Loss %',
            hover_data={"Client Name": False,"Profit/Loss": True,"Nominal Amount": True},)
        client_perf_bar.update_traces(texttemplate='%{text:.2s}%', textposition='auto', textfont_size=10, marker_color="green")
        client_perf_bar.update_layout(height=470, font=dict(size=10,),
                            margin=dict(l=2, r=5, t=5, b=15, pad=10),paper_bgcolor='#f9f9f9',plot_bgcolor='#f9f9f9')
        return client_perf_bar
    elif value == "bottom":
        client_table = client_table[client_table["Profit/Loss"] < 0]
        client_table['Profit/Loss'] = client_table['Profit/Loss'].apply(lambda x : "{:,}".format(x))
        client_table["Profit/Loss %"] = client_table["Profit/Loss %"]*-1
        client_table = client_table.sort_values("Profit/Loss %",ascending=True)
        client_perf_bar = px.bar(client_table, x="Profit/Loss %", y="Client Name",orientation= "h", hover_name="Client Name", text='Profit/Loss %',
            hover_data={"Client Name": False,"Profit/Loss": True,"Nominal Amount": True},)
        client_perf_bar.update_traces(texttemplate='-%{text:.2s}%', textposition='auto',textfont_size=10, marker_color="crimson")
        client_perf_bar.update_layout(height=475,font=dict(size=10,),
                            margin=dict(l=2, r=5, t=5, b=15, pad=10),paper_bgcolor='#f9f9f9',plot_bgcolor='#f9f9f9') 
        return client_perf_bar
    else:
        client_table.loc[client_table['Profit/Loss %'] < 0, 'Profit/Loss %'] = client_table["Profit/Loss %"]*-1
        client_table['Profit/Loss'] = client_table['Profit/Loss'].apply(lambda x : "{:,}".format(x))
        client_table = client_table[client_table["Client Name"] != "SR250824955"]
        client_perf_bar = px.bar(client_table, x="Profit/Loss %", y="Client Name",orientation= "h", hover_name="Client Name", text='Profit/Loss %',
            hover_data={"Client Name": False,"Profit/Loss": True,"Nominal Amount": True},)
        client_perf_bar.update_traces(texttemplate='%{text:.2s}%', textposition='auto',textfont_size=10)
        client_perf_bar.update_layout(font=dict(size=10,),
                            margin=dict(l=2, r=5, t=5, b=15, pad=10),paper_bgcolor='#f9f9f9',plot_bgcolor='#f9f9f9') 
        return client_perf_bar

@app.callback(Output("coy_bar-graph", "figure"),
            [Input("coy_perf_dropdown","value"),Input("coy_time_dropdown","value")])
def coy_perf_value(value,value2):
    company_df = tdf[["Client Name","Asset Class","Name","Ticker","YTD%","1d %","5d %","1m % ","6m %","12m %"]]
    company_df = company_df[company_df["Asset Class"]== "EQUITIES"]
    count_client = company_df.groupby(["Name"])["Client Name"].nunique().reset_index(name="No of Client").sort_values("Name")

    company_df2 = tdf[["Asset Class","Name","Ticker","YTD%","1d %","5d %","1m % ","6m %","12m %"]]
    company_df2= company_df2.drop_duplicates().sort_values("Name")

    company_df_final = pd.merge(count_client,company_df2,on="Name")

    company_df_final = company_df_final[["Name","Ticker","No of Client",value2]]
    company_df_final = company_df_final.sort_values(value2)
    if value == "top":
        coy_table = company_df_final[company_df_final[value2] > 0]
        coy_perf_bar = px.bar(coy_table, x=value2, y="Ticker",orientation= "h", hover_name="Name", text=value2,
            hover_data=["Ticker","No of Client"])
        coy_perf_bar.update_traces(texttemplate='%{text:.2f}%', textposition='auto', textfont_size=10, marker_color="green")
        coy_perf_bar.update_layout(height=150+len(company_df_final)*5, font=dict(size=10,),
                            margin=dict(l=2, r=5, t=5, b=15, pad=10),paper_bgcolor='#f9f9f9',plot_bgcolor='#f9f9f9')
        return coy_perf_bar
    elif value == "bottom":
        coy_table = company_df_final[company_df_final[value2] < 0]
        coy_table[value2] = coy_table[value2]*-1
        coy_table = coy_table.sort_values(value2,ascending=True)
        coy_perf_bar = px.bar(coy_table, x=value2, y="Ticker",orientation= "h", hover_name="Name", text=value2,
            hover_data=["Ticker","No of Client"])
        coy_perf_bar.update_traces(texttemplate='%{text:.2f}%', textposition='auto', textfont_size=10, marker_color="crimson")
        coy_perf_bar.update_layout(height=len(company_df_final)*15, font=dict(size=10,),
                            margin=dict(l=2, r=5, t=5, b=15, pad=10),paper_bgcolor='#f9f9f9',plot_bgcolor='#f9f9f9')
        return coy_perf_bar
    else:
        coy_table = company_df_final[company_df_final[value2] > -99999]
        coy_table.loc[coy_table[value2] < 0, value2] = coy_table[value2]*-1
        #coy_table["1d %"] = coy_table["1d %"]*-1
        coy_table = coy_table.sort_values(value2,ascending=True)
        coy_perf_bar = px.bar(coy_table, x=value2, y="Ticker",orientation= "h", hover_name="Name", text=value2,
            hover_data=["Ticker","No of Client"])
        coy_perf_bar.update_traces(texttemplate='%{text:.2f}%', textposition='auto', textfont_size=10)
        coy_perf_bar.update_layout(height=len(company_df_final)*30, font=dict(size=10,),
                            margin=dict(l=2, r=5, t=5, b=15, pad=10),paper_bgcolor='#f9f9f9',plot_bgcolor='#f9f9f9')
        return coy_perf_bar

@app.callback(Output("remind_table", "data"),
            [Input("remind_dropdown","value")])
def remind_table_value(value):
    if value:
        sub_data = rdf[rdf["Reminder Type"] == value]
        final = sub_data.head(100).to_dict('record')
        return final
    else:
         final=rdf.head(100).to_dict('records')
         return final

@app.callback(
    Output('risk_target_status_table','data'),
    [Input('target_risk_filter', 'value')]
) 
def risk_target_status_table(target_risk_level):
    #print(target_risk_level)
    risk_table_df = risk_analysis_df[["Client Name","Current Risk Level","Target Risk Level"]]
    if target_risk_level != "All Levels" and target_risk_level != None:
        risk_table_df = risk_table_df.loc[risk_table_df["Target Risk Level"] == target_risk_level]
    #print(risk_table_df)
    table_data = risk_table_df.to_dict('records')
    return table_data

if __name__ == '__main__':
    app.run_server(debug=True)