from flask import Flask, render_template, request
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
#from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc


#Flask
server = Flask(__name__)

subscribers = []

@server.route("/")
def home():
    title = "bobby world"
    return render_template("index.html", title=title)

@server.route("/stock")
def stock():
    names = ["bob", "sally", "mike"]
    return render_template("stock.html",names = names)

@server.route("/subscribe")
def subscribe():
    title = "Sub to me Bij"
    return render_template("subscribe.html", title=title)

@server.route("/form", methods=["POST"])
def form():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    subscribers.append(f"{first_name} {last_name} | {email}")
    title = "Thx bijjjj"
    return render_template("form.html", title=title, subscribers=subscribers)

app = dash.Dash(__name__,server=server,routes_pathname_prefix='/dash/')
app.layout = html.Div("My Dash app")

if __name__ == "__main__":
    server.run(debug=True)