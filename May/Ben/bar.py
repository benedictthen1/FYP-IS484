import dash
import dash_core_components as dcc
import dash_table
import pandas as pd
import dash_html_components as html
import numpy as np
from dash.dependencies import Output, Input
import plotly.graph_objects as go


df = pd.read_csv('TestData.csv',encoding='latin1')
df =df[df['Asset Class'].notnull()]

numeric_cols = ['% Change from Avg Cost','YTD%', '1d %', '5d %', '1m % ', '6m %', '12m %']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col].astype("float")
    df[col] = df[col].round(2)

filtered_data = df[['Client Name','Asset Class','Asset Sub Class', 'Name',
       'Ticker', 'CCY', 'Nominal Units', 'Nominal Amount (CCY)',
       'Nominal Amount (USD)', '% Change from Avg Cost', 'Current Price',
       'Closing Price', 'Average Cost', 'YTD%', '1d %', '5d %', '1m % ',
       '6m %', '12m %', 'Company Description']]

cash = filtered_data['CCY'][filtered_data['Asset Class']=="Investment Cash & Short Term Investments"].unique()
ncash = [x for x in cash if x == x]
loans = filtered_data['CCY'][filtered_data['Asset Class']=="Loans"].unique()
nloan = [x for x in loans if x == x]
counts = filtered_data[filtered_data['Asset Class']=="Investment Cash & Short Term Investments"].groupby(['CCY'])['Nominal Amount (USD)'].sum()

#bar chart configurations
fig = go.Figure(data=[
    go.Bar(name='Cash', x=sorted(ncash), y=counts,marker_color='rgb(0,96,0)'),
    go.Bar(name='Loans', x=sorted(nloan), y=counts,marker_color='rgb(128,0,0)')
])

fig.update_layout(title='Cash vs Loan',barmode='group')

#DASH APP
app = dash.Dash(__name__)

app.layout = html.Div([

     dcc.Dropdown(
            id="asset_dropdown",
            options = [{'label': i, 'value': i} for i in df["Client Name"].unique()]
        ),

    dcc.Graph(id="bar_chart")

])

@app.callback(Output("bar_chart","figure"),
              [Input("asset_dropdown","value")])
def Asset_input(input_value):
    if not input_value:
        counts = filtered_data[filtered_data['Asset Class']=="Investment Cash & Short Term Investments"].groupby(['CCY'])['Nominal Amount (USD)'].sum()
    else:
         counts = filtered_data[(filtered_data['Asset Class']=="Investment Cash & Short Term Investments") & (filtered_data['Client Name']==input_value)].groupby(['CCY'])['Nominal Amount (USD)'].sum()

    fig = go.Figure(data=[
        go.Bar(name='Cash', x=sorted(ncash), y=counts,marker_color='rgb(0,96,0)'),
        go.Bar(name='Loans', x=sorted(nloan), y=counts,marker_color='rgb(128,0,0)')
    ])
    return fig   

if __name__ == '__main__':
    app.run_server(debug=True)