import dash_bootstrap_components as dbc
from dash import html

def login_layout():
    return dbc.Container(
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H2("Login", className="text-center mb-4 text-white"),
                        dbc.Input(id="username", placeholder="Benutzername", type="text", className="mb-3"),
                        dbc.Input(id="password", placeholder="Passwort", type="password", className="mb-3"),
                        dbc.Button("Login", id="login-button", color="primary", className="me-2", n_clicks=0),
                        dbc.Button("Registrieren", href="/register", color="secondary", n_clicks=0),
                        html.Div(id="login-output", className="mt-3 text-warning")
                    ]),
                    className="bg-dark"
                ),
                width=6,
                lg=4
            ),
            justify="center",
            align="center",
            className="vh-100"
        ),
        fluid=True
    )
