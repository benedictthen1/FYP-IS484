import dash
import dash_bootstrap_components as dbc
# import os
# from flask import send_from_directory

# meta_tags are required for the app layout to be mobile responsive
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP,'/static/style.css'], suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

# external_css = [
#     '/static/style.css'
# ]
# for css in external_css:
#     app.css.append_css({"external_url": css})


# @app.server.route('/static/<path:path>')
# def static_file(path):
#     static_folder = os.path.join(os.getcwd(), 'static')
#     return send_from_directory(static_folder, path)


server = app.server

