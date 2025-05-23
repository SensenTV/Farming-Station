import dash_bootstrap_components as dbc
from dash import html

def register_layout():
    return dbc.Container(
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H2("Registrieren", className="text-center mb-4 text-white"),
                        dbc.Input(id="username", placeholder="Benutzername", type="text", className="mb-3"),
                        dbc.Input(id="password", placeholder="Passwort", type="password", className="mb-3"),
                        dbc.Input(id="confirm_password", placeholder="Passwort bestätigen", type="password", className="mb-3"),
                        dbc.Button("Registrieren", id="register-button", color="success", className="me-2", n_clicks=0),
                        dbc.Button("Zurück zum Login", href="/", color="secondary"),
                        html.Div(id="register-output", className="mt-3 text-warning"),
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
