import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

import pandas_datareader.data as web
import datetime

df = pd.read_csv('../TestData.csv')
