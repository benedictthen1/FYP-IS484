"""Routes for parent Flask app."""
from flask import render_template
from flask import current_app as app
import os
from flask import Flask, redirect, url_for


@app.route('/')
def home():
    """Landing page."""
    return render_template('home.html')