
import os
import json
import re
import pandas as pd

from IPython.display import Javascript

from ezaggrid import AgGrid

df = pd.read_csv('TestData.csv',encoding='latin1')

ag = AgGrid(grid_data=df[:],

            css_rules=None,
            width=850,
            height=500,
            quick_filter=False,
            export_csv=False,
            export_excel=False,
            implicit_col_defs=False,
            theme='ag-theme-fresh',
            )
ag.show()