import dash
import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
from datetime import datetime, date, timedelta

import os

#### is_thresholds_set Function checks if the threshold values have been set to monitor ####
def is_thresholds_set():
    if not os.path.exists('set_values_df.csv'):
        set_values_df = pd.DataFrame.from_dict(
            {
                "Asset Type": ["Equities", "Fixed Income", "Alternatives"],
                "Column Set": [],
                "Filter Condition": [],
                "Percentage Amt Set": [],
            }, orient='index'
        )
        set_values_df = set_values_df.transpose()
        now = datetime.now()
        now = now - timedelta(microseconds=now.microsecond)
        set_values_df["Time Updated"] = now
        set_values_df.to_csv(r"set_values_df.csv", index = False)
        return False

    print("Importing for latest set_values_df...")
    set_values_df = pd.read_csv('set_values_df.csv')
    check_no_of_nulls = set_values_df["Column Set"].isnull().sum()
    print("No. of values NOT set:",set_values_df["Column Set"].isnull().sum())
    if check_no_of_nulls != 3:
        return True
    return False
#### End of - is_thresholds_set Function ####

#### return_filtered_df Function that returns filtered df based on asset_type,column_name,condition,value set in web form ####
def return_filtered_df(df,asset_type,column_name,condition,value):
    excel_asset_type_mapping = {
        "Equities": "EQUITIES",
        "Fixed Income": "FIXED INCOME",
        "Alternatives": "ALTERNATIVE INVESTMENTS",
        }
    selected_asset_type = excel_asset_type_mapping[asset_type]
    
    df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
    df = df.dropna(subset=[column_name])
  
    conditions_dict = {
        "equal to": df[(df["Asset Class"] == selected_asset_type) & (df[column_name] == value)],
        "less than": df[(df["Asset Class"] == selected_asset_type) & (df[column_name] < value)],
        "less than or equal to": df[(df["Asset Class"] == selected_asset_type) & (df[column_name] <= value)],
        "greater than": df[(df["Asset Class"] == selected_asset_type) & (df[column_name] > value)],
        "greater than or equal to": df[(df["Asset Class"] == selected_asset_type) & (df[column_name] >= value)],
        }
    
    new_df = conditions_dict[condition]
    return new_df

#### End of - return_filtered_df Function ####

#### return_values_for_msg Function: imports lastest data and returns the three lists and three values ####
def return_values_for_msg():
    ############ Import all data files #################
    print("Importing for latest Client data...")
    client_df = pd.read_csv('Client.csv')
    print("Importing for latest set_values_df...")
    set_values_df = pd.read_csv('set_values_df.csv')
    ####################################################

    ############ DateTime conversion ###################
    client_df['Position As of Date'] = pd.to_datetime(client_df['Position As of Date'], errors='coerce').dt.strftime('%d/%m/%Y')
    client_df['Position As of Date']= pd.to_datetime(client_df['Position As of Date'])
    ####################################################

    ############ Get latest data ###################
    latest_date = client_df["Position As of Date"].max()
    latest_client_data = client_df[client_df['Position As of Date'] == latest_date]
    ################################################

    if pd.isnull(set_values_df["Column Set"][0]):
        no_of_companies_affected_in_equities = "-"
        eq_companies_list = []
    else:
        eq_df = return_filtered_df(latest_client_data,set_values_df["Asset Type"][0],set_values_df["Column Set"][0],set_values_df["Filter Condition"][0],set_values_df["Percentage Amt Set"][0])
        eq_companies_list = eq_df["Name"].unique().tolist()
        no_of_companies_affected_in_equities = len(eq_df["Name"].unique())
    if pd.isnull(set_values_df["Column Set"][1]):
        no_of_companies_affected_in_fixedincome = "-"
        fi_companies_list = []
    else:
        fi_df = return_filtered_df(latest_client_data,set_values_df["Asset Type"][1],set_values_df["Column Set"][1],set_values_df["Filter Condition"][1],set_values_df["Percentage Amt Set"][1])
        fi_companies_list = fi_df["Name"].unique().tolist()
        no_of_companies_affected_in_fixedincome = len(fi_df["Name"].unique())
    if  pd.isnull(set_values_df["Column Set"][2]):
        no_of_clients_affected_in_alternatives = "-"
        al_clients_list = []
    else:
        al_df = return_filtered_df(latest_client_data,set_values_df["Asset Type"][2],set_values_df["Column Set"][2],set_values_df["Filter Condition"][2],set_values_df["Percentage Amt Set"][2])
        al_clients_list = al_df["Client Name"].unique().tolist()
        no_of_clients_affected_in_alternatives = len(al_df["Client Name"].unique())
    print(no_of_companies_affected_in_equities, no_of_companies_affected_in_fixedincome, no_of_clients_affected_in_alternatives)
    return eq_companies_list, fi_companies_list, al_clients_list, no_of_companies_affected_in_equities, no_of_companies_affected_in_fixedincome, no_of_clients_affected_in_alternatives

#### End of - return_values_for_msg Function ####

####### DASH DataTables ########
set_values_table = dash_table.DataTable(
        id='set_values_table',
        style_cell={'textAlign': 'center','textOverflow': 'ellipsis','border': '1px solid black','font_size': '10px','padding': '5px'},
        style_as_list_view=True,
        fixed_rows={'headers': True},
        style_table={'overflowY': 'auto','height': '202px','border': 'thin lightgrey solid'},
        style_header={'fontWeight': 'bold', 'height': 'auto','whiteSpace': 'normal','border': '1px solid grey','backgroundColor':'#f2f2f2'},
        style_data={'minWidth': '90px','maxWidth': '90px'},
    )

equities_companies_table = dash_table.DataTable(
        id='equities_companies_table',
        style_cell={'textAlign': 'center','textOverflow': 'ellipsis','border': '1px solid black','font_size': '10px','padding': '5px'},
        style_as_list_view=True,
        fixed_rows={'headers': True},
        style_table={'overflowY': 'auto','height': '202px','border': 'thin lightgrey solid'},
        style_header = {'display': 'none'},
        style_data={'minWidth': '90px','maxWidth': '90px'},
        columns=[{"name": "eq", "id": "eq"}],
    )

fixed_income_companies_table = dash_table.DataTable(
        id='fixed_income_companies_table',
        style_cell={'textAlign': 'center','textOverflow': 'ellipsis','border': '1px solid black','font_size': '10px','padding': '5px'},
        style_as_list_view=True,
        fixed_rows={'headers': True},
        style_table={'overflowY': 'auto','height': '202px','border': 'thin lightgrey solid'},
        style_header = {'display': 'none'},
        style_data={'minWidth': '90px','maxWidth': '90px'},
        columns=[{"name": "fi", "id": "fi"}],
    )

alternatives_clients_table = dash_table.DataTable(
        id='alternatives_clients_table',
        style_cell={'textAlign': 'center','textOverflow': 'ellipsis','border': '1px solid black','font_size': '10px','padding': '5px'},
        style_as_list_view=True,
        fixed_rows={'headers': True},
        style_table={'overflowY': 'auto','height': '202px','border': 'thin lightgrey solid'},
        style_header = {'display': 'none'},
        style_data={'minWidth': '90px','maxWidth': '90px'},
        columns=[{"name": "alt", "id": "alt"}],
    )
####### End of - DASH DataTables ########

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Interval(
        id='my_interval',
        disabled=False,     #if True, the counter will no longer update
        interval=2*1000,    #increment the counter n_intervals every interval milliseconds
        n_intervals=0,      #number of times the interval has passed
        max_intervals=-1,    #number of times the interval will be fired.
                            #if -1, then the interval has no limit (the default)
                            #and if 0 then the interval stops running.
    ),
    dbc.Row([
        dbc.Col(html.H6(children='Set Values to Monitor and Send Notifications', style={'textAlign': 'center','color': 'white','backgroundColor': "#003B70"}),width=8),
        dbc.Col(html.H6(children='Latest Values Set to Monitor', style={'textAlign': 'center','color': 'white','backgroundColor': "#003B70"}),width=4),
        ]),
    dbc.Row([
        dbc.Col(
            dbc.Card([
            html.Br(),
            dbc.FormGroup([
                dbc.Col(dbc.Label("Equities", html_for="equities"), style={'textAlign': 'right'}, width=2),
                dbc.Col(
                    dcc.Dropdown(
                    id="equities_columns_dropdown",
                    options=[
                        {"label": "% Change from Avg Cost", "value": "% Change from Avg Cost"},
                        {"label": "1d %", "value": "1d %"},
                        {"label": "5d %", "value": "5d %"},
                        {"label": "1m %", "value": "1m %"},
                        {"label": "6m %", "value": "6m %"},
                        {"label": "12m %", "value": "12m %"},
                        {"label": "YTD%", "value": "YTD%"}
                    ],
                    placeholder="Choose column"), width=3),
                dbc.Col(
                    dcc.Dropdown(
                    id="equities_conditions_dropdown",
                    options=[
                        {"label": "equal to", "value": "equal to"},
                        {"label": "less than", "value": "less than"},
                        {"label": "less than or equal to", "value": "less than or equal to"},
                        {"label": "greater than", "value": "greater than"},
                        {"label": "greater than or equal to", "value": "greater than or equal to"},
                    ],
                    placeholder="Choose filter condition"), width=3),
                dbc.Col(dbc.Input(type="number", id="equities_percentage_amount", placeholder="Enter percentage amount"),width=3),
            ],row=True),

            dbc.FormGroup([
                dbc.Col(dbc.Label("Fixed Income", html_for="fixedincome"), style={'textAlign': 'right'}, width=2),
                dbc.Col(
                    dcc.Dropdown(
                    id="fixedincome_columns_dropdown",
                    options=[
                        {"label": "% Change from Avg Cost", "value": "% Change from Avg Cost"},
                        {"label": "1d %", "value": "1d %"},
                        {"label": "5d %", "value": "5d %"},
                        {"label": "1m %", "value": "1m %"},
                        {"label": "6m %", "value": "6m %"},
                        {"label": "12m %", "value": "12m %"},
                        {"label": "YTD%", "value": "YTD%"}
                    ],
                    placeholder="Choose column"), width=3),
                dbc.Col(
                    dcc.Dropdown(
                    id="fixedincome_conditions_dropdown",
                    options=[
                        {"label": "equal to", "value": "equal to"},
                        {"label": "less than", "value": "less than"},
                        {"label": "less than or equal to", "value": "less than or equal to"},
                        {"label": "greater than", "value": "greater than"},
                        {"label": "greater than or equal to", "value": "greater than or equal to"},
                    ],
                    placeholder="Choose filter condition"), width=3),
                dbc.Col(dbc.Input(type="number", id="fixedincome_percentage_amount", placeholder="Enter percentage amount"),width=3),
            ],row=True),

            dbc.FormGroup([
                dbc.Col(dbc.Label("Alternatives", html_for="alternatives"), style={'textAlign': 'right'}, width=2),
                dbc.Col(
                    dcc.Dropdown(
                    id="alternatives_columns_dropdown",
                    options=[
                        {"label": "Return on Contribution", "value": "Return on Contribution"}
                    ],
                    placeholder="Choose column"), width=3),
                dbc.Col(
                    dcc.Dropdown(
                    id="alternatives_conditions_dropdown",
                    options=[
                        {"label": "equal to", "value": "equal to"},
                        {"label": "less than", "value": "less than"},
                        {"label": "less than or equal to", "value": "less than or equal to"},
                        {"label": "greater than", "value": "greater than"},
                        {"label": "greater than or equal to", "value": "greater than or equal to"},
                    ],
                    placeholder="Choose filter condition"), width=3),
                dbc.Col(dbc.Input(type="number", id="alternatives_percentage_amount", placeholder="Enter percentage amount"),width=3),
            ],row=True),

            dbc.Row(dbc.Col(dbc.Button("Set Values", id='set_values_button', n_clicks=0, color="primary", outline=True), style={'textAlign': 'right'},width=11)),

        ], style={"height": "100%"}), width=8),
        dbc.Col(dbc.Card([
            html.Div(id='output_message', style={'textAlign': 'center'}),
            html.Br(),
            html.Div(set_values_table),
        ]), width=4)
    ]),
    html.Div(id="hidden_div",style={"display":"none"}),
    html.Br(),
    html.H6(children='Affected Companies/Clients Lists based on set thresholds', style={'textAlign': 'center','color': 'white','backgroundColor': "#003B70"}),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6(["Companies affected by Equities threshold", dbc.Badge(id="equities_companies_no", pill=True, color="primary", className="ml-1")], style={'textAlign': 'center'}),width=4),
        dbc.Col(html.H6(["Companies affected by Fixed Income threshold", dbc.Badge(id="fixed_income_companies_no",  pill=True, color="primary", className="ml-1")], style={'textAlign': 'center'}),width=4),
        dbc.Col(html.H6(["Clients affected by Alternatives threshold", dbc.Badge(id="alternatives_clients_no",  pill=True, color="primary", className="ml-1")], style={'textAlign': 'center'}),width=4),
        ]),
    dbc.Row([
        dbc.Col(equities_companies_table,width=4),
        dbc.Col(fixed_income_companies_table,width=4),
        dbc.Col(alternatives_clients_table,width=4)
    ])
    
])


@app.callback(
    [Output('hidden_div', 'children')],
    [Input('set_values_button', 'n_clicks'),
    Input('equities_columns_dropdown', 'value'),
    Input('equities_conditions_dropdown', 'value'),
    Input('equities_percentage_amount', 'value'),
    Input('fixedincome_columns_dropdown', 'value'),
    Input('fixedincome_conditions_dropdown', 'value'),
    Input('fixedincome_percentage_amount', 'value'),
    Input('alternatives_columns_dropdown', 'value'),
    Input('alternatives_conditions_dropdown', 'value'),
    Input('alternatives_percentage_amount', 'value')],
)
def generate_set_values(n_clicks, equities_columns_dropdown, equities_conditions_dropdown, equities_percentage_amount,
        fixedincome_columns_dropdown, fixedincome_conditions_dropdown, fixedincome_percentage_amount,
        alternatives_columns_dropdown, alternatives_conditions_dropdown, alternatives_percentage_amount):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "set_values_button" in changed_id:
        now = datetime.now()
        now = now - timedelta(microseconds=now.microsecond)
        set_values_df = pd.DataFrame(
            {
                "Asset Type": ["Equities", "Fixed Income", "Alternatives"],
                "Column Set": [equities_columns_dropdown, fixedincome_columns_dropdown, alternatives_columns_dropdown],
                "Filter Condition": [equities_conditions_dropdown, fixedincome_conditions_dropdown, alternatives_conditions_dropdown],
                "Percentage Amt Set": [equities_percentage_amount, fixedincome_percentage_amount, alternatives_percentage_amount],
            }
        )
        set_values_df["Time Updated"] = now
        set_values_df.to_csv(r"set_values_df.csv", index = False)
        
    hidden_div_children = [""]
    return hidden_div_children

@app.callback(
    [Output('output_message', 'children'),
    Output('set_values_table','columns'),
    Output('set_values_table','data'),
    Output('set_values_table','tooltip_data'),
    Output('equities_companies_no','children'),
    Output('fixed_income_companies_no','children'),
    Output('alternatives_clients_no','children'),
    Output('equities_companies_table','data'),
    Output('fixed_income_companies_table','data'),
    Output('alternatives_clients_table','data')],
    [Input('my_interval', 'n_intervals')])
def return_thresholds_set_table_and_affected_companies_clients(n_intervals):
    if n_intervals is None:
        raise PreventUpdate
    else:
        if not is_thresholds_set():
            output_msg = html.I("No values have been set to monitor so far.")
            set_values_df = pd.read_csv('set_values_df.csv')
            set_values_df = set_values_df.drop(columns="Time Updated")
            set_values_table_columns = [{"name": i, "id": i} for i in set_values_df.columns]
            set_values_table_data = set_values_df.to_dict('records')
            set_values_table_tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in set_values_df.to_dict('rows')
            ]

            equities_companies_no = "-"
            fixed_income_companies_no = "-"
            alternatives_clients_no = "-"
            equities_companies_table_data = []
            fixed_income_companies_table_data = []
            alternatives_clients_table_data = []
        else:
            set_values_df = pd.read_csv('set_values_df.csv')
            updated_time = set_values_df["Time Updated"][0]
            set_values_df = set_values_df.drop(columns="Time Updated")
            output_msg = html.I("Last updated: {}".format(updated_time))
            set_values_table_columns = [{"name": i, "id": i} for i in set_values_df.columns]
            set_values_table_data = set_values_df.to_dict('records')
            set_values_table_tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in set_values_df.to_dict('rows')
            ]

            equities_companies_list, fixed_income_companies_list, alternatives_clients_list, equities_companies_no, fixed_income_companies_no, alternatives_clients_no = return_values_for_msg()
            equities_companies_df = pd.DataFrame.from_dict({"eq": equities_companies_list})
            fixed_income_companies_df = pd.DataFrame.from_dict({"fi": fixed_income_companies_list})
            alternatives_clients_df = pd.DataFrame.from_dict({"alt": alternatives_clients_list})
            
            equities_companies_table_data = equities_companies_df.to_dict('records')
            fixed_income_companies_table_data = fixed_income_companies_df.to_dict('records')
            alternatives_clients_table_data = alternatives_clients_df.to_dict('records')

    return output_msg, set_values_table_columns, set_values_table_data, set_values_table_tooltip_data,\
    equities_companies_no, fixed_income_companies_no, alternatives_clients_no,\
    equities_companies_table_data, fixed_income_companies_table_data, alternatives_clients_table_data


if __name__ == '__main__':
    app.run_server(debug=True)