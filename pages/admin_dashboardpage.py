import dash_bootstrap_components as dbc
from dash import html, Output, Input, dcc, State, callback
import dash_iconify as dic

def admin_dashboard_layout():
    sidebar = dbc.Offcanvas(
        dbc.Nav(
            [
                dbc.NavLink(
                    [
                        dic.DashIconify(icon="mdi:view-dashboard", width=25),
                        " Gesamtüberblick"
                    ],
                    href="/admin/overview",
                    active="exact",
                    className="py-2 fs-5"
                ),
                dbc.NavLink(
                    [
                        dic.DashIconify(icon="mdi:thermometer", width=25),
                        " Sensor 1"
                    ],
                    href="/admin/sensor1",
                    active="exact",
                    className="py-2 fs-5"
                ),
                dbc.NavLink(
                    [
                        dic.DashIconify(icon="mdi:thermometer", width=25),
                        " Sensor 2"
                    ],
                    href="/admin/sensor2",
                    active="exact",
                    className="py-2 fs-5"
                ),
                dbc.NavLink(
                    [
                        dic.DashIconify(icon="mdi:thermometer", width=25),
                        " Sensor 3"
                    ],
                    href="/admin/sensor3",
                    active="exact",
                    className="py-2 fs-5"
                ),
                dbc.NavLink(
                    [
                        dic.DashIconify(icon="mdi:thermometer", width=25),
                        " Sensor 4"
                    ],
                    href="/admin/sensor4",
                    active="exact",
                    className="py-2 fs-5"
                ),
                dbc.NavLink(
                    [
                        dic.DashIconify(icon="mdi:thermometer", width=25),
                        " Sensor 5"
                    ],
                    href="/admin/sensor5",
                    active="exact",
                    className="py-2 fs-5"
                ),
                dbc.NavLink(
                    [
                        dic.DashIconify(icon="mdi:cog", width=25),
                        " Einstellungen"
                    ],
                    href="/admin/settings",
                    active="exact",
                    className="py-2 fs-5"
                ),
                dbc.NavLink(
                    [
                        dic.DashIconify(icon="mdi:logout", width=25),
                        " Abmelden"
                    ],
                    href="/logout",
                    className="py-2 text-danger fs-5"
                ),
            ],
            vertical=True,
            pills=True,
        ),
        id="sidebar",
        title="Navigation",
        is_open=True,
        placement="start",
        className="bg-light",
        style={"width": "300px"}
    )

    toggle_button = dbc.Button(
        html.Div(
            dic.DashIconify(icon="mdi:menu", width=30),
            style={
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "height": "100%",
                "width": "100%"
            }
        ),
        id="sidebar-toggle",
        className="position-fixed",
        style={
            "top": "20px",
            "left": "20px",
            "zIndex": "1000",
            "width": "50px",
            "height": "50px",
            "borderRadius": "50%",
            "padding": "0",
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center"
        },
        color="primary"
    )

    content = dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H2("Admin Dashboard", className="text-white text-center mb-2",
                           style={"marginTop": "-10px"}),
                    html.P("Hier kannst du verschiedene Einstellungen zu den Sensoren und deren Daten vornehmen",
                          className="text-white text-center"),
                ], className="mx-auto", style={"maxWidth": "800px"}),
                dbc.Alert("Willkommen! Du bist eingeloggt.",
                         id="logged_in",
                         color="success",
                         is_open=True,
                         dismissable=True,
                         className="mx-auto",
                         style={"maxWidth": "800px"}),
                dcc.Interval(id="alert-close-timer", interval=3000, n_intervals=0, max_intervals=1),
                html.Div(id="admin-page-content", className="mx-auto", style={"maxWidth": "800px"})
            ]),
            className="bg-dark h-100"
        ),
        className="px-0"
    )

    return dbc.Container(
        [
            toggle_button,
            sidebar,
            dbc.Row(
                [
                    dbc.Col(content, width=12)
                ],
                className="g-0 vh-100 d-flex align-items-center justify-content-center"
            )
        ],
        fluid=True,
        style={"paddingLeft": "0px", "transition": "padding-left 0.3s"}
    )

# Callback für das Öffnen/Schließen der Sidebar
@callback(
    Output("sidebar", "is_open"),
    Input("sidebar-toggle", "n_clicks"),
    State("sidebar", "is_open"),
    prevent_initial_call=True
)
def toggle_sidebar(n, is_open):
    return not is_open

# Callback für das Schließen der Alert-Box
@callback(
    Output("logged_in", "is_open"),
    Input("alert-close-timer", "n_intervals"),
)
def close_alert(n):
    if n > 0:
        return False
    return True