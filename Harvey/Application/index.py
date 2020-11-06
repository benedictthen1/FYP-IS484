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

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import home, data_table, stocks, home2, client
#from apps import client, home2,stocks


nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Home",  href='/apps/home')),
        dbc.NavItem(dbc.NavLink("Home2",active=True, href='/apps/home2')),
        dbc.NavItem(dbc.NavLink("Client Page", href='/apps/client')),
        dbc.NavItem(dbc.NavLink("Stocks Page", href='/apps/stocks')),
        dbc.NavItem(dbc.NavLink("Data Table", href='/apps/datatable')),
    ], className="breadcrumb"
)

app.layout = html.Div([
    dcc.Store(id='coy_session', storage_type='session'),
    dcc.Store(id='client_session', storage_type='session'),
    dcc.Store(id='coy_to_client_session', storage_type='session'),
    dcc.Location(id='url', refresh=False),
    html.Div([nav],id="navbar_cont"),
    html.Div(id='content', children=[])
])


@app.callback(Output('content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/home':
        return home.layout
    if pathname == '/apps/home2':
        return home2.layout
    if pathname == '/apps/client':
         return client.layout
    if pathname == '/apps/stocks':
        return stocks.layout
    if pathname == '/apps/datatable':
        return data_table.layout
    else:
         return home2.layout


if __name__ == '__main__':
    app.run_server(debug=True)
