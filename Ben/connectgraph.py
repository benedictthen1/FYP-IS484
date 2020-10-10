import dash  # use Dash version 1.16.0 or higher for this app to work
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.express as px
import pandas as pd
import numpy as np

tdf = pd.read_csv("TestData.csv",encoding='latin1')
numeric_cols = ['% Change from Avg Cost','YTD%', '1d %', '5d %', '1m % ', '6m %', '12m %'] + ['Nominal Amount (USD)','Nominal Units','Nominal Amount (CCY)','Current Price','Closing Price', 'Average Cost']
for col in numeric_cols:
    tdf[col] = pd.to_numeric(tdf[col], errors="coerce")
    tdf[col].astype("float")
    tdf[col] = tdf[col].round(2)

data = tdf[tdf["Asset Class"]== "EQUITIES"]
data = tdf[tdf["Asset Class"].isin(["EQUITIES","ALTERNATIVE INVESTMENTS","FIXED INCOME"])]
data["Profit/Loss"] = (data["Current Price"] - data["Average Cost"]) * data["Nominal Units"]
#df["Profit/Loss %"] = df["Profit/Loss"]/(df["Current Price"]*df["Nominal Units"]) * 100
client_table = data.groupby(["Client Name"])[["Profit/Loss","Nominal Amount (CCY)"]].sum().reset_index()
client_table["Profit/Loss"] = client_table["Profit/Loss"].round(2)
client_table["Nominal Amount (CCY)"] = client_table["Nominal Amount (CCY)"].round(2)
client_table["Profit/Loss %"] = client_table["Profit/Loss"]/client_table["Nominal Amount (CCY)"]*100
client_table["Profit/Loss %"] = client_table["Profit/Loss %"].round(1)
client_table["Nominal Amount"] = client_table["Nominal Amount (CCY)"]
client_table = client_table[["Client Name","Nominal Amount","Profit/Loss","Profit/Loss %"]].sort_values("Profit/Loss %")

df = px.data.gapminder()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



color=np.where(np.logical_and(client_table['Profit/Loss'] >= 0, client_table['Profit/Loss']) <0, 'green', 'red'),

fig = px.bar(client_table, x="Profit/Loss %", y="Client Name",orientation= "h", hover_name="Client Name", text='Profit/Loss %',
            hover_data={"Client Name": False,
                        "Profit/Loss": ':.2f',
                        "Nominal Amount": ':.2f'})
fig.update_traces(texttemplate='%{text:.2s}%', textposition='outside')
fig.update_layout(uniformtext_minsize=3, uniformtext_mode='hide')

app.layout = html.Div([
    dcc.Dropdown(id='dpdn2', value=['Germany','Brazil'], multi=True,
                 options=[{'label': x, 'value': x} for x in
                          df.country.unique()]),
    html.Div([
        dcc.Graph(id='pie-graph', figure={}, className='six columns'),
        dcc.Graph(id='my-graph', figure={}, clickData=None, hoverData=None, # I assigned None for tutorial purposes. By defualt, these are None, unless you specify otherwise.
                  config={
                      'staticPlot': False,     # True, False
                      'scrollZoom': True,      # True, False
                      'doubleClick': 'reset',  # 'reset', 'autosize' or 'reset+autosize', False
                      'showTips': False,       # True, False
                      'displayModeBar': True,  # True, False, 'hover'
                      'watermark': True,
                      # 'modeBarButtonsToRemove': ['pan2d','select2d'],
                        },
                  className='six columns'
                  ),
        dcc.Graph(id="bar-graph",figure=fig),
        dcc.Graph(id='pie2', figure={}),
    ])
])

@app.callback(
    Output(component_id='pie2', component_property='figure'),
    Input(component_id='bar-graph', component_property='hoverData'),
    Input(component_id='bar-graph', component_property='clickData')
)
def update_side_graph(hov_data, clk_data):
    client_table = data.groupby(["Client Name","Base Number"])[["Profit/Loss","Nominal Amount (CCY)"]].sum().reset_index()
    client_table["Profit/Loss"] = client_table["Profit/Loss"].round(2)
    client_table["Nominal Amount (CCY)"] = client_table["Nominal Amount (CCY)"].round(2)
    client_table["Profit/Loss %"] = client_table["Profit/Loss"]/client_table["Nominal Amount (CCY)"]*100
    client_table["Profit/Loss %"] = client_table["Profit/Loss %"].round(1)
    client_table["Nominal Amount"] = client_table["Nominal Amount (CCY)"]
    client_table = client_table[["Client Name","Base Number","Nominal Amount","Profit/Loss","Profit/Loss %"]].sort_values("Profit/Loss %")
    #hoc = hov_data['points'][0]['hovertext']
    if clk_data is None:
        #print(client_table)
        fdf = client_table[client_table["Client Name"] == "SR250824955"]
        print("TEST")
        print(fdf)
        fig10 = px.pie(data_frame=fdf, values='Nominal Amount', names='Base Number', title=f'Client: SR250824955 Nom Amount Breakdown')
        return fig10
    else:
        clk = clk_data['points'][0]['hovertext']
        fdf = client_table[client_table["Client Name"] == clk]
        print(fdf)
        fig10 = px.pie(data_frame=fdf, values='Nominal Amount', names='Base Number', title=f'Client: {clk} Nom Amount Breakdown')
        return fig10


@app.callback(
    Output(component_id='my-graph', component_property='figure'),
    Input(component_id='dpdn2', component_property='value'),
)
def update_graph(country_chosen):
    dff = df[df.country.isin(country_chosen)]
    fig = px.line(data_frame=dff, x='year', y='gdpPercap', color='country',
                  custom_data=['country', 'continent', 'lifeExp', 'pop'])
    fig.update_traces(mode='lines+markers')
    return fig


# Dash version 1.16.0 or higher
@app.callback(
    Output(component_id='pie-graph', component_property='figure'),
    Input(component_id='my-graph', component_property='hoverData'),
    Input(component_id='my-graph', component_property='clickData'),
    Input(component_id='my-graph', component_property='selectedData'),
    Input(component_id='dpdn2', component_property='value')
)
def update_side_graph(hov_data, clk_data, slct_data, country_chosen):
    if hov_data is None:
        dff2 = df[df.country.isin(country_chosen)]
        dff2 = dff2[dff2.year == 1952]
        print(dff2)
        fig2 = px.pie(data_frame=dff2, values='pop', names='country',
                      title='Population for 1952')
        return fig2
    else:
        print(f'hover data: {hov_data}')
        # print(hov_data['points'][0]['customdata'][0])
        # print(f'click data: {clk_data}')
        # print(f'selected data: {slct_data}')
        dff2 = df[df.country.isin(country_chosen)]
        hov_year = hov_data['points'][0]['x']
        dff2 = dff2[dff2.year == hov_year]
        fig2 = px.pie(data_frame=dff2, values='pop', names='country', title=f'Population for: {hov_year}')
        return fig2


if __name__ == '__main__':
    app.run_server(debug=True)