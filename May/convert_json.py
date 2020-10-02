print("Hello world")
import json
import pandas as pd 
import time
import numpy as np

# json_data = pd.read_json("SamplePositionsFromLJSpreadsheet.json",lines=True)
# json_data.head()

with open("SamplePositionsFromLJSpreadsheet.json") as f:
    read_content = json.load(f)

read_content.head()

