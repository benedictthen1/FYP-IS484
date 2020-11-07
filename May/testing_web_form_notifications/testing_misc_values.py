import dash
import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
from datetime import datetime, date, timedelta

test_list1 = ['SR250594544', 'SR250824955'] 
test_list2 = ['SR111111111', 'SR222222222', 'SR333333333']

print(test_list1, test_list2)

test_list1.sort()
test_list2.sort()
print(test_list1, test_list2)

last_updated_values_df = pd.read_csv('set_values_df.csv')

print(last_updated_values_df.to_dict('records'))