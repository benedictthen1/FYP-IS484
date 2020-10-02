import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas_datareader.data as web
import datetime

# start = datetime.datetime(2015, 1, 1)
# end = datetime.datetime.now()

# df = web.DataReader('TSLA','yahoo', start, end)

# print(df.head()) # this will print the first few rows in terminal window

# stock = 'TSLA'

# df = web.DataReader(stock,'yahoo', start, end)

app = dash.Dash()

# app.layout = html.Div(children=[
#     html.H1("Learn from sentdex"),
#     ("omg finance"),
#     dcc.Graph(id='example',
#     figure={
#         'data': [
#             {'x':df.index,'y':df.Close,'type':'line','name':stock},
#             ],
#         'layout': {
#             'title': stock
#         }
#     })
#     ])

app.layout = html.Div(children=[
    html.Div(children='''
    symbol to graph:
    '''),

    dcc.Input(id='input', value='',type='text'),
    html.Div(id='output-graph')
    ])

@app.callback(
    Output('output-graph', component_property='children'),
    [Input('input', 'value')]
)

def update_graph(input_data):

    start = datetime.datetime(2015, 1, 1)
    end = datetime.datetime.now()
    df = web.DataReader(input_data,'yahoo', start, end)

    return dcc.Graph(id='example-graph',
    figure={
        'data': [
            {'x':df.index,'y':df.Close,'type':'line','name':input_data},
            ],
        'layout': {
            'title': input_data
        }
    })

if __name__ == '__main__':
    app.run_server(debug=True)