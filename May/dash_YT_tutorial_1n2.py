import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash()

########## Tutorial 1 ##############
# app.layout = html.Div(children=[
#     html.H1("Dash tutorials"),
#     dcc.Graph(id='example',
#     figure={
#         'data': [
#             {'x':[1,2,3,4,5],'y':[5,6,7,2,1],'type':'line','name':'boats'},
#             {'x':[1,2,4,3,5],'y':[3,3,3,2,5],'type':'bar','name':'cars'},
#             ],
#         'layout': {
#             'title':'Basic Dash Example'
#         }
#     })
#     ])

########### Tutorial 2 ###############
app.layout = html.Div(children=[
    dcc.Input(id='input',value='Enter something',type='text'),
    html.Div(id='output')
    ])

@app.callback(
    Output(component_id='output',component_property='children'),
    [Input(component_id='input',component_property='value')]
)
def update_value(input_data):
    try:
        # return "Input: {}".format(input_data) # this output what ever typed in input without error exception
        return str(float(input_data)**2)
    except:
        return "Some error"

########## Tutorial 3 ##############
app.layout = html.Div(children=[
    html.H1("Hello Dash"),
    ("Dash: A web application framework for Python."),
    dcc.Graph(id='example',
    figure={
        'data': [
            {'x':[1,2,3,4,5],'y':[5,6,7,2,1],'type':'line','name':'boats'},
            {'x':[1,2,4,3,5],'y':[3,3,3,2,5],'type':'bar','name':'cars'},
            ],
        'layout': {
            'title':'Dash Data Visualization'
        }
    })
    ])


if __name__ == '__main__':
    app.run_server(debug=True)