import numpy as np
import pandas as pd
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State

from navbar import html_layout


def init_dashboard(server):
    dash_app = dash.Dash(server=server, routes_pathname_prefix='/dash1/')

    """Create a Plotly Dash dashboard."""
    df = pd.read_csv('TestData.csv',encoding='latin1')
    df =df[df['Asset Class'].notnull()]

    numeric_cols = ['% Change from Avg Cost','YTD%', '1d %', '5d %', '1m % ', '6m %', '12m %'] + ['Nominal Amount (USD)','Nominal Units','Nominal Amount (CCY)','Current Price','Closing Price', 'Average Cost']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col].astype("float")
        df[col] = df[col].round(2)

    filtered_data = df[['Asset Class','Asset Sub Class', 'Name',
        'Ticker', 'CCY', 'Nominal Units', 'Nominal Amount (CCY)',
        'Nominal Amount (USD)', '% Change from Avg Cost', 'Current Price',
        'Closing Price', 'Average Cost', 'YTD%', '1d %', '5d %', '1m % ',
        '6m %', '12m %', 'Company Description']]
    
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
            print("BACKGROUND " + str(backgroundColor))
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
    (styles) = discrete_background_color_bins(df)
    # Create Dash Layout
    dash_app.index_string = html_layout
    dash_app.layout = html.Div([
        dash_table.DataTable(
        id="main_table",
        sort_action='native',
        columns=[{'name': i, 'id': i} for i in filtered_data.columns],
        style_data_conditional=styles,
        style_cell={'textAlign': 'center','padding': '6px', 'textOverflow': 'ellipsis','font_size': '10px','font': 'Lato','border': '1px solid grey'},
        style_as_list_view=True,
        style_header={'fontWeight': 'bold', 'height': 'auto','whiteSpace': 'normal','border': '1px solid grey'},
        fixed_rows={'headers': True},
        #export_columns = "all", export_format ="csv",
        style_data={
             'maxWidth': '70px','minWidth': '70px'},
         style_cell_conditional=[
            {'if': {'column_id': 'Name'},
            'width': '200px'},
        ],
        style_table={'height': '450px', 'overflowY': 'auto', 'overflowX': 'auto', 'width': '1350px'},
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in df.to_dict('rows')
        ],
        tooltip_duration=None,

        ),
        html.Button(id="submit-btn",n_clicks=0,children="apply"),

        dcc.Dropdown(
                id="assest_dropdown",
                options = [{'label': i, 'value': i} for i in df["Asset Class"].unique()],
            ),
        dcc.Dropdown(
                id="sub_asset_dropdown",
                options = [{'label': i, 'value': i} for i in df["Asset Sub Class"].unique()]
            ),
        dcc.Dropdown(
                id="currency_dropdown",
                options = [{'label': i, 'value': i} for i in df["CCY"].unique()]
            ),
        ])
    
    ######################## Callbacks ###############################################

    @dash_app.callback(Output("currency_dropdown","options"),
                [Input("assest_dropdown","value"),Input("sub_asset_dropdown","value")])
    def curr_input(Asset_input, Sub_Asset_input):
        if not Asset_input and not Sub_Asset_input:
            options = [{'label': i, 'value': i} for i in df["CCY"].unique()]
        elif Asset_input and not Sub_Asset_input:
            options = [{'label': i, 'value': i} for i in df["CCY"][df["Asset Class"] == Asset_input].unique()]
        elif not Asset_input and Sub_Asset_input:
            options = [{'label': i, 'value': i} for i in df["CCY"][df["Asset Sub Class"] == Sub_Asset_input].unique()]
        else:
            options = [{'label': i, 'value': i} for i in df["CCY"][(df["Asset Sub Class"] == Sub_Asset_input) & (df["Asset Class"] == Asset_input)].unique()]

        return options    

    #Sub Asset Dropdown
    @dash_app.callback(Output("sub_asset_dropdown","options"),
                [Input("assest_dropdown","value")])
    def asset_input(input_value):
        if not input_value:
            options = [{'label': i, 'value': i} for i in df["Asset Sub Class"].unique()]
        else:
            options = [{'label': i, 'value': i} for i in df["Asset Sub Class"][df["Asset Class"] == input_value].unique()]

        return options 

    #Asset Dropdown
    @dash_app.callback(Output("assest_dropdown","options"),
                [Input("sub_asset_dropdown","value")])
    def sub_asset_input(input_value):
        if not input_value:
            options = [{'label': i, 'value': i} for i in df["Asset Class"].unique()]
        else:
            options = [{'label': i, 'value': i} for i in df["Asset Class"][df["Asset Sub Class"] == input_value].unique()]
        
        return options
            
    #Main Table Chart
    @dash_app.callback([Output("main_table","data"),Output("main_table","tooltip_data")],
                [Input("submit-btn","n_clicks")],[State("assest_dropdown","value"),State("sub_asset_dropdown","value"),State("currency_dropdown","value")])
    def main_table_gather(n_clicks,Asset_input, Sub_Asset_input, curr_input):
        if not Asset_input and not Sub_Asset_input and not curr_input:
            data = df
        elif Asset_input and not Sub_Asset_input and not curr_input:
            data = df[df["Asset Class"]==Asset_input]
        elif not Asset_input and Sub_Asset_input and not curr_input:
            data = df[df["Asset Sub Class"]==Sub_Asset_input]
        elif not Asset_input and not Sub_Asset_input and curr_input:
            data = df[df["CCY"]==curr_input]
        else:
            data = df[(df["Asset Class"]==Asset_input) & (df["Asset Sub Class"]==Sub_Asset_input)]
            if data.empty:
                data = df[df["Asset Class"] == Asset_input]
        
        data = data[['Asset Class','Asset Sub Class', 'Name',
        'Ticker', 'CCY', 'Nominal Units', 'Nominal Amount (CCY)',
        'Nominal Amount (USD)', '% Change from Avg Cost', 'Current Price',
        'Closing Price', 'Average Cost', 'YTD%', '1d %', '5d %', '1m % ',
        '6m %', '12m %', 'Company Description']]

        tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in data.to_dict('rows')
            ]

        return data.to_dict('records'), tooltip_data

    return dash_app.server