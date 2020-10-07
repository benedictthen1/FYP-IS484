import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import pathlib
import dash
import dash_table
import numpy as np
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
from app import app

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

# owner: shivp Kaggle. Source: https://data.mendeley.com/datasets
# dataset was modified. Original data: https://www.kaggle.com/shivkp/customer-behaviour
tdf = pd.read_csv(DATA_PATH.joinpath("TestData.csv"),encoding='latin1')
tdf =tdf[tdf['Asset Class'].notnull()]

numeric_cols = ['% Change from Avg Cost','YTD%', '1d %', '5d %', '1m % ', '6m %', '12m %'] + ['Nominal Amount (USD)','Nominal Units','Nominal Amount (CCY)','Current Price','Closing Price', 'Average Cost']
for col in numeric_cols:
    tdf[col] = pd.to_numeric(tdf[col], errors="coerce")
    tdf[col].astype("float")
    tdf[col] = tdf[col].round(2)

#SIDEBAR FILTER 
sidebar_header = dbc.Row([
        dbc.Col(html.H3("Table Filters", id="sidebar_title")),
        dbc.Col([
            html.Button(
                # use the Bootstrap navbar-toggler classes to style
                html.Span(className="navbar-toggler-icon"),
                className="navbar-toggler",
                # the navbar-toggler classes don't set color
                style={
                    "color": "rgba(0,0,0,.5)",
                    "border-color": "rgba(0,0,0,.1)",
                },
                id="navbar-toggle",),
            
            html.Button(
                # use the Bootstrap navbar-toggler classes to style
                html.Span(className="navbar-toggler-icon"),
                className="navbar-toggler",
                # the navbar-toggler classes don't set color
                style={
                    "color": "rgba(0,0,0,.5)",
                    "border-color": "rgba(0,0,0,.1)",
                },
                id="sidebar-toggle",),
            ],
            # the column containing the toggle will be only as wide as the
            # toggle, resulting in the toggle being right aligned
            width="auto",
            # vertically align the toggle in the center
            align="center",
        ),
    ])

sidebar = html.Div([
        sidebar_header,
        # we wrap the horizontal rule and short blurb in a div that can be
        # hidden on a small screen
        # html.Div([
        html.Hr(id="blurb"),
        # ], id="blurb",),
        # use the Collapse component to animate hiding / revealing links
        dbc.Collapse(
            html.Div([
                html.Div([
                    html.Button(id="main_select_btn",n_clicks=0,children="Select All"),
                    html.Button(id="main_clear_btn",n_clicks=0,children="Clear All"),
                ]),

                html.Div([ #Client title, clear and all button
                    html.H6("Client Name", className="checkbox_words"),
                    html.Button('Clear', id='client_clear_btn', n_clicks=0,className='all_clear_btn'),
                    html.Button('All', id='client_all_btn', n_clicks=0,className='all_clear_btn'),
                ],id="client_fitler_box"),

                html.Div([ #Base title, clear and all button
                    html.H6("Base Num", className="checkbox_words"),
                    html.Button('Clear', id='base_clear_btn', n_clicks=0,className='all_clear_btn'),
                    html.Button('All', id='base_all_btn', n_clicks=0,className='all_clear_btn'),
                ],id="base_fitler_box"),

                html.Div([ 
                dcc.Checklist(
                        options = [{'label': i, 'value': i} for i in tdf["Client Name"].unique()],
                        labelStyle={'display': 'block'},value = tdf["Client Name"].unique(),id = "client_checkbox"
                    ),
                dcc.Checklist(
                        options = [{'label': i, 'value': i} for i in tdf["Base Number"].unique()],
                        labelStyle={'display': 'block'},value = tdf["Base Number"].unique(),id = "base_checkbox"
                    ),    
                ],id="client_to_base_filter_box"),

                html.Div([ #Asset title, clear and all button
                    html.H6("Asset Class", className="checkbox_words"),
                    html.Button('Clear', id='asset_clear_btn', n_clicks=0,className='all_clear_btn'),
                    html.Button('All', id='asset_all_btn', n_clicks=0,className='all_clear_btn'),
                ],id="asset_fitler_box"),

                html.Div([ #Sub Asset title, clear and all button
                    html.H6("Asset-S Class", className="checkbox_words"),
                    html.Button('Clear', id='asset_sub_clear_btn', n_clicks=0,className='all_clear_btn'),
                    html.Button('All', id='asset_sub_all_btn', n_clicks=0,className='all_clear_btn'),
                ],id="asset_sub_fitler_box"),
                

                html.Div([
                    dcc.Checklist(
                            options = [{'label': i, 'value': i} for i in tdf["Asset Class"].unique()],
                            labelStyle={'display': 'block'},value = tdf["Asset Class"].unique(),id = "asset_checkbox"
                        ),
                    dcc.Checklist(
                            options = [{'label': i, 'value': i} for i in tdf["Asset Sub Class"].unique()],
                            labelStyle={'display': 'block'},value = tdf["Asset Sub Class"].unique(),id = "sub_asset_checkbox"
                        ),
                ],id="Asset_to_Sub_filter_box"),

                html.Div([ #Currency title, clear and all button
                    html.H6("CCY", className="checkbox_words"),
                    html.Button('Clear', id='ccy_clear_btn', n_clicks=0,className='all_clear_btn'),
                    html.Button('All', id='ccy_all_btn', n_clicks=0,className='all_clear_btn'),
                ],id="ccy_filter_box"),

                html.Br(),

                html.Div ([
                    dcc.Checklist(
                            options = [{'label': i, 'value': i} for i in tdf["CCY"].unique()],
                            labelStyle={'display': 'block'},value = tdf["CCY"].unique(),id = "ccy_checkbox"
                        ),
                ],id="ccy_to_ccy_filter_box"),

                html.Button(id="submit-btn",n_clicks=0,children="Apply"),
                # dcc.Dropdown(
                #     id="assest_dropdown",
                #     options = [{'label': i, 'value': i} for i in df["Asset Class"].unique()],
                # ),
                # dcc.Dropdown(
                #     id="sub_asset_dropdown",
                #     options = [{'label': i, 'value': i} for i in df["Asset Sub Class"].unique()]
                # ),
                # dcc.Dropdown(
                #     id="currency_dropdown",
                #     options = [{'label': i, 'value': i} for i in df["CCY"].unique()]
                # ),
                
            ]),
            id="collapse",             
        ),
    ],
    id="sidebar",
)

#table colour scale function
def discrete_background_color_bins(df, n_bins=7, columns= ['% Change from Avg Cost','YTD%', '1d %', '5d %', '1m % ', '6m %', '12m %']):
    import colorlover
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    if columns == 'all':
        if 'id' in df:
            df_numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
        else:
            df_numeric_columns = df.select_dtypes('number')
    else:
        df_numeric_columns = df[columns]

    df_max = df_numeric_columns.max().max()
    df_min = df_numeric_columns.min().min()
    ranges = [
        ((df_max - df_min) * i) + df_min
        for i in bounds
    ]
    ranges = [-100, -50, -25, -10 ,0, 10 , 25, 50, 75, 100]

    styles = []
    colours = ['rgb(215,25,28)', 'rgb(201,122,44)', 'rgb(209, 164, 29)','rgb(255, 255, 255)','rgb(255, 255, 255)', 'rgb(100,181,65)', 'rgb(26,150,65)']
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        backgroundColor = colours[i-1]
        #print("BACKGROUND " + str(backgroundColor))
        #color = 'white' if i > len(bounds) / 2. else 'inherit'
        color = 'inherit'

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
print(tdf.columns)
(styles) = discrete_background_color_bins(tdf)

#MAIN DASH TABLE
main_table = html.Div([
                dash_table.DataTable(
                    id="main_table",
                    sort_action='native',
                    #columns=[{'name': i, 'id': i} for i in filtered_data.columns],
                    style_data_conditional=styles,
                    page_size=100,
                    style_cell={'textAlign': 'center','padding': '6px', 'textOverflow': 'ellipsis','font_size': '10px','font': 'Lato','border': '1px solid grey'},
                    style_as_list_view=True,
                    style_header={'fontWeight': 'bold', 'height': 'auto','whiteSpace': 'normal','border': '1px solid grey'},
                    fixed_rows={'headers': True},
                    #export_columns = "all", export_format ="csv",
                    style_data={'maxWidth': '70px','minWidth': '70px'},
                    style_cell_conditional=[
                        {'if': {'column_id': 'Name'},
                        'width': '200px'},
                    ],
                    style_table={'height': '450px', 'overflowY': 'auto', 'overflowX': 'auto', 'width': '1350px','overflow':'auto'},
                    tooltip_data=[
                        {
                            column: {'value': str(value), 'type': 'markdown'}
                            for column, value in row.items()
                        } for row in tdf.to_dict('rows')
                    ],
                    tooltip_duration=None,
        ),
    ])

testdata = px.data.iris() # iris is a pandas DataFrame
fig21 = px.scatter(testdata, x="sepal_width", y="sepal_length")

layout = html.Div([

    sidebar,

    html.Div(id="testing"),
    html.Div([
        dbc.Button("Main", color="dark",size="sm", id="main_btn",n_clicks=0, className="mr-1"),
        dbc.Button("Equities", color="dark",size="sm", id="eq_btn",n_clicks=0, className="mr-1"),
        dbc.Button("Cash Liab", color="dark",size="sm", id="cl_btn",n_clicks=0, className="mr-1"),
        dbc.Button("Fixed Inc", color="dark",size="sm", id="fi_btn",n_clicks=0, className="mr-1"),
        dbc.Button("Alters", color="dark",size="sm", id="alt_btn",n_clicks=0, className="mr-1"),
        main_table,
    ],id="page-content"),

    dbc.Modal(
            [
                dbc.ModalHeader("Header"),
                dbc.ModalBody(
                    html.Div([
                        html.H1("HELLOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"),
                        html.H1("HELLOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"),
                        html.H1("HELLOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"),
                        html.H1("HELLOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"),
                        html.H1("HELLOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"),
                        html.H1("HELLOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"),
                        html.H1("HELLOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"),
                        html.Div(id="testingz"),  
                        html.Div(
                            dcc.Graph(figure=fig21)
                        )   
                    ])   
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close-body-scroll", className="ml-auto"
                    )
                ),
            ],
            id="modal-body-scroll",
            size="xl",
            scrollable=True,
        ),

    # dcc.Dropdown(
    #         id="assest_dropdown",
    #         options = [{'label': i, 'value': i} for i in df["Asset Class"].unique()],
    #     ),
    # dcc.Dropdown(
    #         id="sub_asset_dropdown",
    #         options = [{'label': i, 'value': i} for i in df["Asset Sub Class"].unique()]
    #     ),
    # dcc.Dropdown(
    #         id="currency_dropdown",
    #         options = [{'label': i, 'value': i} for i in df["CCY"].unique()]
    #     ),
    # html.Button(id="submit-btn",n_clicks=0,children="apply"),
])

######################## Callbacks ###############################################
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

app.callback(
    Output("modal-body-scroll", "is_open"),
    [Input("main_table","selected_cells"),Input("close-body-scroll", "n_clicks")],
    [State("modal-body-scroll", "is_open")],
)(toggle_modal)

@app.callback(Output("testingz", "children"),
            [Input("main_table","selected_cells"),Input("main_table","derived_virtual_data")])
def toggle_details(t1, t2):
    if t1:
        print(t1)
        print(t2[0])
        print("row number:")
        row_num = t1[0]["row"]
        print("col number:")
        col_name = t1[0]["column_id"]
        return t2[row_num][col_name]


@app.callback(Output("sidebar", "className"),[Input("sidebar-toggle", "n_clicks")],[State("sidebar", "className")])
def toggle_classname(n, classname):
    if n and classname == "":
        return "collapsed"
    return ""

@app.callback(Output("collapse", "is_open"),[Input("navbar-toggle", "n_clicks")],[State("collapse", "is_open")])
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

#Client filter CLEAR & ALL btn
@app.callback(Output("client_checkbox", "value"),
             [Input("client_clear_btn", "n_clicks"),Input("client_all_btn","n_clicks"),Input("main_select_btn","n_clicks"),Input("main_clear_btn","n_clicks")])
def client_clear(clear,all,select_all,clear_all):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "client_clear_btn" in changed_id:
        value = []
    elif "main_clear_btn" in changed_id:
        value = []
    elif "main_select_btn" in changed_id:
        value = tdf["Client Name"].unique()
    else:
        value = tdf["Client Name"].unique()
    return value

#Asset filter CLEAR & ALL btn
@app.callback(Output("asset_checkbox", "value"),
             [Input("asset_clear_btn", "n_clicks"),Input("asset_all_btn","n_clicks"),Input("main_select_btn","n_clicks"),Input("main_clear_btn","n_clicks")])
def base_clear(clear,all,select_all,clear_all):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "asset_clear_btn" in changed_id:
        value = []
    elif "main_clear_btn" in changed_id:
        value = []
    elif "main_select_btn" in changed_id:
        value = tdf["Asset Class"].unique()
    else:
        value = tdf["Asset Class"].unique()
    return value

#Sub Asset filter CLEAR & ALL btn
# @app.callback(Output("asset_checkbox", "value"),
#              [Input("asset_clear_btn", "n_clicks"),Input("asset_all_btn","n_clicks")])
# def base_clear(clear,all):
#     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
#     if "asset_clear_btn" in changed_id:
#         value = []
#     else:
#         value = df["Asset Class"].unique()
#     return value

#Base Number Checkbox based on Client input, Base clear and all button filter. 
@app.callback([Output("base_checkbox","options"),Output("base_checkbox","value")],
              [Input("client_checkbox","value"),Input("base_clear_btn", "n_clicks"),Input("base_all_btn","n_clicks"),Input("main_clear_btn","n_clicks")])
def client_input(client_input,clear,all,clear_all):
    if not client_input:
        options = [{'label': i, 'value': i} for i in tdf["Base Number"].unique()]
        value = []
    else:
        options = [{'label': i, 'value': i} for i in tdf["Base Number"][tdf["Client Name"].isin(client_input)].unique()]
        value = tdf["Base Number"][tdf["Client Name"].isin(client_input)]
    
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "base_clear_btn" in changed_id:
        value = []
    elif "main_clear_btn" in changed_id:
        value = []
    else:
        value = tdf["Base Number"].unique()

    return options,value

# Sub Asset Class Checkbox
@app.callback([Output("sub_asset_checkbox","options"),Output("sub_asset_checkbox","value")],
             [Input("asset_checkbox","value"),Input("asset_sub_clear_btn", "n_clicks"),Input("asset_sub_all_btn","n_clicks"),
             Input("main_select_btn","n_clicks"),Input("main_clear_btn","n_clicks")])
def base_input(base_input,clear,all,select_all,clear_all):
    if not base_input:
        options = [{'label': i, 'value': i} for i in tdf["Asset Sub Class"].unique()]
        value = []
    else:
        options = [{'label': i, 'value': i} for i in tdf["Asset Sub Class"][tdf["Asset Class"].isin(base_input)].unique()]
        value = tdf["Asset Sub Class"][tdf["Asset Class"].isin(base_input)]

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "asset_sub_clear_btn" in changed_id:
        value = []
    elif "main_clear_btn" in changed_id:
        value = []
    elif "main_select_btn" in changed_id:
        value = tdf["Asset Sub Class"].unique()

    return options,value

#CCY filter CLEAR & ALL btn
@app.callback(Output("ccy_checkbox", "value"),
             [Input("ccy_clear_btn", "n_clicks"),Input("ccy_all_btn","n_clicks"),Input("main_select_btn","n_clicks"),Input("main_clear_btn","n_clicks")])
def CCY_clear(clear,all,select_all,clear_all):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "ccy_clear_btn" in changed_id:
        value = []
    elif "main_clear_btn" in changed_id:
        value = []
    elif "main_select_btn" in changed_id:
        value = tdf["CCY"].unique()
    else:
        value = tdf["CCY"].unique()
    return value

# @app.callback([Output("asset_checkbox","options"),Output("asset_checkbox","value")],
#              [Input("client_checkbox","value")])
# def asset_checkbox(client_input):
#     if not client_input:
#         options = [{'label': i, 'value': i} for i in df["Asset Class"].unique()]
#         value = []
#     else:
#         options = [{'label': i, 'value': i} for i in df["Asset Class"][df["Client Name"].isin(client_input)].unique()]
#         value = df["Asset Sub Class"][df["Client Name"].isin(client_input)]
#     return options,value

#Curreny Dropdown
# @app.callback(Output("currency_dropdown","options"),
#               [Input("assest_dropdown","value"),Input("sub_asset_dropdown","value")])
# def curr_input(Asset_input, Sub_Asset_input):
#     if not Asset_input and not Sub_Asset_input:
#         options = [{'label': i, 'value': i} for i in df["CCY"].unique()]
#     elif Asset_input and not Sub_Asset_input:
#         options = [{'label': i, 'value': i} for i in df["CCY"][df["Asset Class"] == Asset_input].unique()]
#     elif not Asset_input and Sub_Asset_input:
#         options = [{'label': i, 'value': i} for i in df["CCY"][df["Asset Sub Class"] == Sub_Asset_input].unique()]
#     else:
#        options = [{'label': i, 'value': i} for i in df["CCY"][(df["Asset Sub Class"] == Sub_Asset_input) & (df["Asset Class"] == Asset_input)].unique()]

#     return options    

#Sub_Asset Dropdown
# @app.callback(Output("sub_asset_dropdown","options"),
#               [Input("assest_dropdown","value")])
# def sub_asset_input(input_value):
#     if not input_value:
#         options = [{'label': i, 'value': i} for i in df["Asset Sub Class"].unique()]
#     else:
#         options = [{'label': i, 'value': i} for i in df["Asset Sub Class"][df["Asset Class"] == input_value].unique()]

#     return options 

#Asset Dropdown
# @app.callback(Output("assest_dropdown","options"),
#               [Input("sub_asset_dropdown","value")])
# def asset_input(input_value):
#     if not input_value:
#         options = [{'label': i, 'value': i} for i in df["Asset Class"].unique()]
#     else:
#         options = [{'label': i, 'value': i} for i in df["Asset Class"][df["Asset Sub Class"] == input_value].unique()]
    
#     return options
        
#Main Table Cells
# @app.callback(Output("testing","children"),
#               [Input("main_table","selected_cells"),Input("main_table","derived_virtual_data")])
# def test(cell,cell2):
#     if cell:
#         print(cell)
#     if cell2:
#         print(cell2[0]['Asset Class'])

#Main Table column titles change according to excel tabs
@app.callback(Output("main_table","columns"),
              [Input("eq_btn","n_clicks"),Input("main_btn","n_clicks"),Input("cl_btn","n_clicks")])
def main_table_col(sub_click,eq_click,cl_click):
    data = tdf
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "eq_btn" in changed_id:
        data = data
    elif "main_btn" in changed_id:
        data = data
    elif "cl_btn" in changed_id:
        data = data[['Client Name','Base Number','Asset Class','Asset Sub Class','Nominal Units', 
        'Nominal Amount (CCY)','Nominal Amount (USD)']]
    else:
        data = data[['Client Name','Base Number','Asset Class','Asset Sub Class', 'Name',
       'Ticker', 'CCY', 'Nominal Units', 'Nominal Amount (CCY)',
       'Nominal Amount (USD)', '% Change from Avg Cost', 'Current Price',
       'Closing Price', 'Average Cost', 'YTD%', '1d %', '5d %', '1m % ',
       '6m %', '12m %', 'Company Description']]
    
    columns=([{'name': i, 'id': i} for i in data.columns])
    return columns

#MAINT TABLE ADJUST FROM FILTERS
@app.callback([Output("main_table","data"),Output("main_table","tooltip_data")],
              [Input("submit-btn","n_clicks"),Input("eq_btn","n_clicks"),Input("main_btn","n_clicks"),Input("cl_btn","n_clicks")],
              [State("client_checkbox","value"),State("base_checkbox","value"),State("asset_checkbox","value"),State("sub_asset_checkbox","value"),State("ccy_checkbox","value")])
def main_table_gather(sub_click, eq_click, main_click,cl_click, Client_input, Base_input, Asset_input, Sub_Asset_input, curr_input):
    data = tdf
    if Client_input and Base_input and Asset_input and Sub_Asset_input and curr_input:
        data =  tdf[
            (tdf["Client Name"].isin(Client_input)) & 
            (tdf["Base Number"].isin(Base_input)) &
            (tdf["Asset Class"].isin(Asset_input)) &
            (tdf["Asset Sub Class"].isin(Sub_Asset_input)) &
            (tdf["CCY"].isin(curr_input))
            ]
    elif Client_input and Base_input and Asset_input and Sub_Asset_input:
        data =  tdf[
            (tdf["Client Name"].isin(Client_input)) & 
            (tdf["Base Number"].isin(Base_input)) &
            (tdf["Asset Class"].isin(Asset_input)) &
            (tdf["Asset Sub Class"].isin(Sub_Asset_input))
            ]
    elif Client_input and Base_input: 
        data = tdf[(tdf["Client Name"].isin(Client_input)) & (tdf["Base Number"].isin(Base_input))]
    elif Client_input:
        data = tdf[tdf["Client Name"].isin(Client_input)]
    elif not Client_input and Base_input:
         data = tdf[tdf["Base Number"].isin(Base_input)]
    elif not Client_input and not Base_input and  not Asset_input and not Sub_Asset_input and not curr_input:
        data =  tdf[
            (tdf["Client Name"].isin(Client_input)) & 
            (tdf["Base Number"].isin(Base_input)) &
            (tdf["Asset Class"].isin(Asset_input)) &
            (tdf["Asset Sub Class"].isin(Sub_Asset_input))
            ]
    else:
        data = tdf
    
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "eq_btn" in changed_id:
        data = data[data["Asset Class"]=="EQUITIES"]
    elif "main_btn" in changed_id:
        data = data
    elif "cl_btn" in changed_id:
         data = data[data["Asset Class"]=="Investment Cash & Short Term Investments"]
    else:
        data = tdf
    # else:
    #     data = data[['Asset Class','Asset Sub Class', 'Name',
    #    'Ticker', 'CCY', 'Nominal Units', 'Nominal Amount (CCY)',
    #    'Nominal Amount (USD)', '% Change from Avg Cost', 'Current Price',
    #    'Closing Price', 'Average Cost', 'YTD%', '1d %', '5d %', '1m % ',
    #    '6m %', '12m %', 'Company Description']]

    tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in data.to_dict('rows')
        ]

    return data.to_dict('records'), tooltip_data,