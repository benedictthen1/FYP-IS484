import dash
import dash_bootstrap_components as dbc
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

# Connect to your app pages
from apps import home, data_table

# meta_tags are required for the app layout to be mobile responsive
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server
app.config["suppress_callback_exceptions"] = True

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


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)