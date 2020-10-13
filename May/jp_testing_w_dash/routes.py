"""Routes for parent Flask app."""
from flask import render_template
from flask import current_app as app
import os
from flask import Flask, redirect, url_for
import justpy as jp

@app.route('/')
def home():
    """Landing page."""
    return render_template('home.html')

# @jp.SetRoute('/wm')
# def serve_wm():
#     wp = jp.WebPage()
#     jp.Div(text='All Majors', classes=title_classes, a=wp)
#     wm.jp.ag_grid(a=wp, style=grid_style)
#     return wp