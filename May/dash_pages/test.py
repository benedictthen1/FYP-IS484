
import pandas as pd

import pandas_datareader.data as web
import datetime

df = pd.read_csv('../TestDataManipulated.csv')

client_data = df[df["Client Name"]=="SR004022615"]
client_data["Asset Class"][client_data["Asset Class"]!="Loans"] = "Others"
#print(client_data["Asset Class"].unique())
group_by_asset_class = client_data\
.groupby(['Position As of Date','Asset Class'], as_index=False)\
.agg({'Nominal Amount (USD)':'sum'})


print(group_by_asset_class)
