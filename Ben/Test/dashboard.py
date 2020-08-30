import numpy as np
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import dash_bootstrap_components as dbc

from navbar import html_layout


def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(server=server, routes_pathname_prefix='/dash1/', external_stylesheets=[dbc.themes.SUPERHERO])
    
    # Create Dash Layout
    df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    })

    fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")


    dash_app.index_string = html_layout
    dash_app.layout = html.Div([

    dcc.Graph(
        id='example-graph',
        figure=fig
        ),

    dcc.Graph(
        id='example-graph2',
        figure=fig
        )

    ])
    return dash_app.server