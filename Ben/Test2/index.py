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
server = app.server

# Connect to your app pages
from apps import home, data_table


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('Home |', href='/apps/home'),
        dcc.Link('Data Table', href='/apps/datatable'),
    ],id="links", className="row"),
    html.Div(id='content', children=[])
])


@app.callback(Output('content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/home':
        return home.layout
    if pathname == '/apps/datatable':
        return data_table.layout
    else:
        return home.layout


if __name__ == '__main__':
    app.run_server(debug=True)
