app = dash.Dash()

# app.layout = html.Div(children=[
#     html.Div(children='''
#     Client's Asset Class Chart
#     '''),
#     dcc.Dropdown(
#         id='my-dropdown',
#         options=[
#             {'label': name, 'value': name} for name in client_names
#         ],
#         value=client_names[0]
#     ),
#     dcc.Graph(id='asset_class_barchart')
#     ])

# @app.callback(
#     Output('asset_class_barchart','figure'),
#     [Input('input', 'value')]
# )

# def asset_class_barchart(client_name):
#     client_data = df.loc[df["Client Name"] == client_name]
#     group_by_asset_class = client_data\
#     .groupby(['Asset Class'], as_index=False)\
#     .agg({'Nominal Amount (USD)':'sum'})

#     return {
#         'data': [
#             {'x':group_by_asset_class['Asset Class'],'y':df.Close,'type':'bar','name':client_name},
#             ],
#         'layout': {
#             'title': input_data
#         }
#     }

# if __name__ == '__main__':
#     app.run_server(debug=True)