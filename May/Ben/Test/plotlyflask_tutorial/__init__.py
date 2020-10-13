"""Initialize Flask app."""
from flask import Flask
import config


def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes

        # Import Dash application
        from dashboard import init_dashboard
        from dashboard2 import init_dashboard2
        
        #from grid import grid_test
        app = init_dashboard(app)
        app = init_dashboard2(app)

        return app