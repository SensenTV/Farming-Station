import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input
from dash import get_app
app = get_app()

def user_dashboard_layout():
        return dbc.Container([
            dbc.Row(
                 dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H2("User Dashboard", className="text-white"),
                            html.P("Hier kannst du verschiedene Einstellungen zu den Sensoren und deren Daten vornehemen",
                                    className="text-white"),
                            dbc.Button("Logout", id="logout-button", color="danger", className="mt-3"),
                            dbc.Alert("Willkommen! Du bist eingeloggt.",
                                      id="logged_in",
                                      color="success",
                                      is_open=True,
                                      dismissable=True
                                      ),
                            dcc.Interval(id="alert-close-timer", interval=3000, n_intervals=0, max_intervals=1),
                        ]),
                        className="bg-dark"
                    ),
                    width=6,
                    lg=4
                ),
                justify="center",
                align="center",
                className="vh-100"
            )
        ],
        fluid=True,
    )

# Logout Callback: Session leeren und zurück zum Login
@app.callback(
    Output('session-store', 'data'),
    Output('url', 'pathname'),
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def logout(n_clicks):
    return {}, '/'