from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = Flask(__name__, instance_relative_config=False)

@app.route("/method2")
def hello():
    return "method2"

dash_app = dash.Dash(__name__, server=app, routes_pathname_prefix="/dash1/")

dash_app.layout = html.Div([
    html.H6("Change the value in the text box to see callbacks in action!"),
    html.Div(["Input: ",
              dcc.Input(id='my-input', value='initial value', type='text')]),
    html.Br(),
    html.Div(id='my-output'),

])




# @app.route('/')
# def home():
#     """Landing page."""
#     return render_template('home.html')

# app.config.from_object('config.Config')

# with app.app_context():
#     # Import parts of our core Flask app
#     import routes

#     # Import Dash application
#     from dashboard import init_dashboard
#     from dashboard2 import init_dashboard2
#     app = init_dashboard(app)
#     app = init_dashboard2(app)

