import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import dash_table
import plotly.graph_objs as go

df = pd.read_csv("output.csv")


app = dash.Dash(
    external_stylesheets=[dbc.themes.LUX])


app.layout = html.Div([
    #Überschrift
    dbc.Row(dbc.Col(html.H3("Analyse von Tweets"),
                    width={'size': 6, 'offset': 1},
                    )
    ),
    dbc.Row(dbc.Col(html.H3(""),
                    width=6,
                    )
    ),
    #Tabelle
    dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i}
            for i in df.columns],
    data=df.to_dict('records'),   
    editable=True,
    filter_action="native",
    sort_action="native",
    page_size=20,
    style_data={
        'whiteSpace': 'normal',
        'height': 'auto'
        },
    style_cell_conditional=[    # align text columns to left. By default they are aligned to right
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['tweets', 'author', 'source']
    ],
    ),

    html.Br(),
    html.Br(),
    html.Div(id='bar-container'),

    html.P(children='''Limitationen: Twitter hat bei seiner API die maximale Anzahl der zucrawlenden Tweets limitiert. Damit lässt sich also nicht das gesamte Thema abbilden, sondern ein Ausschnitt dessen. Aus dem Grund muss das bei der Analyse und Interpretation der Daten berücksichtigt werden.''',
             style={'textAlign': 'center', 'color': 'red'})
])


if __name__ == '__main__':
    app.run_server()

