# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input,Output
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

df = pd.read_csv('./data/pop_mis.csv')
#df = df_raw[df_raw['분석년월'] > 202000].copy()
df['분석년월'] = pd.to_datetime(df['분석년월'], format='%Y%m')

app.layout = html.Div(children=[
    html.H1('행정안전부 데이터'),
    html.H4('2008~2020년 데이터'),

    html.Label('시도'),
    dcc.Dropdown(
        id = 'sido',
        options=[{'label': k, 'value': k} for k in df['시도'].sort_values().unique()],
        value='전국'
    ),
    html.Label('시군구'),
    dcc.Dropdown(
        id='sgg',
        options=[{'label': k, 'value': k} for k in df['시군구'].sort_values().unique()],
        value='-'
    ),
    html.Label('행정동'),
    dcc.Dropdown(
        id='hjd',
        options=[{'label': k, 'value': k} for k in df['행정동'].sort_values().unique()],
        value='-'
    ),
    dt.DataTable(
        id='pop-table',
        columns= [{'name': i, 'id': i} for i in df.columns],
        data=df.to_dict('records'),
        page_action='native',
        page_size=10,
        column_selectable="single",
        selected_columns=[],
        row_selectable="multi",
        selected_rows=[]
    ),
    html.Div(id='pop-graph',
             style={'marginTop': 50})
 ])

@app.callback(
    Output('pop-table', 'data'),
    [Input('sido', 'value'), Input('sgg', 'value'), Input('hjd', 'value')])
def update_table(*args):
    if args[0] != '전국':
        if args[1] != '-':
            if args[2] != '-':
                result = df[(df['시도'] == args[0]) & (df['시군구'] == args[1]) & (df['행정동'] == args[2])]
            else:
                result = df[(df['시도'] == args[0]) & (df['시군구'] == args[1])]
        else:
            result = df[(df['시도'] == args[0])]
    else:
        result = df
    return result.to_dict('records')

@app.callback(
    Output('sgg', 'options'),
    Input('sido', 'value'))
def update_sgg_drowDown(sido):
    result = df[df['시도'] == sido]
    #dash.callback_context
    return [{'label': k, 'value': k} for k in result['시군구'].sort_values().unique()]

@app.callback(
    Output('hjd', 'options'),
    Input('sgg', 'value'))
def update_hjd_drowDown(sgg):
    result = df[df['시군구'] == sgg]

    #dash.callback_context
    return [{'label': k, 'value': k} for k in result['행정동'].sort_values().unique()]

@app.callback(
    Output('pop-graph', 'children'),
    Input('pop-table', 'derived_virtual_data'),
    Input('pop-table', 'derived_virtual_selected_rows')
)
def update_graph(data, derived_virtual_selected_rows):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []
    result_tot = df if data is None else pd.DataFrame(data)
    key = result_tot[['시도', '시군구', '행정동']].values[0]
    result = result_tot[(result_tot['시도'] == key[0]) & (result_tot['시군구'] == key[1]) & (result_tot['행정동'] == key[2])]
    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9' for i in range(len(result))]
    return [dcc.Graph(
        id='tot-pop',
        figure={
            'data': [
                {
                'x': result['분석년월'],
                'y': result['총인구수'],
                'type': 'line',
                'marker': {'color': colors}
                }
            ],
            'layout': {
                'xaxis': {'automargin': True},
                'yaxis': {'automargin': True},
                'title': '{} 총 인구 수'.format('-'.join([i for i in result[['시도', '시군구', '행정동']].values[0] if i != '-']))
            }
        }
    )
    ]

if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='127.0.0.1')