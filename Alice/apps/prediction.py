import pandas as pd
from app import app
import pathlib
import dash
import dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
# import datetime as dt
# from dt import date
from datetime import datetime, timedelta 
today_date =datetime.today().strftime('%Y-%m-%d')

################# Import: Yfinance #########################
import yfinance as yf
from yahoofinancials import YahooFinancials
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np

################# Data Processing #########################
# Ticker list
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

df = pd.read_csv(DATA_PATH.joinpath("Client.csv"),encoding='latin1',dtype='unicode')
# df = pd.read_csv('Client.csv',dtype='unicode')
df = df[df['Asset Class']=='EQUITIES']
final_df = df[df['Asset Sub Class'] == 'Common Stocks']
tickers = final_df["Ticker"].unique()
# Interval list
# intervals = ['1M','6M','1.5Y']
# Function to validate dates
def validate(date_text):
    if(date_text != None):
        try:
            if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d'):
                raise ValueError
            return True
        except ValueError:
            return False

# Prediction Functions

def get_linearprediction(ticker_name,start_date,end_date, future_period):    
    import datetime
    from datetime import timedelta, date
    #Download the data from Yfinance
    ticker = yf.Ticker(ticker_name)
    ticker_historical = ticker.history(start= start_date, end= end_date)
    ticker_historical #Display the data

    name = ticker_name
    filename = "%s.csv" % name
    #Save data into a CSV file
    ticker_historical.to_csv(filename)
    
    #df.to_csv(filename)
    df = pd.read_csv(filename)

    df_days = df[['Date']]
    # print(df)

    # A variable for predicting 'n' days out into the future #'n=30' days

    # Get the Adjusted Close Price 
    df = df[['Close']] 


    #Create another column (the target ) shifted 'n' units up
    df['Prediction'] = df[['Close']].shift(-future_period)
    #print the new data set
    #print(df.tail())


    ### Create the independent data set (X)  #######
    # Convert the dataframe to a numpy array
    X = np.array(df.drop(['Prediction'],1))

    #Remove the last '30' rows
    X = X[:-future_period]
    #print(X)

    ### Create the dependent data set (y)  #####
    # Convert the dataframe to a numpy array 
    y = np.array(df['Prediction'])
    # Get all of the y values except the last '30' rows
    y = y[:-future_period]
    #print(y)

    # Split the data into 80% training and 20% testing
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2)


    # Create and train the Linear Regression  Model
    lr = LinearRegression()
    # Train the model
    lr.fit(x_train, y_train)

    # Testing Model: Score returns the coefficient of determination R^2 of the prediction. 
    # The best possible score is 1.0
    lr_confidence = lr.score(x_test, y_test)
    #print("lr confidence: ", lr_confidence)

    # df['Linear Regression Accuracy'] = lr_confidence
    # Set x_forecast equal to the last 30 rows of the original data set from Adj. Close column
    x_forecast = np.array(df.drop(['Prediction'],1))[-future_period:]
    #print(x_forecast)

    #Print linear regression model predictions for the next '30' days
    lr_prediction = lr.predict(x_forecast)
    #print(lr_prediction)

    df['Date'] = df_days
    df

    # A variable for predicting 'n' days out into the future

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    def daterange(date1, date2):
        for n in range(int ((date2 - date1).days)+1):
            yield date1 + timedelta(n)
    for lr in lr_prediction:
        end_date +=  timedelta(days=1)
        #print(end_date)
        weekdays = [5,6]
        df = df.append({'Date': end_date, 'LR Prediction': lr}, ignore_index = True)  
    df = df[['Date', 'Close', 'LR Prediction']]
    df["Price"] = df["Close"]
    df["Price"] = df["Price"].fillna(df["LR Prediction"])
    return df

def get_RBFSVMPrediction(ticker_name,start_date,end_date,future_period):
    import datetime
    from datetime import timedelta, date
    #Download the data from Yfinance
    ticker = yf.Ticker(ticker_name)
    ticker_historical = ticker.history(start= start_date, end= end_date)
    ticker_historical #Display the data

    
    name = ticker_name
    filename = "%s.csv" % name
    #Save data into a CSV file
    ticker_historical.to_csv(filename)
    
    #df.to_csv(filename)
    df = pd.read_csv(filename)

    df_days = df[['Date']]
    # print(df)

    # A variable for predicting 'n' days out into the future #'n=30' days

    # Get the Adjusted Close Price 
    df = df[['Close']] 


    #Create another column (the target ) shifted 'n' units up
    df['Prediction'] = df[['Close']].shift(-future_period)
    #print the new data set
    #print(df.tail())


    ### Create the independent data set (X)  #######
    # Convert the dataframe to a numpy array
    X = np.array(df.drop(['Prediction'],1))

    #Remove the last '30' rows
    X = X[:-future_period]
    #print(X)

    ### Create the dependent data set (y)  #####
    # Convert the dataframe to a numpy array 
    y = np.array(df['Prediction'])
    # Get all of the y values except the last '30' rows
    y = y[:-future_period]
    #print(y)

    # Split the data into 80% training and 20% testing
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        
    # Create and train the Support Vector Machine (Regressor) 
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1) 
    svr_rbf.fit(x_train, y_train)

    # Testing Model: Score returns the coefficient of determination R^2 of the prediction. 
    # The best possible score is 1.0
    svm_confidence = svr_rbf.score(x_test, y_test)
    #print("svm confidence: ", svm_confidence)


    # df['Linear Regression Accuracy'] = lr_confidence
    # Set x_forecast equal to the last 30 rows of the original data set from Adj. Close column
    x_forecast = np.array(df.drop(['Prediction'],1))[-future_period:]
    #print(x_forecast)

    # Print support vector regressor model predictions for the next '30' days
    svm_prediction = svr_rbf.predict(x_forecast)
    #print(svm_prediction)


    df['Date'] = df_days
    

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    def daterange(date1, date2):
        for n in range(int ((date2 - date1).days)+1):
            yield date1 + timedelta(n)

    for svm in svm_prediction:
        end_date +=  timedelta(days=1)
        #print(end_date)
        weekdays = [5,6]
    #     for dt in daterange(start_date, end_date):
    #         if dt.weekday() not in weekdays:                    # to print only the weekdates
                #date = dt.strftime("%Y-%m-%d")

        df = df.append({'Date': end_date, 'RBF SVMR Prediction': svm}, ignore_index = True)    
        
    df = df[['Date', 'Close', 'RBF SVMR Prediction']]
    df["Price"] = df["Close"]
    df["Price"] = df["Price"].fillna(df["RBF SVMR Prediction"])   

    return df

def get_LinearSVMPrediction(ticker_name,start_date,end_date,future_period):
    import datetime
    from datetime import timedelta, date
    
    
    #Download the data from Yfinance
    ticker = yf.Ticker(ticker_name)
    
    ticker_historical = ticker.history(start= start_date, end= end_date)
    ticker_historical #Display the data

    
    name = ticker_name
    filename = "%s.csv" % name
    #Save data into a CSV file
    ticker_historical.to_csv(filename)
    
    #df.to_csv(filename)
    df = pd.read_csv(filename)

    df_days = df[['Date']]
    # print(df)

    # A variable for predicting 'n' days out into the future #'n=30' days

    # Get the Adjusted Close Price 
    df = df[['Close']] 


    #Create another column (the target ) shifted 'n' units up
    df['Prediction'] = df[['Close']].shift(-future_period)
    #print the new data set
    #print(df.tail())


    ### Create the independent data set (X)  #######
    # Convert the dataframe to a numpy array
    X = np.array(df.drop(['Prediction'],1))

    #Remove the last '30' rows
    X = X[:-future_period]
    #print(X)

    ### Create the dependent data set (y)  #####
    # Convert the dataframe to a numpy array 
    y = np.array(df['Prediction'])
    # Get all of the y values except the last '30' rows
    y = y[:-future_period]
    #print(y)

    # Split the data into 80% training and 20% testing
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        
    # Create and train the Support Vector Machine (Regressor) 
    svr_lin = SVR(kernel='linear', C=1e3, gamma=0.1) 
    svr_lin.fit(x_train, y_train)

    # Testing Model: Score returns the coefficient of determination R^2 of the prediction. 
    # The best possible score is 1.0
    svm_confidence = svr_lin.score(x_test, y_test)
    #print("svm confidence: ", svm_confidence)


    # df['Linear Regression Accuracy'] = lr_confidence
    # Set x_forecast equal to the last 30 rows of the original data set from Adj. Close column
    x_forecast = np.array(df.drop(['Prediction'],1))[-future_period:]
    #print(x_forecast)

    # Print support vector regressor model predictions for the next '30' days
    svm_prediction = svr_lin.predict(x_forecast)
    #print(svm_prediction)


    df['Date'] = df_days
    

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    def daterange(date1, date2):
        for n in range(int ((date2 - date1).days)+1):
            yield date1 + timedelta(n)

    for svm in svm_prediction:
        end_date +=  timedelta(days=1)
        #print(end_date)
        weekdays = [5,6]
    #     for dt in daterange(start_date, end_date):
    #         if dt.weekday() not in weekdays:                    # to print only the weekdates
                #date = dt.strftime("%Y-%m-%d")

        df = df.append({'Date': end_date, 'LSVMR Prediction': svm}, ignore_index = True)    
        
    df = df[['Date', 'Close', 'LSVMR Prediction']]
    df["Price"] = df["Close"]
    df["Price"] = df["Price"].fillna(df["LSVMR Prediction"])       

    return df

def get_performance(ticker_name,start_date,end_date, future_period):    
    import datetime
    from datetime import timedelta, date

    #Download the data from Yfinance
    ticker = yf.Ticker(ticker_name)
    
    ticker_historical = ticker.history(start= start_date, end= end_date)
    ticker_historical #Display the data

    
    name = ticker_name
    filename = "%s.csv" % name
    #Save data into a CSV file
    ticker_historical.to_csv(filename)
    
    #df.to_csv(filename)
    df = pd.read_csv(filename)

    df_days = df[['Date']]
    # print(df)

    # A variable for predicting 'n' days out into the future #'n=30' days

    # Get the Adjusted Close Price 
    df = df[['Close']] 


    #Create another column (the target ) shifted 'n' units up
    df['Prediction'] = df[['Close']].shift(-future_period)
    #print the new data set
    #print(df.tail())

    ### Create the independent data set (X)  #######
    # Convert the dataframe to a numpy array
    X = np.array(df.drop(['Prediction'],1))

    #Remove the last '30' rows
    X = X[:-future_period]
    #print(X)

    ### Create the dependent data set (y)  #####
    # Convert the dataframe to a numpy array 
    y = np.array(df['Prediction'])
    # Get all of the y values except the last '30' rows
    y = y[:-future_period]
    #print(y)

    # Split the data into 80% training and 20% testing
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
     # Create and train the Linear Regression  Model
    lr = LinearRegression()
    # Train the model
    lr.fit(x_train, y_train)

    # Testing Model: Score returns the coefficient of determination R^2 of the prediction. 
    # The best possible score is 1.0
    lr_confidence = lr.score(x_test, y_test)
    #print("lr confidence: ", lr_confidence)

    # df['Linear Regression Accuracy'] = lr_confidence
    # Set x_forecast equal to the last 30 rows of the original data set from Adj. Close column
    x_forecast = np.array(df.drop(['Prediction'],1))[-future_period:]
    #print(x_forecast)

    #Print linear regression model predictions for the next '30' days
    lr_prediction = lr.predict(x_forecast)
    #print(lr_prediction)
        
    # Create and train the Support Vector Machine (Regressor) 
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1) 
    svr_rbf.fit(x_train, y_train)

    # Testing Model: Score returns the coefficient of determination R^2 of the prediction. 
    # The best possible score is 1.0
    rbf_svm_confidence = svr_rbf.score(x_test, y_test)
    #print("svm confidence: ", svm_confidence)
    

    # df['Linear Regression Accuracy'] = lr_confidence
    # Set x_forecast equal to the last 30 rows of the original data set from Adj. Close column
    x_forecast = np.array(df.drop(['Prediction'],1))[-future_period:]
    #print(x_forecast)

    # Print support vector regressor model predictions for the next '30' days
    rbf_svm_prediction = svr_rbf.predict(x_forecast)
    #print(svm_prediction)
    
    
     # Create and train the Support Vector Machine (Regressor) 
    svr_lin = SVR(kernel='linear', C=1e3, gamma=0.1) 
    svr_lin.fit(x_train, y_train)

    # Testing Model: Score returns the coefficient of determination R^2 of the prediction. 
    # The best possible score is 1.0
    lin_svm_confidence = svr_lin.score(x_test, y_test)
    #print("svm confidence: ", svm_confidence)


    # df['Linear Regression Accuracy'] = lr_confidence
    # Set x_forecast equal to the last 30 rows of the original data set from Adj. Close column
    x_forecast = np.array(df.drop(['Prediction'],1))[-future_period:]
    #print(x_forecast)

    # Print support vector regressor model predictions for the next '30' days
    lin_svm_prediction = svr_lin.predict(x_forecast)
    #print(svm_prediction)
    
    
     # Create and train the Support Vector Machine (Regressor) 
    svr_poly = SVR(kernel='poly', C=1e3, gamma=0.1) 
    svr_poly.fit(x_train, y_train)

    # Testing Model: Score returns the coefficient of determination R^2 of the prediction. 
    # The best possible score is 1.0

    x_forecast = np.array(df.drop(['Prediction'],1))[-future_period:]

    Accuracy = {'LR Prediction': [lr_confidence], 
            'RBF SVMR Prediction': [rbf_svm_confidence],
            'LSVMR Prediction': [lin_svm_confidence]}
    
    df = pd.DataFrame(Accuracy, columns = ['LR Prediction', 'RBF SVMR Prediction', 'LSVMR Prediction'])
    
    return df
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Chart Function
def generate_charts(model_df):

    return dcc.Graph(style={
        'height': '300px',
        'box-shadow': '2px 2px 2px grey'
        },
    figure = px.line(model_df, x="Date", y=[model_df.columns[1],model_df.columns[2]],
    # text = model_df.columns[3], 
    color_discrete_sequence=['#003B70', 'crimson'],title=model_df.columns[2] + " Chart").update_layout(font={'family': 'verdana','size':8},
    legend={'font':{'size':7}, 'title':'Price'},plot_bgcolor="white",margin=dict(l=100, r=50, t=50, b=50, pad=10),
    yaxis_title='Price(USD)').update_traces(
            textposition="top center",
            mode = 'lines+markers',
            # marker_color = '#1E3F66', 
            texttemplate = "%{text:.2f}").update_xaxes(
                showspikes=True,linewidth=0.5, linecolor='Grey', gridcolor='#D3D3D3'
                ).update_yaxes(showspikes=True)
    )

app.layout = html.Div([

    ################# Row 1: Filters + Submit Button #########################   
    dbc.Row([
        # Filter 1: Ticker
        dbc.Col([
            html.Div([
            html.H6("Ticker: "),
            dcc.Dropdown(
                id='ticker_filter',
                options=[
                    {'label': ticker, 'value': ticker} for ticker in tickers
                ],
                style={'width':"100%",'padding-left':'5px'},
                value = tickers[0],
                placeholder="Filter by Ticker",
                clearable=False)
            ])
            ],width=3),

        # Filter 3: Forecast period (days)
        dbc.Col([
            html.Div([
                html.H6(["Forecast Period (days):"]),
                dcc.Input(
                    id="forecast_period", 
                    type="text",   
                    placeholder=" days",
                    value = '5',
                    style = {
                        'width':"50%",
                        "margin-left": "5px",
                        # 'marginRight': "10%",
                        'height':"32px"
                        }
                    )
            ])
            ],width=3),
       
        dbc.Col([
            html.Div([
                dbc.Button(children= "Apply", color="dark",size="sm", id="submit_btn",n_clicks=0)
            ])
        ],width=2)

    ],justify="left",style={'marginLeft': "1%", 'marginRight': "1%", 'marginTop': 20}),
    html.Br(),
    ################# Subsequent Rows: Display Outputs ######################### 
    dbc.Row([
        dbc.Col([
            html.Div([
            html.H5(children='Accuracy Ranking', 
                style={
                    'textAlign': 'center',
                    'color': 'white',
                    'box-shadow': '2px 2px 2px grey',
                    'textAlign': 'center',
                    'padding':'2.5px',
                    'color': 'white',
                    'backgroundColor': "#003B70"})
            ])
        ],width={'size':3}),
        dbc.Col([
            html.Div([
            html.H5('Stock Prediction Chart by different models', 
                style={'textAlign': 'center',
                'color': 'white',
                'box-shadow': '2px 2px 2px grey',
                'textAlign': 'center',
                'padding':'2.5px',
                'color': 'white',
                'backgroundColor': "#003B70"})
            ])
        ],width={'size':6}),
        dbc.Col([
            html.Div([
            html.H5(children='Model Description',
                style={'textAlign': 'center',
                'color': 'white',
                'box-shadow': '2px 2px 2px grey',
                'textAlign': 'center',
                'padding':'2.5px',
                'color': 'white',
                'backgroundColor': "#003B70"})
            ])
        ],width={'size':3})
    ],justify="center",style={'marginLeft': "1%", 'marginRight': "1%", 'marginTop': 0})  ,
    dbc.Row([
    ################# Col 1: 1st Accuracy Card #########################   
        dbc.Col([
            html.Div([
                html.H2(["Rank 1"],style={'textAlign': 'center','color': 'white'}),
                html.H5(["R-Square: "], style= {'color':'white'}),
                html.H5(id = "best_acc", style= {'color':'white'})
                ],
                style = {
                    "backgroundColor": "#004a8c",
                    'box-shadow': '2px 2px 2px grey',
                    'height': '300px',
                    'padding': '100px 0',
                    'text-align': 'center'
                }
                )
            ],width={'size':3}),

    ################# Col 2: 1st Line Graph #########################   
        dbc.Col([
            html.Div([ 
            html.Div(id="best_chart",style={'height':10}),   
            ])
    
        ],width={'size':6}),
    ################# Col 3: 1st Description Card #########################   
        dbc.Col([
            html.Div([
                html.H5(id="best_col",style={'textAlign': 'center','color': 'white'}),
                html.P(id = "best_desc", 
                style= {
                    'color':'white',
                    'padding-left': '20px',
                    'padding-right': '20px'
                    })
                ],
                style = {
                    "backgroundColor": "#004a8c",
                    'box-shadow': '2px 2px 2px grey',
                    'height': '300px',
                    'padding': '55px 0',
                    'text-align': 'center',
                }
                )
        ])
    ],justify="center",style={'marginLeft': "1%", 'marginRight': "1%", 'marginTop': 0,'marginBottom': "1%"}),

    dbc.Row([
    ################# Col 1: 2nd Accuracy Card #########################  
        dbc.Col([
            html.Div([
                html.H2(["Rank 2"],style={'textAlign': 'center','color': 'white'}),
                html.H5(["R-Square: "], style= {'color':'white'}),
                html.H5(id = "second_acc", style= {'color':'white'})
                ],
                style = {
                    "backgroundColor": "#346a99",
                    'box-shadow': '2px 2px 2px grey',
                    'height': '300px',
                    'padding': '100px 0',
                    'text-align': 'center'
                }
            )         
        ],width={'size':3}),
    ################# Col 2: 2nd Line Graph #########################  
        dbc.Col([
            html.Div([
            html.Div(id="second_chart",style={'height':10})   
            ])                     
        ],width={'size':6}),
    ################# Col 3: 2nd Description Card #########################  
        dbc.Col([
            html.Div([
                html.H5(id="second_col",style={'textAlign': 'center','color': 'white'}),
                html.P(id = "second_desc", 
                style= {
                    'color':'white',
                    'padding-left': '20px',
                    'padding-right': '20px'
                    })
                ],
                style = {
                    "backgroundColor": "#346a99",
                    'box-shadow': '2px 2px 2px grey',
                    'height': '300px',
                    'padding': '55px 0',
                    'text-align': 'center'
                }
                )           
        ],width={"size":3}),
    ],justify="center",style={'marginLeft': "1%", 'marginRight': "1%", 'marginTop': 0,'marginBottom': "1%"}),  

    dbc.Row([
    ################# Col 1: 3rd Accuracy Card #########################  
        dbc.Col([
            html.Div([
                html.H2(["Rank 3"],style={'textAlign': 'center','color': 'white'}),
                html.H5(["R-Square: "], style= {'color':'white'}),
                html.H5(id = "third_acc", style= {'color':'white'})
                ],
                style = {
                    "backgroundColor": "#618bb0",
                    'box-shadow': '2px 2px 2px grey',
                    'height': '300px',
                    'padding': '100px 0',
                    'text-align': 'center'
                }
            )           
        ],width={'size':3}),
    ################# Col 2: 3rd Line Graph #########################  
        dbc.Col([
            html.Div([
            html.Div(id="third_chart",style={'height':10})   
            ])
                  
        ],width={'size':6}),
    ################# Col 3: 3rd Description Card #########################  
        dbc.Col([
            html.Div([
                
                html.H5(id="third_col",style={'textAlign': 'center','color': 'white'}),
                html.P(id = "third_desc", 
                style= {
                    'color':'white',
                    'padding-left': '20px',
                    'padding-right': '20px'
                    })
                ],
                style = {
                    "backgroundColor": "#618bb0",
                    'box-shadow': '2px 2px 2px grey',
                    'height': '300px',
                    'padding': '55px 0',
                    'text-align': 'center'
                }
                )            
        ],width={"size":3}),
    ],justify="center",style={'marginLeft': "1%", 'marginRight': "1%", 'marginTop': 0,'marginBottom': "1%"})  
],style = {'backgroundColor': "#f2f2f2"})


@app.callback(
    [
    Output("best_chart", "children"),
    Output("second_chart","children"),
    Output("third_chart","children"),
    Output("best_acc","children"),
    Output("second_acc","children"),
    Output("third_acc","children"),
    Output("best_col","children"),
    Output("best_desc","children"),
    Output("second_col","children"),
    Output("second_desc","children"),
    Output("third_col","children"),
    Output("third_desc","children")
    ],
    Input('submit_btn', 'n_clicks'),
    # values to be passed upon clicking submit button
    [State('ticker_filter', 'value'),
    # State('interval','value'),
    State('forecast_period', 'value')
    ]
) 


def update_output(n_clicks,ticker_subval,period_subval):
    # Check if all 3 inputs are submitted
    errors = []
    # Lock the interval for user
    interval = 300
    # 1: Check if all inputs submitted
    if ticker_subval != "None"  and period_subval != None:
        # 2: Validate each input (except for ticker input)
        # if validate(start_subval) == False:
        #     errors.append("Invalid Start Date input")
        # if validate(end_subval) == False:
        #     errors.append("Invalid End Date input")
        period_subval = period_subval.strip()
        if period_subval.isdigit() == False:
            errors.append("Invalid Forecast Period input")
        else:
            period_subval = int(period_subval)

        # 3: If no validation error, generate relevant dataframes 
        if(errors == []):
            # changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
            # end_subval (end submitted value) is fixed at today's date
            # start_subval is computed by subtracting interval(in days) from end_subval 
            end_subval = today_date
            days = timedelta(interval)
            start_subval = datetime.strptime(end_subval,'%Y-%m-%d') - days
            start_subval = start_subval.date()
            start_subval = datetime.strftime(start_subval,'%Y-%m-%d')

            # retrieve and sort the accuracy df
            accuracy_df = get_performance(ticker_subval,start_subval,end_subval,period_subval)
            sorted_accuracy_df = accuracy_df.sort_values(0,axis = 1, ascending=False)
            sorted_accuracy_table = sorted_accuracy_df.to_dict('records')
            sorted_accuracy_table_cols = [{"name": i, "id": i} for i in sorted_accuracy_df.columns]   
            # prediction_SVR_df['RBF SVR Prediction'] = prediction_SVR_df['RBF SVR Prediction'].apply(lambda x: round(x, 4))            

            # Retrieve Column names in sorted order (Best -> Worst)
            best_col = sorted_accuracy_df.columns[0] # "LR Prediction"
            second_col = sorted_accuracy_df.columns[1] # "LSVMR Prediction"
            third_col = sorted_accuracy_df.columns[2] # "RBF SVMR Prediction Prediction"

            # Based on 3 inputs + 1 computed variable (start_subval), retrieve 3 model dfs
            LR_df = get_linearprediction(ticker_subval,start_subval,end_subval,period_subval)
            RBFSVM_df = get_RBFSVMPrediction(ticker_subval,start_subval,end_subval,period_subval)
            LRSVM_df = get_LinearSVMPrediction(ticker_subval,start_subval,end_subval,period_subval)

            #  Model descriptions for right column
            LR_desc = "Linear regression attempts to model the relationship between two variables by fitting a linear equation to observed data using explanatory and dependent variable."
            RBFSVM_desc = "Radial Basis Function is a real-valued function used in SVM models and its value only on the distance between the input and some fixed point (called as center)."
            LRSVM_desc = "Linear Regression SVM Function creates a line or a hyperplane which separates the data into classes and is a linear model for classification and regression problems."

            # Store each model df + desc according to the accuracy order of the columns in sorted accuracy df
            if best_col == "LR Prediction":
                best_model_df = LR_df 
                best_desc = LR_desc     
            elif second_col == "LR Prediction":
                second_model_df = LR_df
                second_desc = LR_desc 
            else:
                third_model_df = LR_df
                third_desc = LR_desc 

            if best_col == "LSVMR Prediction":
                best_model_df = LRSVM_df   
                best_desc = LRSVM_desc   
            elif second_col == "LSVMR Prediction":
                second_model_df = LRSVM_df
                second_desc = LRSVM_desc
            else:
                third_model_df = LRSVM_df
                third_desc = LRSVM_desc

            if best_col == "RBF SVMR Prediction":
                best_model_df = RBFSVM_df  
                best_desc = RBFSVM_desc    
            elif second_col == "RBF SVMR Prediction":
                second_model_df = RBFSVM_df
                second_desc = RBFSVM_desc    
            else:
                third_model_df = RBFSVM_df
                third_desc = RBFSVM_desc    

            best_chart = generate_charts(best_model_df)
            second_chart = generate_charts(second_model_df)
            third_chart = generate_charts(third_model_df)  

            # Retrieve Accuracy Values to embed in cards
            best_acc = round(sorted_accuracy_df.iloc[0][0],5)
            second_acc = round(sorted_accuracy_df.iloc[0][1],5)
            third_acc = round(sorted_accuracy_df.iloc[0][2],5)

            return best_chart,second_chart,third_chart,best_acc,second_acc,third_acc,best_col,best_desc,second_col, second_desc,third_col,third_desc
        else:
            return errors



if __name__ == '__main__':
    app.run_server(debug=True)



