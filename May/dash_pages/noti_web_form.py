import dash
import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
from datetime import date, timedelta


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.Button('Click Me', id='button'),
    html.H3(id='button-clicks'),

    html.Hr(),

    html.Label('Input 1'),
    dcc.Input(id='input-1'),

    html.Label('Input 2'),
    dcc.Input(id='input-2'),

    html.Label('Slider 1'),
    dcc.Slider(id='slider-1'),

    html.Button('Click Me', id='button-2'),

    html.Div(id='output')
])

@app.callback(
    Output('button-clicks', 'children'),
    [Input('button', 'n_clicks')])
def clicks(n_clicks):
    return 'Button has been clicked {} times'.format(n_clicks)

@app.callback(
    Output('output', 'children'),
    [Input('button-2', 'n_clicks')],
    state=[State('input-1', 'value'),
     State('input-2', 'value'),
     State('slider-1', 'value')])
def compute(n_clicks, input1, input2, slider1):
    return 'A computation based off of {}, {}, and {}'.format(
        input1, input2, slider1
    )

if __name__ == '__main__':
    app.run_server(debug=True)
    app.config['suppress_callback_exceptions'] = True