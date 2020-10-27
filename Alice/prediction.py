import dash
import dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
# from dash.dependencies import Input, Output
# import datetime as dt
# from dt import date
# import plotly.express as px

# from plotly.subplots import make_subplots

from datetime import datetime, timedelta 
today_date =datetime.today().strftime('%Y-%m-%d')

import pandas as pd
# import numpy as np
# import pandas_datareader.data as web

################# Import: Yfinance #########################
import pandas as pd
import yfinance as yf
from yahoofinancials import YahooFinancials
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
# plt.style.use('bmh') #Plotting graph 
import numpy as np

################# Data Processing #########################
# Ticker list
df = pd.read_csv('Client.csv',dtype='unicode')
df = df[df['Asset Class']=='EQUITIES']
final_df = df[df['Asset Sub Class'] == 'Common Stocks']
tickers = final_df["Ticker"].unique()
# Interval list
intervals = ['1M','6M','1Y']
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
        df = df.append({'Date': end_date, 'Linear Regression Prediction': lr}, ignore_index = True)  
    df = df[['Date', 'Close', 'Linear Regression Prediction']]
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

        df = df.append({'Date': end_date, 'RBF SVM Regression Prediction': svm}, ignore_index = True)    
        
    df = df[['Date', 'Close', 'RBF SVM Regression Prediction']]
    

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

        df = df.append({'Date': end_date, 'Linear SVM Regression Prediction': svm}, ignore_index = True)    
        
    df = df[['Date', 'Close', 'Linear SVM Regression Prediction']]
    

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

    Accuracy = {'Linear Regression Prediction': [lr_confidence], 
            'RBF SVM Regression Prediction': [rbf_svm_confidence],
            'Linear SVM Regression Prediction': [lin_svm_confidence]}
    
    df = pd.DataFrame(Accuracy, columns = ['Linear Regression Prediction', 'RBF SVM Regression Prediction', 'Linear SVM Regression Prediction'])
    
    return df
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([

    ################# Row 1: Filters + Submit Button #########################   
    dbc.Row([
        # Filter 1: Ticker
        dbc.Col([
            html.H3("Ticker: ",style={'color': 'white','text-align': 'left'}),
            dcc.Dropdown(
                    id='ticker_filter',
                    options=[
                        {'label': ticker, 'value': ticker} for ticker in tickers
                    ],
                    value = tickers[0],
                    placeholder="Filter by Ticker",
                    clearable=True
                ),\
        ], 
        width={'size':3}),

        # Filter 2: Start Date & End Date
        dbc.Col([
            html.H3("Interval:",style={'color': 'white','text-align': 'left'}),
            dcc.Dropdown(
                    id='interval',
                    options=[
                        {'label': interval, 'value': interval} for interval in intervals
                    ],
                    value = intervals[0],
                    placeholder="Filter by interval",
                    clearable=True
                )

            # dcc.DatePickerRange(
            #     id='date-picker-range',
            #     end_date=today_date,
            #     start_date_placeholder_text='Select a date',
            #     end_date_placeholder_text = 'Select a date',
            #     # start_date = today_date,
            #     style={'width': '100%'}
            # )

            # dbc.Button("YTD", color="dark",size="sm", id="ytd-button",n_clicks=0, className="mr-1"),
            
                # html.Div(id='output-container-date-picker-range')

        ],
        width={'size':3}),

        # Filter 3: Forecast period
       dbc.Col([
            html.H3("Forecast Period (days):",style={'color': 'white','text-align': 'left'}),
            dcc.Textarea(
                id = 'forecast_period',
                placeholder=' days',
                value = '5',
                # value='Textarea content initialized\nwith multiple lines of text',
                style={'width': '100%'}
            )
            ,\

        ],
        width={'size':3}),

        dbc.Col([
            html.Br(),
            html.Br(),

            # html.Button('Apply', id='submit_btn')
            dbc.Button(children='Apply', color="dark",size="lg", id="submit_btn",n_clicks=0, className="mr-1"),
        ],
        width={'size':3}),

        # Display Outputs 
        # html.Div(id='my_output')
    ],style={'backgroundColor': "#003B70"}),
    html.Br(),
    ################# Row 2: Display Outputs #########################   
    dbc.Row([

    ################# Col 1: 1st Accuracy Card #########################   
        dbc.Col([
            html.Br(),
            dbc.Card([
                dbc.CardBody(id='left_best_card')              
            ],
            color="light",  inverse=True, outline=False
            )

        ],width={'size':3}),
    ################# Col 2: 1st Line Graph #########################   
        dbc.Col([
            dcc.Graph(id='best_chart'),         
        ],width={'size':6}),
    ################# Col 3: 1st Description Card #########################   
        dbc.Col([
           html.Br(),
            dbc.Card([
                dbc.CardBody(id='right_best_card')              
            ],
            color="light",  inverse=True, outline=False
            )
        ],width={'size':3}
        ),
    ]),

    dbc.Row([
    ################# Col 1: 2nd Accuracy Card #########################  
        dbc.Col([
            html.Br(),
            html.Br(),
            dbc.Card([
                dbc.CardBody(id='left_second_card')              
            ],
            color="light",  inverse=True, outline=False
            )           
        ],width={'size':3}),
    ################# Col 2: 2nd Line Graph #########################  
        dbc.Col([
            html.Br(),
            dcc.Graph(id='second_chart'),            
        ],width={'size':6}),
    ################# Col 3: 2nd Description Card #########################  
        dbc.Col([
           html.Br(),
            dbc.Card([
                dbc.CardBody(id='right_second_card')              
            ],
            color="light",  inverse=True, outline=False
            )           
        ],width={"size":3}),
    ]),  

    dbc.Row([
    ################# Col 1: 3rd Accuracy Card #########################  
        dbc.Col([
            html.Br(),
            html.Br(),
            dbc.Card([
                dbc.CardBody(id='left_third_card')              
            ],
            color="light",  inverse=True, outline=False
            )            
        ],width={'size':3}),
    ################# Col 2: 3rd Line Graph #########################  
        dbc.Col([
            dcc.Graph(id='third_chart'),            
        ],width={'size':6}),
    ################# Col 3: 3rd Description Card #########################  
        dbc.Col([
           html.Br(),
            dbc.Card([
                dbc.CardBody(id='right_third_card')              
            ],
            color="light",  inverse=True, outline=False
            )            
        ],width={"size":3}),
    ])    
])


@app.callback(
    [
    Output("best_chart", "figure"),
    Output("second_chart","figure"),
    Output("third_chart","figure"),
    # Output("sorted_accuracy_table","columns"),
    # Output("sorted_accuracy_table","data"),
    Output("left_best_card", "children"),
    Output("left_second_card", "children"),
    Output("left_third_card", "children"),
    Output("right_best_card", "children"),
    Output("right_second_card", "children"),
    Output("right_third_card", "children")
    # Output("sorted_accuracy_table", "columns"),
    # Output('sorted_accuracy_table','data')
    ],
    Input('submit_btn', 'n_clicks'),
    # values to be passed upon clicking submit button
    [State('ticker_filter', 'value'),
    State('interval','value'),
    # State('date-picker-range', 'start_date'),
    # State('date-picker-range', 'end_date'),
    State('forecast_period', 'value')
    ]
) 


def update_output(n_clicks,ticker_subval,interval, period_subval):
    # Check if all 4 inputs are submitted
    errors = []
    # 1: Check if ticker input submitted
    if ticker_subval != "None" and interval != None  and period_subval != None:
        # return(ticker_subval,start_subval,end_subval, period_subval)
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

        if interval == "1M":
            interval = 21
        elif interval == "6M":
            interval = 126
        elif interval == "1Y":
            interval = 252
        

        # 3: If no validation error, generate relevant dataframes 
        if(errors == []):
            # prediction_df = get_prediction(ticker_subval,start_subval,end_subval,period_subval)
            end_subval = today_date
            days = timedelta(interval)
            start_subval = datetime.strptime(end_subval,'%Y-%m-%d') - days
            start_subval = start_subval.date()
            start_subval = datetime.strftime(start_subval,'%Y-%m-%d')

            accuracy_df = get_performance(ticker_subval,start_subval,end_subval,period_subval)
            sorted_accuracy_df = accuracy_df.sort_values(0,axis = 1, ascending=False)
            sorted_accuracy_table = sorted_accuracy_df.to_dict('records')
            sorted_accuracy_table_cols = [{"name": i, "id": i} for i in sorted_accuracy_df.columns]   
            # prediction_SVR_df['RBF SVR Prediction'] = prediction_SVR_df['RBF SVR Prediction'].apply(lambda x: round(x, 4))            
            # prediction_table = prediction_df.to_dict('records')
            # prediction_table_cols = [{"name": i, "id": i} for i in prediction_df.columns]

            
            # Retrieve Column names in sorted order (Best -> Worst)
            best_col = sorted_accuracy_df.columns[0] # "Linear Regression Prediction"
            second_col = sorted_accuracy_df.columns[1] # "Linear SVM Regression Prediction"
            third_col = sorted_accuracy_df.columns[2] # "RBF SVM Regression Prediction"

            LR_df = get_linearprediction(ticker_subval,start_subval,end_subval,period_subval)
            RBFSVM_df = get_RBFSVMPrediction(ticker_subval,start_subval,end_subval,period_subval)
            LRSVM_df = get_LinearSVMPrediction(ticker_subval,start_subval,end_subval,period_subval)

            LR_desc = "Linear regression attempts to model the relationship between two variables by fitting a linear equation to observed data. One variable is considered to be an explanatory variable, and the other is considered to be a dependent variable. "
            RBFSVM_desc = "Gaussian RBF (Radial Basis Function) is a Kernel method used in SVM models and its value depends on the distance from the origin or from some point."
            LRSVM_desc = "The algorithm creates a line or a hyperplane which separates the data into classes and is a linear model for classification and regression problems."

            if best_col == "Linear Regression Prediction":
                best_model_df = LR_df 
                best_desc = LR_desc     
            elif second_col == "Linear Regression Prediction":
                second_model_df = LR_df
                second_desc = LR_desc 
            else:
                third_model_df = LR_df
                third_desc = LR_desc 

            if best_col == "Linear SVM Regression Prediction":
                best_model_df = LRSVM_df   
                best_desc = LRSVM_desc   
            elif second_col == "Linear SVM Regression Prediction":
                second_model_df = LRSVM_df
                second_desc = LRSVM_desc
            else:
                third_model_df = LRSVM_df
                third_desc = LRSVM_desc

            if best_col == "RBF SVM Regression Prediction":
                best_model_df = RBFSVM_df  
                best_desc = RBFSVM_desc    
            elif second_col == "RBF SVM Regression Prediction":
                second_model_df = RBFSVM_df
                second_desc = RBFSVM_desc    
            else:
                third_model_df = RBFSVM_df
                third_desc = RBFSVM_desc    

            best_chart = px.line(best_model_df, x="Date", y=[best_model_df.columns[1],best_model_df.columns[2]], 
            color_discrete_sequence=['gray', 'blue'],title=best_model_df.columns[2] + " Chart")
            second_chart = px.line(second_model_df,x="Date", y=[second_model_df.columns[1],second_model_df.columns[2]], 
            color_discrete_sequence=['gray', 'blue'],title=second_model_df.columns[2] + " Chart")    
            third_chart = px.line(third_model_df,x="Date", y=[third_model_df.columns[1],third_model_df.columns[2]], 
            color_discrete_sequence=['gray', 'blue'],title=third_model_df.columns[2] + " Chart")   

            # Retrieve Accuracy Values to embed in cards
            best_acc = sorted_accuracy_df.iloc[0][0]  
            second_acc = sorted_accuracy_df.iloc[0][1]  
            third_acc = sorted_accuracy_df.iloc[0][2]  

            left_best_card = [
                html.Br(),
                html.Br(),
                html.Br(),
                html.H2("Accuracy Rank 1",style={"color":"#003B70"}),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H5("Confidence Level: {}".format(best_acc),style={"color":"#003B70"}),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br()
            ]
            left_second_card = [
                html.Br(),
                html.Br(),
                html.Br(),
                html.H2("Accuracy Rank 2",style={"color":"#4665ae"}),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H5("Confidence Level: {}".format(second_acc),style={"color":"#4665ae"}),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br()
            ]
            left_third_card = [
                html.Br(),
                html.Br(),
                html.Br(),
                html.H2("Accuracy Rank 3",style={"color":"#7791d1"}),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H5("Confidence Level: {}".format(third_acc),style={"color":"#7791d1"}),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br()
            ]
            

            right_best_card = [
                html.Br(),
                html.H2(best_model_df.columns[2],style={"color":"#003B70"}),
                html.Br(),
                html.H5("Model Description: {}".format(best_desc),style={"color":"#003B70"}),
                html.Br(),
                html.Br(),
                html.Br()
            ]
            right_second_card = [
                html.Br(),
                html.H2(second_model_df.columns[2],style={"color":"#4665ae"}),
                html.Br(),
                html.H5("Model Description: {}".format(second_desc),style={"color":"#4665ae"}),
                html.Br(),
                html.Br(),
                html.Br()
            ]
            right_third_card = [
                html.Br(),
                html.H2(third_model_df.columns[2],style={"color":"#7791d1"}),
                html.Br(),
                html.H5("Model Description: {}".format(third_desc),style={"color":"#7791d1"}),
                html.Br(),
                html.Br(),
                html.Br()
            ]
            return best_chart,second_chart,third_chart,left_best_card, left_second_card, left_third_card,right_best_card, right_second_card, right_third_card
            # return "no errors"
        else:
            return errors



if __name__ == '__main__':
    app.run_server(debug=True)



