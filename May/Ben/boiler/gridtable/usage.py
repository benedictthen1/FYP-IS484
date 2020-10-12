import gridtable
import dash
from dash.dependencies import Input, Output
import dash_html_components as html

app = dash.Dash(__name__)

columnDefs = [
    { "headerName": "Make", "field": "make" , "sortable": True, "filter": True},
    { "headerName": "Model", "field": "model" , "sortable": True, "filter": True},
    { "headerName": "Price", "field": "price" , "sortable": True, "filter": True}]

rowData = [
    { "make": "Toyota", "model": "Celica", "price": 35000 },
    { "make": "Ford", "model": "Mondeo", "price": 32000 },
    { "make": "Porsche", "model": "Boxter", "price": 72000 }]

app.layout = html.Div([
    gridtable.gridtable(
        id='input',
        value=columnDefs,
        label=rowData
    ),
    html.Div(id='output')
])


@app.callback(Output('output', 'children'), [Input('input', 'selectedRows')])
def display_selected_car(selectedRows):
    if selectedRows:
        print(selectedRows[0]['make'])
        return 'You selected car is made by {}, model is {}, price is {}'.format(selectedRows[0]['make'], selectedRows[0]['model'],selectedRows[0]['price'])


if __name__ == '__main__':
    app.run_server(debug=True)


if __name__ == '__main__':
    app.run_server(debug=True)
