# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8080/ in your web browser.

import dash
import dash_html_components as html

app = dash.Dash(__name__)
app.layout = html.H1(children='HELLO Dash :)')

if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='127.0.0.1')

