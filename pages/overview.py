from dash import html, dcc
import dash_bootstrap_components as dbc

def overview_layout():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.H3("Gesamtübersicht aller Sensoren", className="text-center"),
                dcc.Graph(id='overview-graph'),
                dbc.Row([
                    dbc.Col(dbc.Card("Statistik 1", body=True), md=4),
                    dbc.Col(dbc.Card("Statistik 2", body=True), md=4),
                    dbc.Col(dbc.Card("Statistik 3", body=True), md=4),
                ], className="mt-4")
            ]),
            className="mt-4"
        )
    ])