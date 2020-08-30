import numpy as np
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px

def init_dashboard2(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(server=server, routes_pathname_prefix='/dash2/', external_stylesheets=['/static/dist/css/styles.css'])

    # Create Dash Layout
    df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas","Cheese"],
    "Amount": [4, 1, 2, 2, 4, 5,10],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal","Singapore"]
    })

    fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

    dash_app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
        ),

    ])
    return dash_app.server