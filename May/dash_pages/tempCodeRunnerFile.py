asset_classes = ['Investment Cash & Short Term Investments', 'Loans']

client_data = df[df["Asset Class"].isin(asset_classes)]
#print(client_data)
group_by_asset_class = client_data\
.groupby(['Asset Class','CCY'], as_index=False)\
.agg({'Nominal Amount (USD)':'sum'})
print(group_by_asset_class)