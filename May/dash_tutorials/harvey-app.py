import dash
import dash_table
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import flask
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import time
import os
import psycopg2


app = dash.Dash('app', server=server)
app.debug = True

conn = psycopg2.connect(
   host="localhost",
   database="Citibank.FYP",
   user="postgres",
   password="postgres")

cur = conn.cursor()
cur.execute("SELECT public.\"Client\".\"Ticker\" FROM public.\"Client\" lIMIT 5")
rows = cur.fetchall()
df_postgres =  pd.DataFrame(rows)

cur.close()
conn.close()

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/hello-world-stock.csv')

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/Citibank.FYP'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
#df_postgres = db.Client

app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

app.layout = html.Div([
    html.H1('Stock Ticker'),
    dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in df_postgres.columns]
            ,data=df_postgres.to_dict("records")
        ),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Tesla', 'value': 'TSLA'},
            {'label': 'Apple', 'value': 'AAPL'},
            {'label': 'Coke', 'value': 'COKE'}
        ],
        value='TSLA'
    ),
    dcc.Graph(id='my-graph')
], className="container")

@app.callback(Output('my-graph', 'figure'),
              [Input('my-dropdown', 'value')])

def update_graph(selected_dropdown_value):
    dff = df[df['Stock'] == selected_dropdown_value]
    return {
        'data': [{
            'x': dff.Date,
            'y': dff.Close,
            'line': {
                'width': 3,
                'shape': 'spline'
            }
        }],
        'layout': {
            'margin': {
                'l': 30,
                'r': 20,
                'b': 30,
                't': 20
            }
        }
    }

if __name__ == '__main__':
    app.run_server()