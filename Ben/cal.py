import datetime
import plotly.graph_objs as go
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
import dash
import calendar

app = dash.Dash(__name__)
year = datetime.datetime.now().year
month = datetime.datetime.now().month

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)

d1 = datetime.date(year, month, 1)
d2 = add_months(d1,3) - datetime.timedelta(1)
delta = d2 - d1

dates_in_year = [d1 + datetime.timedelta(i) for i in range(delta.days+1)] #gives me a list with datetimes for each day a year
print(len(dates_in_year))
weekdays_in_year = [i.weekday() for i in dates_in_year] #gives [0,1,2,3,4,5,6,0,1,2,3,4,5,6,…] (ticktext in xaxis dict translates this to weekdays
weeknumber_of_dates = [i.strftime("%b-W%V") for i in dates_in_year] #gives [1,1,1,1,1,1,1,2,2,2,2,2,2,2,…] name is self-explanatory
z = np.random.randint(2, size=(len(dates_in_year)))
print(z)

text = [str(i) for i in dates_in_year] 
text[10] = str(dates_in_year[10]) + "<br> Maturity: MSFT <br> Next Call: AAPL"
#gives something like list of strings like ‘2018-01-25’ for each date. Used in data trace to make good hovertext.
#4cc417 green #347c17 dark green
colorscale=[[False, "#eeeeee"], [True, "green"]]

data = [
    go.Heatmap(
    x = weeknumber_of_dates,
    y = weekdays_in_year,
    z = z,
    text=text,
    hoverinfo="text",
    xgap=6, # this
    ygap=6, # and this is used to make the grid-like apperance
    showscale=False,
    colorscale=colorscale
)
]
layout = go.Layout(
    #title="activity chart",
    height=320,
    width = 900,
    yaxis=dict(
    showline = False, showgrid = False, zeroline = False,
    tickmode="array",
    ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    tickvals=[0,1,2,3,4,5,6],
    ),
    xaxis=dict(
    showline = False, showgrid = False, zeroline = False,
    ),
    font={"size":8, "color":"#9e9e9e"},
    plot_bgcolor=("#fff"),
    margin = dict(t=40),
)


fig = go.Figure(data=data, layout=layout)
fig.update_layout(
    margin=dict(l=20, r=20, t=20, b=20, pad=5),
    paper_bgcolor="white",
)
fig.update_xaxes(side="top")

app.layout = html.Div([
dcc.Graph(id="heatmap-test", figure=fig, config={"displayModeBar": False})
])

if __name__ == '__main__':
    app.run_server(debug =True, port=5000)
