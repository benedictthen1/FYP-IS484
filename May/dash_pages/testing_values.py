import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
from datetime import date, timedelta   

# def format(val):
#     a = pd.to_datetime(val, errors='coerce', cache=False).strftime('%m/%d/%Y')
#     try:
#         date_time_obj = datetime.datetime.strptime(a, '%d/%m/%Y')
#     except:
#         date_time_obj = datetime.datetime.strptime(a, '%m/%d/%Y')
#     return date_time_obj.date()

# df = pd.read_csv('../Client.csv')
# position_date = df['Position As of Date'].loc[0]
# df[['Position As of Date','Maturity','Next Call Date']] = df[['Position As of Date','Maturity','Next Call Date']].apply(pd.to_datetime)
# #print(df[['Position As of Date','Maturity','Next Call Date']])

# ex_div_date = df['Dividend EX Date'].loc[50]
# print(ex_div_date)
# # df['Dividend EX Date1'] = df['Dividend EX Date'].dt.strftime('%m/%d/%Y')
# # print(df.dtypes)

# # df['Dividend EX Date1'] = pd.to_datetime(df['Dividend EX Date1'])
# # print(df.dtypes)

# # df['Dividend EX Date'] = df['Dividend EX Date'].apply(lambda x: format(x))

# df['Dividend EX Date'] = pd.to_datetime(df['Dividend EX Date'], errors='coerce').dt.strftime('%m/%d/%Y')
# df['Dividend EX Date']= pd.to_datetime(df['Dividend EX Date'])
# # print(df['Dividend EX Date'].head())
# # ex_div_date = df['Dividend EX Date'].loc[50]
# # position_date = df['Position As of Date'].loc[0]
# # maturity_date = df['Next Call Date'].loc[53]
# # print(ex_div_date, position_date,maturity_date)

# # not_null_boolean = pd.notnull(df["Next Call Date"])
# # next_call_df = df[not_null_boolean]
# # print(df["Position As of Date"].head())


# Eq_FI = ["EQUITIES","FIXED INCOME"]
# df = df[df["Asset Class"].isin(Eq_FI)]
# common_columns = ["Client Name","Base Number","Position As of Date","Asset Class","Asset Sub Class","Name","Ticker","CCY","Nominal Units","Nominal Amount (CCY)",
# "Nominal Amount (USD)","Current Price","Closing Price","Average Cost","% Change from Avg Cost","1d %","5d %","1m %","6m %","12m %","YTD%",
# "Sector","Country (Domicile)","Region (Largest Revenue)"]
# equities_columns = ["Citi rating","Citi TARGET","% to target","Market Consensus","12M Div Yield (%)",
# "P/E Ratio","P/B Ratio","EPS (Current Year)","EPS (Next Year)","YoY EPS Growth (%)","50D MA","200D MA","Profit Margin",
# "Company Description"]
# equities_date = ["Dividend EX Date"]
# # "CoCo Action","Duration" are left out in fixed_income_columns because Client.csv do not have them
# fixed_income_columns = ["Rank","Moodys R","S&P R","Fitch","Coupon","YTC","YTM","Coupon type","Issue Date"]
# fixed_income_date = ["Maturity","Next Call Date"]
# reminders_columns = common_columns + equities_columns + fixed_income_columns + equities_date + fixed_income_date
# reminders_columns_without_dates = common_columns + equities_columns + fixed_income_columns
# print(len(reminders_columns))

# df = df[reminders_columns]
# print(df.shape)

# # client_data = df.loc[df["Client Name"] == 'SR250824955']
# client_data = df.loc[df["Client Name"] == 'SR004022615']

# # latest_date = client_data["Position As of Date"].max()
# # latest_client_data = client_data[client_data['Position As of Date'] == latest_date]
# #print(latest_client_data)

# # melted_df = latest_client_data.melt(id_vars=reminders_columns_without_dates,var_name="Reminder Type",value_name="Date")
# melted_df = client_data.melt(id_vars=reminders_columns_without_dates,var_name="Reminder Type",value_name="Date")
# print(melted_df)
# # melted_df.to_csv (r'C:\Users\User\Desktop\melted_df_not_latest.csv', index = False, header=True)

# today = date.today()
# next_week_date =  today + timedelta(weeks=4) # change time accordingly here
# # last_week_date =  today - timedelta(weeks=8)

# df_next_week = melted_df[(melted_df['Date'].dt.date <= next_week_date) & (melted_df['Date'].dt.date >= today)]
# # df_last_week = df[(df['Dividend EX Date'].dt.date >= last_week_date) & (df['Dividend EX Date'].dt.date <= today)]
# count = len(df_next_week.index)
# print(today)
# print(next_week_date)
# print(df_next_week)
# print(count)

# all_list = ["ALTERNATIVES",]
# Eq_FI = ["EQUITIES","FIXED INCOME"]

# if any(i in all_list for i in Eq_FI):
#     print("exists")
# else:
#     print("not exist")

# df = pd.DataFrame({
#     'brand': ['Yum Yum', 'Yum Yum', 'Indomie', 'Indomie', 'Indomie'],
#     'style': ['cup', 'cup', 'cup', 'pack', 'pack'],
#     'rating': [4, 4, 3.5, 15, 5]
# })

# print(df)
# df = df.drop_duplicates()
# print(df)
df = pd.read_csv('../Client.csv')
risk_df = pd.read_csv('../RiskLevelsAllocation.csv')

df['Position As of Date'] = pd.to_datetime(df['Position As of Date'], errors='coerce').dt.strftime('%d/%m/%Y')
df['Position As of Date']= pd.to_datetime(df['Position As of Date'])
df['Maturity'] = pd.to_datetime(df['Maturity'], errors='coerce').dt.strftime('%d/%m/%Y')
df['Maturity']= pd.to_datetime(df['Maturity'])
df['Next Call Date'] = pd.to_datetime(df['Next Call Date'], errors='coerce').dt.strftime('%d/%m/%Y')
df['Next Call Date']= pd.to_datetime(df['Next Call Date'])
df['Dividend EX Date'] = pd.to_datetime(df['Dividend EX Date'], errors='coerce').dt.strftime('%m/%d/%Y')
df['Dividend EX Date']= pd.to_datetime(df['Dividend EX Date'])

latest_date = df["Position As of Date"].max()
latest_client_data = df[df['Position As of Date'] == latest_date]

# Eq_FI = ["EQUITIES","FIXED INCOME"]
# client_data = latest_client_data[latest_client_data["Asset Class"].isin(Eq_FI)]

# common_columns = ["Client Name","Base Number","Position As of Date","Asset Class","Asset Sub Class","Name","Ticker","CCY","Nominal Units","Nominal Amount (CCY)",
# "Nominal Amount (USD)","Current Price","Closing Price","Average Cost","% Change from Avg Cost","1d %","5d %","1m %","6m %","12m %","YTD%",
# "Sector","Country (Domicile)","Region (Largest Revenue)"]
# equities_columns = ["Citi rating","Citi TARGET","% to target","Market Consensus","12M Div Yield (%)",
# "P/E Ratio","P/B Ratio","EPS (Current Year)","EPS (Next Year)","YoY EPS Growth (%)","50D MA","200D MA","Profit Margin",
# "Company Description"]
# equities_date = ["Dividend EX Date"]
# # "CoCo Action","Duration" are left out in fixed_income_columns because Client.csv do not have them
# fixed_income_columns = ["Rank","Moodys R","S&P R","Fitch","Coupon","YTC","YTM","Coupon type","Issue Date"]
# fixed_income_date = ["Maturity","Next Call Date"]
# reminders_columns = common_columns + equities_columns + fixed_income_columns + equities_date + fixed_income_date
# reminders_columns_without_dates = common_columns + equities_columns + fixed_income_columns

# reminder_df = client_data[reminders_columns]

# melted_reminder_df = reminder_df.melt(id_vars=reminders_columns_without_dates,var_name="Reminder Type",value_name="DateTime")
# melted_reminder_df['Date'] = melted_reminder_df['DateTime'].dt.date

# melted_reminder_df = melted_reminder_df.drop_duplicates()
# today = date.today()
# next_reminder_date =  today + timedelta(weeks=52) # change time accordingly here
# # time_string = "1 Year" # change accordingly here also

# df_next_reminder = melted_reminder_df[(melted_reminder_df['Date'] <= next_reminder_date) & (melted_reminder_df['Date'] >= today)]
# # df_all_reminder = melted_reminder_df[melted_reminder_df['Date'] >= today]
# # df_next_reminder = df_next_reminder[["Name","Reminder Type","Date"]]
# # print(df_next_reminder)
# df_next_reminder = df_next_reminder.drop_duplicates()
# print(df_next_reminder["Date"].unique())
# print(len(df_next_reminder["Client Name"].unique()))
# df_overdue_reminder = melted_reminder_df[melted_reminder_df['Date'] <= today]

# df_overdue_reminder = df_overdue_reminder.drop_duplicates()
# print(len(df_overdue_reminder["Client Name"].unique()))


################ Profit/Loss Breakdown ####################

Eq_FI = ["EQUITIES","FIXED INCOME"]
Eq_FI_df = latest_client_data[latest_client_data["Asset Class"].isin(Eq_FI)]
Alt_df = latest_client_data[latest_client_data["Asset Class"]=="ALTERNATIVE INVESTMENTS"]

Eq_FI_df = Eq_FI_df[["Client Name","Base Number","Asset Class","Estimated Profit/Loss"]]
Alt_df = Alt_df[["Client Name","Base Number","Asset Class","Distribution Amount","Estimated Profit/Loss"]]

Alt_Distribution_boolean = pd.notnull(Alt_df["Distribution Amount"])
Alt_Distribution_df = Alt_df[Alt_Distribution_boolean]
#print(Alt_Distribution_df.tail())
Alt_Distribution_df = Alt_Distribution_df[["Client Name","Base Number","Asset Class","Distribution Amount"]][Alt_Distribution_df["Distribution Amount"]!=0]
#print(Alt_Distribution_df.tail())
Alt_Distribution_df.rename(columns={"Distribution Amount": "Estimated Profit/Loss"}, inplace=True)
#print(Eq_FI_df.shape)
#print(Alt_Distribution_df.shape)

Alt_Profit_Loss_boolean = pd.isnull(Alt_df["Distribution Amount"])
Alt_Profit_Loss_NA_df = Alt_df[["Client Name","Base Number","Asset Class","Estimated Profit/Loss"]][Alt_Profit_Loss_boolean]
#print(Alt_Profit_Loss_NA_df.shape)
Alt_Profit_Loss_zero_df = Alt_df[["Client Name","Base Number","Asset Class","Estimated Profit/Loss"]][Alt_df["Distribution Amount"]==0]
#print(Alt_Profit_Loss_zero_df.shape)

frames = [Eq_FI_df,Alt_Distribution_df,Alt_Profit_Loss_NA_df,Alt_Profit_Loss_zero_df]
Profit_Loss_df = pd.concat(frames,ignore_index=True)
#print(Profit_Loss_df.tail())
#print(Profit_Loss_df.shape)

# decimals = 3
# Profit_Loss_df['Estimated Profit/Loss'] = Profit_Loss_df['Estimated Profit/Loss'].apply(lambda x: round(x, decimals))
# #print(Profit_Loss_df.head())
# total_profit_loss = Profit_Loss_df['Estimated Profit/Loss'].sum()

group_by_PL_asset_class = Profit_Loss_df\
.groupby(['Client Name'], as_index=False)\
.agg({'Estimated Profit/Loss':'sum'})

print(group_by_PL_asset_class)
negative_client_count = sum(n < 0 for n in group_by_PL_asset_class['Estimated Profit/Loss'].values.flatten())
print(negative_client_count)

a = [1,2,3,None,(),[],]
print('length of a:',len(a))

L = [2e-04,'a',False,87]
T = (6.22, 'boy',True,554)
for i in range(len(L)):
    if L[i]:
        L[i] = L[i] + T[i]
        print(L)
    # else:
    #     T[i] = L[i] + T[i]
    #     break
print(L)

w = "hello"
v = ('a','e','i','o','u')
print([x for x in w if x in v])

value = [1,2,3,4]
data = 0
try:
    data = value[-4]
except IndexError:
    print("IndexError ",end = " ")
except:
    print("Error ",end= " ")
finally:
    print("Hello world ", end=" ")

data = 10
try:
    data = data/0
except ZeroDivisionError:
    print("ZeroDivisionError ",end = " ")
finally:
    print("Hello world again ")

columns_bef_safe_index =\
['host_response_rate',
 'host_acceptance_rate',
 'host_is_superhost',
 'host_listings_count',
 'accommodates',
 'bathrooms',
 'price',
 'minimum_nights',
 'review_scores_rating',
 'reviews_per_month',
 'price_log',
 'a few days or more',
 'within a day',
 'within a few hours',
 'within an hour',
 'Bayview',
 'Bernal Heights',
 'Castro/Upper Market',
 'Chinatown',
 'Crocker Amazon',
 'Diamond Heights',
 'Downtown/Civic Center',
 'Excelsior',
 'Financial District',
 'Glen Park',
 'Golden Gate Park',
 'Haight Ashbury',
 'Inner Richmond',
 'Inner Sunset',
 'Lakeshore',
 'Marina',
 'Mission',
 'Nob Hill',
 'Noe Valley',
 'North Beach',
 'Ocean View',
 'Outer Mission',
 'Outer Richmond',
 'Outer Sunset',
 'Pacific Heights',
 'Parkside',
 'Potrero Hill',
 'Presidio',
 'Presidio Heights',
 'Russian Hill',
 'Seacliff',
 'South of Market',
 'Treasure Island/YBI',
 'Twin Peaks',
 'Visitacion Valley',
 'West of Twin Peaks',
 'Western Addition',
 'Boat',
 'Casa particular',
 'Earth house',
 'Entire apartment',
 'Entire bungalow',
 'Entire cabin',
 'Entire condominium',
 'Entire cottage',
 'Entire floor',
 'Entire guest suite',
 'Entire guesthouse',
 'Entire house',
 'Entire in-law',
 'Entire loft',
 'Entire place',
 'Entire serviced apartment',
 'Entire townhouse',
 'Entire villa',
 'Private room (Property Type)',
 'Private room in apartment',
 'Private room in bed and breakfast',
 'Private room in bungalow',
 'Private room in cabin',
 'Private room in castle',
 'Private room in condominium',
 'Private room in cottage',
 'Private room in earth house',
 'Private room in guest suite',
 'Private room in guesthouse',
 'Private room in hostel',
 'Private room in house',
 'Private room in hut',
 'Private room in loft',
 'Private room in resort',
 'Private room in serviced apartment',
 'Private room in townhouse',
 'Private room in villa',
 'Room in aparthotel',
 'Room in bed and breakfast',
 'Room in boutique hotel',
 'Room in hostel',
 'Room in hotel',
 'Room in serviced apartment',
 'Shared room in apartment',
 'Shared room in bed and breakfast',
 'Shared room in boutique hotel',
 'Shared room in bungalow',
 'Shared room in condominium',
 'Shared room in hostel',
 'Shared room in house',
 'Shared room in loft',
 'Shared room in townhouse',
 'Shared room in villa',
 'Tiny house',
 'Entire home/apt',
 'Hotel room',
 'Private room',
 'Shared room',
 'air conditioning',
 'alarm system',
 'baby bath',
 'baby monitor',
 'babysitter recommendations',
 'baking sheet',
 'barbecue utensils',
 'bathroom essentials',
 'bathtub',
 'bbq grill',
 'beach essentials',
 'beachfront',
 'bed linens',
 'bedroom comforts',
 'bread maker',
 'breakfast',
 'breakfast bar',
 'building staff',
 'cable tv',
 'carbon monoxide alarm',
 'changing table',
 'children\\u2019s books and toys',
 'children\\u2019s dinnerware',
 'cleaning before checkout',
 'coffee maker',
 'cooking basics',
 'crib',
 'desk',
 'dishes and silverware',
 'dishwasher',
 'dryer',
 'dual vanity',
 'elevator',
 'essentials',
 'ethernet connection',
 'ev charger',
 'extra pillows and blankets',
 'fire extinguisher',
 'fireplace guards',
 'first aid kit',
 'free parking on premises',
 'free street parking',
 'full kitchen',
 'game console',
 'garden or backyard',
 'gas fireplace',
 'gym',
 'hair dryer',
 'hangers',
 'heating',
 'high chair',
 'host greets you',
 'hot tub',
 'hot water',
 'indoor fireplace',
 'iron',
 'ironing board',
 'jetted tub',
 'keypad',
 'kitchen',
 'kitchenette',
 'lake access',
 'laptop-friendly workspace',
 'lock on bedroom door',
 'lockbox',
 'long term stays allowed',
 'luggage dropoff allowed',
 'microwave',
 'mini fridge',
 'natural gas barbeque',
 'office',
 'outlet covers',
 'oven',
 'pack \\u2019n play/travel crib',
 'paid parking off premises',
 'paid parking on premises',
 'patio or balcony',
 'pets allowed',
 'piano',
 'pocket wifi',
 'pool',
 'portable air conditioning',
 'private entrance',
 'private hot tub',
 'private living room',
 'refrigerator',
 'room-darkening shades',
 'security cameras',
 'self check-in',
 'shampoo',
 'shared hot tub',
 'shower gel',
 'single level home',
 'ski-in/ski-out',
 'smart home technology',
 'smart lock',
 'smart tv',
 'smoke alarm',
 'smoking allowed',
 'sonos sound system',
 'stair gates',
 'stand alone bathtub',
 'stand alone rain shower',
 'stove',
 'suitable for events',
 'table corner guards',
 'terrace',
 'tv',
 'walk in closet',
 'washer',
 'waterfront',
 'wet bar',
 'wifi',
 'window guards',
 'wine cooler']

columns_aft_safe_index = \
['host_response_rate',
 'host_acceptance_rate',
 'host_is_superhost',
 'host_listings_count',
 'accommodates',
 'bathrooms',
 'price',
 'minimum_nights',
 'review_scores_rating',
 'reviews_per_month',
 'price_log',
 'sentiment_compound',
 'SafeIndex_Score',
 'wifi',
 'heating',
 'smoke alarm',
 'essentials',
 'hair dryer',
 'tv',
 'kitchen',
 'hot water',
 'fire extinguisher',
 'washer',
 'coffee maker',
 'refrigerator',
 'free street parking',
 'first aid kit',
 'bed linens',
 'oven',
 'private entrance',
 'dishwasher',
 'cable tv',
 'luggage dropoff allowed',
 'long term stays allowed',
 'garden or backyard',
 'patio or balcony',
 'lock on bedroom door',
 'lockbox',
 'keypad',
 'free parking on premises',
 'elevator',
 'bathtub',
 'indoor fireplace',
 'paid parking off premises',
 'air conditioning',
 "pack 'n play/travel crib",
 'bbq grill',
 'breakfast',
 'host greets you',
 'room-darkening shades',
 "children's books and toys",
 'shower gel',
 'single level home',
 'paid parking on premises',
 'building staff',
 'ethernet connection',
 'smart lock',
 'hot tub',
 'private living room',
 'high chair',
 'baking sheet',
 'bathroom essentials',
 'cleaning before checkout',
 'crib',
 'babysitter recommendations',
 'game console',
 'stair gates',
 'fireplace guards',
 'pool',
 'pocket wifi',
 'changing table',
 'beach essentials',
 'window guards',
 'ev charger',
 'beachfront',
 '-',
 'a few days or more',
 'within a day',
 'within a few hours',
 'within an hour',
 'Bayview',
 'Bernal Heights',
 'Castro/Upper Market',
 'Chinatown',
 'Crocker Amazon',
 'Diamond Heights',
 'Downtown/Civic Center',
 'Excelsior',
 'Financial District',
 'Glen Park',
 'Haight Ashbury',
 'Inner Richmond',
 'Inner Sunset',
 'Lakeshore',
 'Marina',
 'Mission',
 'Nob Hill',
 'Noe Valley',
 'North Beach',
 'Ocean View',
 'Outer Mission',
 'Outer Richmond',
 'Outer Sunset',
 'Pacific Heights',
 'Parkside',
 'Potrero Hill',
 'Presidio Heights',
 'Russian Hill',
 'Seacliff',
 'South of Market',
 'Twin Peaks',
 'Visitacion Valley',
 'West of Twin Peaks',
 'Western Addition',
 'Earth house',
 'Entire apartment',
 'Entire bungalow',
 'Entire cabin',
 'Entire condominium',
 'Entire cottage',
 'Entire floor',
 'Entire guest suite',
 'Entire guesthouse',
 'Entire house',
 'Entire in-law',
 'Entire loft',
 'Entire place',
 'Entire serviced apartment',
 'Entire townhouse',
 'Private room',
 'Private room in apartment',
 'Private room in bed and breakfast',
 'Private room in bungalow',
 'Private room in cabin',
 'Private room in castle',
 'Private room in condominium',
 'Private room in cottage',
 'Private room in earth house',
 'Private room in guest suite',
 'Private room in guesthouse',
 'Private room in hostel',
 'Private room in house',
 'Private room in hut',
 'Private room in loft',
 'Private room in resort',
 'Private room in serviced apartment',
 'Private room in townhouse',
 'Private room in villa',
 'Room in aparthotel',
 'Room in bed and breakfast',
 'Room in boutique hotel',
 'Room in hostel',
 'Room in hotel',
 'Room in serviced apartment',
 'Shared room in apartment',
 'Shared room in bed and breakfast',
 'Shared room in boutique hotel',
 'Shared room in bungalow',
 'Shared room in hostel',
 'Shared room in house',
 'Shared room in loft',
 'Shared room in townhouse',
 'Shared room in villa',
 'Tiny house',
 'Entire home/apt',
 'Hotel room',
 'Private room (Room Type)',
 'Shared room']

columns_not_in_aft_safe_index = [x for x in columns_bef_safe_index if x not in columns_aft_safe_index]
print("length of columns_bef_safe_index:",len(columns_bef_safe_index))
print("length of columns_aft_safe_index:",len(columns_aft_safe_index))
print("columns_not_in_aft_safe_index:",columns_not_in_aft_safe_index)
print("length of columns_not_in_aft_safe_index:",len(columns_not_in_aft_safe_index))