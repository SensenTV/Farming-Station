from dash import html, Output, Input, dcc, callback, callback_context, ctx
from datetime import timedelta
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash.dependencies import State
from datetime import datetime
import pandas as pd
import sqlite3
import os
import csv

DB_PATH = "./SQLite/sensors.db"
LOG_FILE = "log.csv"
log_data = []

# Aktualisiertes Farbschema
COLOR_SCHEME = {
    'background': '#ffffff',  # Weißer Hintergrund
    'card_bg': '#f8f9fa',  # Helles Grau für Karten
    'accent': '#2563eb',  # Moderne Blau Akzentfarbe
    'text_primary': '#1e293b',  # Dunkles Blau-Grau für Text
    'text_secondary': '#64748b',  # Mittleres Grau für sekundären Text
    'success': '#22c55e',  # Grün für positive Status
    'warning': '#f59e0b',  # Orange für Warnungen
    'border': '#e2e8f0',  # Hellgrau für Borders
    'graph_grid': '#e2e8f0',  # Hellgrau für Graphenraster
    'log_bg': '#e5e7eb',  # Leicht dunkleres Grau für Log/Kamera Bereiche
    'control_bg': '#e5e7eb',  # Leicht dunkleres Grau für Steuerungselemente
    'transparent': 'rgba(0, 0, 0, 0)',  # komplett transparent
}


def admin_dashboard_layout():
    # Lade gespeicherte Zeitstempel
    licht_data = get_light_data()
    start_time = licht_data.get("start_time")
    end_time = licht_data.get("end_time")
    pump_data = get_pump_data()
    fan_data = get_fan_data()

    system_card = dbc.Card([
        dbc.CardHeader(
            dbc.Row([
                dbc.Col(
                    html.H3("System 1", style={"color": COLOR_SCHEME['text_primary']}),
                    width=11,
                    style={"background-color": COLOR_SCHEME['card_bg']},
                ),
                dbc.Col(
                    dbc.Button("Logout", id={'type': 'logout-btn', 'index': 'admin'}, color="primary", outline=True),
                    width="auto",
                    className="d-flex justify-content-right",  # Button rechts ausrichten
                )
            ]), style={"background-color": COLOR_SCHEME['card_bg']},
        ),
        dbc.CardBody([
            # Aktuelle Werte
            html.H4("Aktuelle Werte:", className="mb-3", style={"color": COLOR_SCHEME['text_primary']}),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.Row([
                            dbc.Col(
                                html.Strong("Füllstand: ", style={"color": COLOR_SCHEME['text_primary']}),
                                width="auto"
                            ),
                            dbc.Col(
                                html.Span("-", id="fuellstand-wert", style={"color": COLOR_SCHEME['accent']}),
                                className="d-flex justify-content-left",
                                width=True,
                            ),
                            dbc.Col(
                                dbc.Button("Graph", id="fuellstand-graph-btn", size="sm", color="primary",
                                           className="ms-2"),
                                className="d-flex justify-content-end",
                                width=True,
                            ),
                        ], align="center", className="mb-2"),

                        dbc.Row([
                            dbc.Col(
                                html.Strong("PH: ", style={"color": COLOR_SCHEME['text_primary']}),
                                width="auto"
                            ),
                            dbc.Col(
                                html.Span("-", id="ph-wert", style={"color": COLOR_SCHEME['accent']}),
                                className="d-flex justify-content-left",
                                width=True,
                            ),
                            dbc.Col(
                                dbc.Button("Graph", id="ph-graph-btn", size="sm", color="primary", className="ms-2"),
                                className="d-flex justify-content-end",
                                width=True,
                            ),
                        ], align="center", className="mb-2"),

                        dbc.Row([
                            dbc.Col(
                                html.Strong("EC: ", style={"color": COLOR_SCHEME['text_primary']}),
                                width="auto"
                            ),
                            dbc.Col(
                                html.Span("-", id="ec-wert", style={"color": COLOR_SCHEME['accent']}),
                                className="d-flex justify-content-left",
                                width=True,
                            ),
                            dbc.Col(
                                dbc.Button("Graph", id="ec-graph-btn", size="sm", color="primary", className="ms-2"),
                                className="d-flex justify-content-end",
                                width=True,
                            ),
                        ], align="center", className="mb-2"),

                        dbc.Row([
                            dbc.Col(
                                html.Strong("Temp: ", style={"color": COLOR_SCHEME['text_primary']}),
                                width="auto"
                            ),
                            dbc.Col(
                                html.Span("-", id="temp-wert", style={"color": COLOR_SCHEME['accent']}),
                                className="d-flex justify-content-left",
                                width=True,
                            ),
                            dbc.Col(
                                dbc.Button("Graph", id="temp-graph-btn", size="sm", color="primary", className="ms-2"),
                                className="d-flex justify-content-end",
                                width=True,
                            ),
                        ], align="center", className="mb-2"),

                        dbc.Row([
                            dbc.Col(
                                html.Strong("Luftfeuchtigkeit: ", style={"color": COLOR_SCHEME['text_primary']}),
                                width="auto"
                            ),
                            dbc.Col(
                                html.Span("-", id="luft-wert", style={"color": COLOR_SCHEME['accent']}),
                                className="d-flex justify-content-left",
                                width="auto"
                            ),
                            dbc.Col(
                                dbc.Button("Graph", id="luft-graph-btn", size="sm", color="primary", className="ms-2"),
                                className="d-flex justify-content-end",
                                width=True,
                            ),
                        ], align="center", className="mb-2"),
                    ], style={"background-color": COLOR_SCHEME['transparent'], "width": "auto", "border": "none"}),
                ], md=2),

                dbc.Col([
                    html.Div(
                        dcc.Graph(
                            id="sensor-graph",
                            style={"height": "300px"},
                            config={
                                "displayModeBar": True,
                                "modeBarButtonsToRemove": [
                                    "zoom2d", "select2d", "lasso2d",
                                    "autoScale2d"
                                ],
                                "displaylogo": False
                            }
                        ),
                        id="graph-container",
                        style={"display": "none"},
                        className="my-3 p-2",
                    )
                ], md=10),
                dcc.Interval(id='werte-refresh', interval=5000, n_intervals=0)
            ]),

            dbc.Card([
                dbc.CardBody([
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.DropdownMenu(
                                    [
                                        dbc.DropdownMenuItem("Füllstand",
                                                             id="water_level_sensor_dropdown_button",
                                                             n_clicks=0),
                                        dbc.DropdownMenuItem("PH", id="ph_sensor_dropdown_button", n_clicks=0),
                                        dbc.DropdownMenuItem("EC", id="ec_sensor_dropdown_button", n_clicks=0),
                                        dbc.DropdownMenuItem("Temp", id="temp_sensor_dropdown_button",
                                                             n_clicks=0),
                                        dbc.DropdownMenuItem("Luftfeuchtigkeit",
                                                             id="humidity_sensor_dropdown_button", n_clicks=0),
                                        dbc.DropdownMenuItem("Alle Sensoren", id="all_sensor_dropdown_button",
                                                             n_clicks=0),
                                    ],
                                    label="Sensoren auswählen",
                                    id="sensor_dropdown",
                                    className="me-2",  # kleiner Abstand rechts
                                ),
                                width="auto",
                            ),
                            dbc.Col(
                                html.P("über die letzten",
                                       style={"color": COLOR_SCHEME['text_primary'], "margin": "0"}),
                                width="auto",
                                className="d-flex align-items-center",  # vertikal mittig
                            ),
                            dbc.Col(
                                html.Div([
                                    dbc.Input(type="number", min=0, max=365, step=1, id="number"),
                                    dbc.Tooltip(
                                        "Geben Sie eine Nummer zwischen 0-365",
                                        target="number",
                                        placement="bottom",
                                    )
                                ]),
                                width="auto",
                            ),
                            dbc.Col(
                                dbc.DropdownMenu([
                                    dbc.DropdownMenuItem("Stunden", id="hour_dropdown_button", n_clicks=0),
                                    dbc.DropdownMenuItem("Tage", id="days_dropdown_button", n_clicks=0),
                                ],
                                    label="Zeiteinheit",
                                    id="time_dropdown",
                                    className="me-2",
                                ),
                                width="auto",
                            ),
                            dbc.Col([
                                dbc.Button("Herunterladen", id="download_button", n_clicks=0),
                                dcc.Download(id="download")
                            ], width="auto")
                        ],
                        className="g-1",
                        align="center",
                    )
                ])
            ], className="mb-3", style={"background-color": COLOR_SCHEME['control_bg'], "width": "auto%"}),

            html.Hr(style={"border-color": COLOR_SCHEME['border']}),

            # Log und Kamera nebeneinander
            dbc.Row([
                # Error Log
                dbc.Col([
                    html.H4("Log:", className="mb-3", style={"color": COLOR_SCHEME['text_primary']}),
                    dbc.Textarea(
                        id="error-log",
                        className="mb-3",
                        style={
                            "height": "200px",
                            "background-color": COLOR_SCHEME['log_bg'],
                            "color": COLOR_SCHEME['text_primary'],
                            "border": f"1px solid {COLOR_SCHEME['border']}",
                            "resize": "none",
                            "border-radius": "4px"
                        },
                        readOnly=True
                    ),
                    dbc.Button("Download Log", id="download-btn", color="primary", className="mt-2"),
                    dcc.Download(id="download-log"),
                    dbc.Button("Clear Log", id="clear-log-btn", color="danger", className="mt-2 ms-2")
                ], md=6),

                # Kamera
                dbc.Col([
                    html.H4("Cam1:", className="mb-3", style={"color": COLOR_SCHEME['text_primary']}),
                    # Kamera-Bereich
                    html.Div(
                        id="camera-feed",
                        style={
                            "height": "200px",
                            "background-color": COLOR_SCHEME['log_bg'],
                            "display": "flex",
                            "align-items": "center",
                            "justify-content": "center",
                            "border": f"1px solid {COLOR_SCHEME['border']}",
                            "border-radius": "4px"
                        },
                        children=html.P("Kamera-Feed nicht verfügbar",
                                        style={"color": COLOR_SCHEME['text_primary']})
                    ),
                ], md=6),
            ], className="mb-4"),
            dcc.Interval(id="log-update", interval=10000, n_intervals=0),
            html.Div(id="dummy-output", style={"display": "none"}),

            # Steuerungselemente
            dbc.Row([
                dcc.Interval(id="luefter-interval", interval=5 * 1000, n_intervals=0),
                dcc.Interval(id="pumpe-interval", interval=5 * 1000, n_intervals=0),
                dcc.Interval(id="licht-interval", interval=5 * 1000, n_intervals=0),
                # Lüfter
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col(
                                    html.Span("Lüfter", style={
                                        "color": COLOR_SCHEME['text_primary'],
                                        "font-weight": "500",
                                    }),
                                    className="d-flex align-items-center"
                                ),
                                dbc.Col(
                                    dbc.Switch(
                                        id="luefter-switch",
                                        disabled=True,
                                        className="float-end"
                                    ),
                                    className="d-flex justify-content-end"
                                ),
                            ]),
                            # Lüftereinstellungen
                            html.Div([
                                dbc.Label("Alle", html_for="fan-intervall", className="me-2 mb-0",
                                          style={"color": COLOR_SCHEME['text_primary']}),
                                dbc.Input(id="fan-intervall",
                                          type="number",
                                          className="me-2",
                                          size="sm",
                                          min=0,
                                          max=120,
                                          style={"width": "15%"},
                                          step=1,
                                          value=fan_data["intervall"]
                                          ),
                                dbc.Label("Minuten für", html_for="fan-intervall", className="me-2 mb-0",
                                          style={"color": COLOR_SCHEME['text_primary']}),
                                dbc.Input(id="fan-on-for",
                                          type="number",
                                          className="me-2",
                                          size="sm",
                                          min=0,
                                          max=120,
                                          style={"width": "15%"},
                                          step=1,
                                          value=fan_data["on_for"]
                                          ),
                                dbc.Label("Minuten einschalten", html_for="fan-intervall", className="me-2 mb-0",
                                          style={"color": COLOR_SCHEME['text_primary']})
                            ], className="d-flex align-items-center mt-2"),
                            html.Small(
                                f"Last change: {get_last_change('Fan')}",
                                id="luefter-last-change",
                                className="d-block mt-2",
                                style={"color": COLOR_SCHEME['text_secondary']}
                            )
                        ]),
                    ], className="mb-3", style={"background-color": COLOR_SCHEME['control_bg'], "width": "100%"}),
                ], md=4),

                # Licht
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col(
                                    html.Span("Licht", style={
                                        "color": COLOR_SCHEME['text_primary'],
                                        "font-weight": "500",
                                    }),
                                    className="d-flex align-items-center"
                                ),
                                dbc.Col(
                                    dbc.Switch(
                                        id="licht-switch",
                                        disabled=True,
                                        className="float-end"
                                    ),
                                    className="d-flex justify-content-end"
                                ),
                            ]),

                            # Zeiteinstellung
                            html.Div([
                                dbc.Label("Eingeschaltet von:", html_for="licht-start-time", className="me-2 mb-0",
                                          style={"color": COLOR_SCHEME['text_primary']}),
                                dmc.TimeInput(
                                    id="licht-start-time",
                                    value=licht_data["start_time"],
                                    placeholder="HH:mm",
                                    className="me-2",
                                    size="sm"
                                ),
                                dbc.Label("bis:", html_for="licht-end-time", className="me-2 mb-0",
                                          style={"color": COLOR_SCHEME['text_primary']}),
                                dmc.TimeInput(
                                    id="licht-end-time",
                                    value=licht_data["end_time"],
                                    placeholder="HH:mm",
                                    className="me-2",
                                    size="sm"
                                ),
                                dbc.Label("sowie von:", html_for="second-licht-start-time", className="me-2 mb-0",
                                          style={"color": COLOR_SCHEME['text_primary']}),
                                dmc.TimeInput(
                                    id="second-licht-start-time",
                                    value=licht_data["second_start_time"],
                                    placeholder="HH:mm",
                                    className="me-2",
                                    size="sm"
                                ),
                                dbc.Label("bis:", html_for="second-licht-end-time", className="me-2 mb-0",
                                          style={"color": COLOR_SCHEME['text_primary']}),
                                dmc.TimeInput(
                                    id="second-licht-end-time",
                                    value=licht_data["second_end_time"],
                                    placeholder="HH:mm",
                                    className="me-2",
                                    size="sm"
                                ),
                            ], className="d-flex align-items-center mt-2"),
                            html.Small(
                                f"Last change: {licht_data.get('last_change', '-')}",
                                id="licht-last-change",
                                className="d-block mt-2",
                                style={"color": COLOR_SCHEME['text_secondary']}
                            )
                        ]),
                    ], className="mb-3", style={"background-color": COLOR_SCHEME['control_bg'], "width": "100%"}),
                ], md=4),

                # Wasserpumpe
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col(
                                    html.Span("Wasserpumpe", style={
                                        "color": COLOR_SCHEME['text_primary'],
                                        "font-weight": "500",
                                    }),
                                    className="d-flex align-items-center"
                                ),
                                dbc.Col(
                                    dbc.Switch(
                                        id="pumpe-switch",
                                        disabled=True,
                                        className="float-end"
                                    ),
                                    className="d-flex justify-content-end"
                                ),
                            ]),

                            # Pumpeneinstellung
                            html.Div([
                                dbc.Label("Alle", html_for="pump-intervall", className="me-2 mb-0",
                                          style={"color": COLOR_SCHEME['text_primary']}),
                                dbc.Input(id="pump-intervall",
                                          type="number",
                                          className="me-2",
                                          size="sm",
                                          min=0,
                                          max=120,
                                          style={"width": "15%"},
                                          step=1,
                                          value=pump_data["intervall"]
                                          ),
                                dbc.Label("Minuten für", html_for="pump-intervall", className="me-2 mb-0",
                                          style={"color": COLOR_SCHEME['text_primary']}),
                                dbc.Input(id="pump-on-for",
                                          type="number",
                                          className="me-2",
                                          size="sm",
                                          min=0,
                                          max=120,
                                          style={"width": "15%"},
                                          step=1,
                                          value=pump_data["on_for"]
                                          ),
                                dbc.Label("Minuten einschalten", html_for="pump-intervall", className="me-2 mb-0",
                                          style={"color": COLOR_SCHEME['text_primary']})
                            ], className="d-flex align-items-center mt-2"),
                            html.Small(
                                f"Last change: {get_last_change('Pump')}",
                                id="pumpe-last-change",
                                className="d-block mt-2",
                                style={"color": COLOR_SCHEME['text_secondary']}
                            )
                        ])
                    ], className="mb-3", style={"background-color": COLOR_SCHEME['control_bg'], "width": "100%"}),
                ], md=4),
            ]),
        ], style={"background-color": COLOR_SCHEME['card_bg']}),
    ], className="shadow-sm")

    return dbc.Container(
        children=[  # Alles in einer Liste
            dbc.Row([
                dbc.Col(system_card, width=12)
            ], className="g-0 vh-100 py-4"),
            dcc.Interval(
                id='admin-refresh-interval',
                interval=3000,
                n_intervals=0
            )
        ],
        fluid=True,
        style={"background-color": COLOR_SCHEME['background']}
    )


# ------------------------------
# Funktion: Lichtwerte lesen
# ------------------------------
def get_light_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT last_change, start_time, end_time FROM Light LIMIT 2")
    result = cursor.fetchall()
    conn.close()
    if result:
        return {
            "last_change": result[0][0],
            "start_time": result[0][1],
            "end_time": result[0][2],
            "second_start_time": result[1][1],
            "second_end_time": result[1][2],
        }
    else:
        return {
            "last_change": "-",
            "start_time": "06:00",
            "end_time": "22:00",
            "second_start_time": "00:00",
            "second_end_time": "05:00",
        }


# ------------------------------
# Funktion: Lichtwerte schreiben
# ------------------------------
def update_light_data(last_change=None, start_time=None, end_time=None, second_start_time=None, second_end_time=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Existiert schon ein Eintrag?
    cursor.execute("SELECT COUNT(*) FROM Light")
    exists = cursor.fetchall()[0]

    if exists:
        if last_change is not None:
            cursor.execute("UPDATE Light SET last_change = ? WHERE ROWID = 1", (last_change,))
        if start_time is not None:
            cursor.execute("UPDATE Light SET start_time = ? WHERE ROWID = 1", (start_time,))
        if end_time is not None:
            cursor.execute("UPDATE Light SET end_time = ? WHERE ROWID = 1", (end_time,))
        if second_start_time is not None:
            cursor.execute("UPDATE Light SET start_time = ? WHERE ROWID = 2", (second_start_time,))
        if second_end_time is not None:
            cursor.execute("UPDATE Light SET end_time = ? WHERE ROWID = 2", (second_end_time,))
    else:
        # Fallback-Eintrag
        cursor.execute("INSERT INTO Light (last_change, start_time, end_time) VALUES (?, ?, ?)", (
            last_change or "-", start_time or "06:00", end_time or "22:00", start_time or "00:00", end_time or "05:00",
        ))

    conn.commit()
    conn.close()


# ------------------------------
# Funktion: Lichtbutton aktivieren/deaktivieren
# ------------------------------
@callback(
    Output("licht-switch", "value"),
    Input("licht-interval", "n_intervals")  # Dummy Input, nur um beim Laden zu triggern
)
def update_light_switch(n):
    # Verbindung zur DB öffnen
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Status abfragen
    cursor.execute("SELECT status FROM Light WHERE rowid = 1")
    result = cursor.fetchone()  # liefert ein Tupel wie ('online')

    conn.close()  # Verbindung schließen

    if result:
        status = result[0]  # den Wert aus dem Tupel holen
        return status == "online"
    else:
        return False  # falls kein Eintrag existiert


# ------------------------------
# Funktion: Licht Uhrzeiten aktualisieren
# ------------------------------
@callback(
    [
        Output("licht-start-time", "value"),
        Output("licht-end-time", "value"),
        Output("second-licht-start-time", "value"),
        Output("second-licht-end-time", "value"),
    ],
    Input("admin-refresh-interval", "n_intervals")
)
def refresh_light_times(n):
    light_data = get_light_data()
    return (
        light_data["start_time"],
        light_data["end_time"],
        light_data["second_start_time"],
        light_data["second_end_time"],
    )


# ------------------------------
# Funktion: Pumpenwerte lesen
# ------------------------------
def get_pump_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT last_change, intervall, on_for FROM Pump LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "last_change": result[0],
            "intervall": result[1],
            "on_for": result[2],
        }
    else:
        return {
            "last_change": "-",
            "intervall": "10",
            "on_for": "10",
        }


# ------------------------------
# Funktion: Pumpenwerte schreiben
# ------------------------------
def update_pump_data(last_change=None, intervall=None, on_for=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Pump")
    exists = cursor.fetchone()[0]

    if exists:
        if last_change is not None:
            cursor.execute("UPDATE Pump SET last_change = ? WHERE ROWID = 1", (last_change,))
        if intervall is not None:
            cursor.execute("UPDATE Pump SET intervall = ? WHERE ROWID = 1", (intervall,))
        if on_for is not None:
            cursor.execute("UPDATE Pump SET on_for = ? WHERE ROWID = 1", (on_for,))
    else:
        cursor.execute("INSERT INTO Pump (last_change, intervall, on_for) VALUES (?, ?, ?)", (
            last_change or "-", intervall or "10", on_for or "10",
        ))

    conn.commit()
    conn.close()


# ------------------------------
# Funktion: Pumpenbutton aktivieren/deaktivieren
# ------------------------------
@callback(
    Output("pumpe-switch", "value"),
    Input("pumpe-interval", "n_intervals")  # Dummy Input, nur um beim Laden zu triggern
)
def update_pump_switch(n):
    # Verbindung zur DB öffnen
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Status abfragen
    cursor.execute("SELECT status FROM Pump WHERE rowid = 1")
    result = cursor.fetchone()  # liefert ein Tupel wie ('online')

    conn.close()  # Verbindung schließen

    if result:
        status = result[0]  # den Wert aus dem Tupel holen
        return status == "online"
    else:
        return False  # falls kein Eintrag existiert


# ------------------------------
# Funktion: Pumpentextfeld aktualisieren
# ------------------------------
@callback(
    [
        Output("pump-intervall", "value"),
        Output("pump-on-for", "value")
    ],
    Input("admin-refresh-interval", "n_intervals")
)
def refresh_pump_inputs(n):
    pump_data = get_pump_data()
    return pump_data["intervall"], pump_data["on_for"]


# ------------------------------
# Funktion: Lüfterwerte lesen
# ------------------------------
def get_fan_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT last_change, intervall, on_for FROM Fan LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "last_change": result[0],
            "intervall": result[1],
            "on_for": result[2],
        }
    else:
        return {
            "last_change": "-",
            "intervall": "10",
            "on_for": "10",
        }


# ------------------------------
# Funktion: Lüfterwerte schreiben
# ------------------------------
def update_fan_data(last_change=None, intervall=None, on_for=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Fan")
    exists = cursor.fetchone()[0]

    if exists:
        if last_change is not None:
            cursor.execute("UPDATE Fan SET last_change = ? WHERE ROWID = 1", (last_change,))
        if intervall is not None:
            cursor.execute("UPDATE Fan SET intervall = ? WHERE ROWID = 1", (intervall,))
        if on_for is not None:
            cursor.execute("UPDATE Fan SET on_for = ? WHERE ROWID = 1", (on_for,))
    else:
        cursor.execute("INSERT INTO Fan (last_change, intervall, on_for) VALUES (?, ?, ?)", (
            last_change or "-", intervall or "10", on_for or "10",
        ))

    conn.commit()
    conn.close()


# ------------------------------
# Funktion: Lüfterbutton aktivieren/deaktivieren
# ------------------------------
@callback(
    Output("luefter-switch", "value"),
    Input("luefter-interval", "n_intervals")
)
def update_fan_switch(n):
    # Verbindung zur DB öffnen
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Status abfragen
    cursor.execute("SELECT status FROM Fan WHERE rowid = 1")
    result = cursor.fetchone()  # liefert ein Tupel wie ('online')

    conn.close()  # Verbindung schließen

    if result:
        status = result[0]  # den Wert aus dem Tupel holen
        return status == "online"
    else:
        return False  # falls kein Eintrag existiert


# ------------------------------
# Funktion: Lüftertextfeld aktualisieren
# ------------------------------
@callback(
    [
        Output("fan-intervall", "value"),
        Output("fan-on-for", "value")
    ],
    Input("admin-refresh-interval", "n_intervals")
)
def refresh_fan_inputs(n):
    fan_data = get_fan_data()
    return fan_data["intervall"], fan_data["on_for"]


def get_last_change(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT last_change FROM {table_name} LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "-"


def get_data_from_db(table_name: str, value_column: str):
    if not table_name or not value_column:
        return [], []  # leere Listen zurückgeben, kein Graph

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now = datetime.now()
    past_24h = now - timedelta(hours=24)

    query = f"""
        SELECT timestamp, {value_column}
        FROM {table_name}
        WHERE datetime(timestamp) >= datetime(?) AND {value_column} IS NOT NULL
        ORDER BY timestamp
    """

    cursor.execute(query, (past_24h.strftime("%Y-%m-%d %H:%M:%S"),))
    rows = cursor.fetchall()
    conn.close()

    # Split in X and Y
    times = [row[0] for row in rows]
    values = [row[1] for row in rows]

    return times, values


def update_last_change(table_name, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    exists = cursor.fetchone()[0] > 0

    if exists:
        cursor.execute(f"UPDATE {table_name} SET last_change = ? WHERE ROWID = 1", (value,))
    else:
        cursor.execute(f"INSERT INTO {table_name} (last_change) VALUES (?)", (value,))

    conn.commit()
    conn.close()


# Neue Callbacks für die Zeitstempel-Aktualisierung
@callback(
    [
        Output("luefter-last-change", "children"),
        Output("pumpe-last-change", "children"),
        Output("licht-last-change", "children"),
    ],
    [
        Input("luefter-switch", "value"),
        Input("pumpe-switch", "value"),
        Input("pump-intervall", "value"),
        Input("pump-on-for", "value"),
        Input("licht-start-time", "value"),
        Input("licht-end-time", "value"),
        Input("licht-switch", "value"),
        Input("second-licht-start-time", "value"),
        Input("second-licht-end-time", "value"),
        Input("fan-intervall", "value"),
        Input("fan-on-for", "value"),
        Input("werte-refresh", "n_intervals"),
    ]
)
def update_timestamps(
        luefter_value, pumpe_value,
        pump_intervall, pump_on_for,
        start_time, end_time,
        licht_switch, second_start,
        second_end, fan_intervall,
        fan_on_for, n_intervals
):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # prüfen, welches Element den Callback ausgelöst hat
    triggered_id = ctx.triggered_id

    if triggered_id == "luefter-switch":
        update_last_change("Fan", current_time)

    elif triggered_id == "pumpe-switch":
        update_last_change("Pump", current_time)

    elif triggered_id in ["pump-intervall", "pump-on-for"]:
        update_pump_data(
            last_change=current_time,
            intervall=pump_intervall,
            on_for=pump_on_for,
        )

    elif triggered_id in ["fan-intervall", "fan-on-for"]:
        update_fan_data(
            last_change=current_time,
            intervall=fan_intervall,
            on_for=fan_on_for,
        )

    elif triggered_id in [
        "licht-start-time", "licht-end-time", "licht-switch",
        "second-licht-start-time", "second-licht-end-time"
    ]:
        update_light_data(
            last_change=current_time,
            start_time=start_time if triggered_id == "licht-start-time" else None,
            end_time=end_time if triggered_id == "licht-end-time" else None,
            second_start_time=second_start if triggered_id == "second-licht-start-time" else None,
            second_end_time=second_end if triggered_id == "second-licht-end-time" else None,
        )

    # Falls Interval getriggert hat oder Input getriggert wurde, Labels aktualisieren
    return [
        f"Last change: {get_last_change('Fan')}",
        f"Last change: {get_last_change('Pump')}",
        f"Last change: {get_light_data().get('last_change', '-')}",
    ]


# Die Callbacks bleiben gleich, aber update_graph wird angepasst:

@callback(
    [Output("sensor-graph", "figure"),
     Output("graph-container", "style")],
    [Input("fuellstand-graph-btn", "n_clicks"),
     Input("ph-graph-btn", "n_clicks"),
     Input("ec-graph-btn", "n_clicks"),
     Input("temp-graph-btn", "n_clicks"),
     Input("luft-graph-btn", "n_clicks"),
     ],
    prevent_initial_call=True
)
def update_graph(*args):
    ctx = callback_context
    if not ctx.triggered:
        return {}, {"display": "none"}

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    now = datetime.now()
    past_24h = now - timedelta(hours=24)

    title = "24h Verlauf: "
    table = None,
    column = None,

    if button_id == "fuellstand-graph-btn":
        title += "Füllstand"
        table, column = "Ultrasonic_Sensor", "value"
    elif button_id == "ph-graph-btn":
        title += "PH-Wert"
        table, column = "PH_Sensor", "value"
    elif button_id == "ec-graph-btn":
        title += "EC-Wert"
        table, column = "EC_Sensor", "value"
    elif button_id == "temp-graph-btn":
        title += "Temperatur"
        table, column = "Temp_Sensor", "value"
    elif button_id == "luft-graph-btn":
        title += "Luftfeuchtigkeit"
        table, column = "Humidity_Sensor", "value"

    if not table or not column:
        return {}, {"display": "none"}  # Kein Graph anzeigen, wenn ungültig

    times, values = get_data_from_db(table, column)

    fig = {
        "data": [{
            "x": times,
            "y": values,
            "type": "scatter",
            "mode": "lines+markers",
            "line": {"color": COLOR_SCHEME['accent']},
            "marker": {"color": COLOR_SCHEME['accent']},
            "hovertemplate": "%{y} °C<br>%{x|%d.%m.%y %H:%M} Uhr<extra></extra>"
        }],
        "layout": {
            "title": {"text": title, "font": {"color": COLOR_SCHEME['text_primary']}},
            "paper_bgcolor": COLOR_SCHEME['card_bg'],
            "plot_bgcolor": COLOR_SCHEME['card_bg'],
            "font": {"color": COLOR_SCHEME['text_primary']},
            "xaxis": {
                "type": "date",
                "range": [past_24h.isoformat(), now.isoformat()],  # expliziter Bereich
                "autorange": False,
                "tickformat": "%H:%M\n%d.%m",  # Stunden + Datum z. B.
                "gridcolor": COLOR_SCHEME['graph_grid'],
                "color": COLOR_SCHEME['text_primary'],
                "title": "Zeit"
            },
            "yaxis": {
                "gridcolor": COLOR_SCHEME['graph_grid'],
                "color": COLOR_SCHEME['text_primary'],
                "title": column
            }
        }
    }

    return fig, {"display": "block"}


def lade_aktuelle_werte():
    tabellen = ["Ultrasonic_Sensor", "PH_Sensor", "EC_Sensor", "Temp_Sensor", "Humidity_Sensor"]
    werte = {}

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for table in tabellen:
        cursor.execute(f"SELECT live_value FROM {table} LIMIT 1")
        result = cursor.fetchone()
        werte[table] = result[0] if result else "-"

    conn.close()
    return werte


@callback(
    [
        Output("fuellstand-wert", "children"),
        Output("ph-wert", "children"),
        Output("ec-wert", "children"),
        Output("temp-wert", "children"),
        Output("luft-wert", "children"),
    ],
    Input("werte-refresh", "n_intervals")
)
def update_sensorwerte(n):
    werte = lade_aktuelle_werte()
    return (
        f"{werte['Ultrasonic_Sensor']}%",
        f"{werte['PH_Sensor']}",
        f"{werte['EC_Sensor']} mS/cm",
        f"{werte['Temp_Sensor']} °C",
        f"{werte['Humidity_Sensor']} %",
    )


@callback(
    Output("sensor_dropdown", "label"),
    Input("water_level_sensor_dropdown_button", "n_clicks"),
    Input("ph_sensor_dropdown_button", "n_clicks"),
    Input("ec_sensor_dropdown_button", "n_clicks"),
    Input("temp_sensor_dropdown_button", "n_clicks"),
    Input("humidity_sensor_dropdown_button", "n_clicks"),
    Input("all_sensor_dropdown_button", "n_clicks")
)
def update_sensor_dropdown_label(n1, n2, n3, n4, n5, n6):
    if not ctx.triggered_id:
        return "Sensoren auswählen",

    mapping = {
        "water_level_sensor_dropdown_button": "Füllstand",
        "ph_sensor_dropdown_button": "PH",
        "ec_sensor_dropdown_button": "EC",
        "temp_sensor_dropdown_button": "Temp",
        "humidity_sensor_dropdown_button": "Luftfeuchtigkeit",
        "all_sensor_dropdown_button": "Alle Sensoren",
    }

    label = mapping.get(ctx.triggered_id, "Sensoren auswählen")
    return label


@callback(
    Output("time_dropdown", "label"),
    Input("hour_dropdown_button", "n_clicks"),
    Input("days_dropdown_button", "n_clicks"),
)
def update_time_dropdown_label(n1, n2):
    if not ctx.triggered_id:
        return "Zeiteinheit auswählen"

    mapping = {
        "hour_dropdown_button": "Stunden",
        "days_dropdown_button": "Tage",
    }

    return mapping.get(ctx.triggered_id, "Zeiteinheit auswählen")


# ------------------------------
# Funktion: Sensor-Daten aus SQLite laden
# ------------------------------
def get_sensor_data(sensor_label, number_value, time_unit):
    """
    Lädt Daten aus SQLite basierend auf Sensor, Anzahl und Zeiteinheit.

    Parameter:
    - sensor_label: Name des Sensors (z.B. "Füllstand")
    - number_value: Anzahl der Zeiteinheiten
    - time_unit: "Stunden" oder "Tage"

    Rückgabe:
    - pandas DataFrame mit Spalten: value, timestamp
    """
    # Mapping Dropdown-Label → Tabellenname in der DB
    table_mapping = {
        "Füllstand": "Ultrasonic_Sensor",
        "PH": "PH_Sensor",
        "EC": "EC_Sensor",
        "Temp": "Temp_Sensor",
        "Luftfeuchtigkeit": "Humidity_Sensor",
        "Alle Sensoren": None
    }

    table_name = table_mapping.get(sensor_label)
    db_path = r"C:\Users\steve\PycharmProjects\Farming-Station\SQLite\sensors.db"
    conn = sqlite3.connect(db_path)

    # ------------------------------
    # Berechne Zeitgrenze für Filterung
    # ------------------------------
    now = datetime.now()
    if time_unit.lower().startswith("stunde"):
        time_limit = now - timedelta(hours=number_value)
    else:  # Tage
        time_limit = now - timedelta(days=number_value)
    time_limit_str = time_limit.strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------
    # Daten abfragen
    # ------------------------------
    if table_name:  # Einzelner Sensor
        query = f"""
            SELECT value, timestamp
            FROM {table_name}
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """
        df = pd.read_sql_query(query, conn, params=(time_limit_str,))
    else:  # Alle Sensoren
        dfs = []
        for tname in ["Ultrasonic_Sensor", "PH_Sensor", "EC_Sensor", "Temp_Sensor", "Humidity_Sensor"]:
            q = f"""
                SELECT value, timestamp
                FROM {tname}
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """
            dfs.append(pd.read_sql_query(q, conn, params=(time_limit_str,)))
        df = pd.concat(dfs, ignore_index=True)

    conn.close()
    return df


# ------------------------------
# Callback: CSV-Download generieren
# ------------------------------
@callback(
    Output("download", "data"),
    Input("download_button", "n_clicks"),
    State("sensor_dropdown", "label"),
    State("number", "value"),
    State("time_dropdown", "label"),
    prevent_initial_call=True
)
def download_sensor_data(n_clicks, sensor_label, number_value, time_unit):
    """
    Generiert eine CSV-Datei zum Download basierend auf den ausgewählten Sensoren,
    der Anzahl der Zeiteinheiten und der Zeiteinheit (Stunden/Tage).
    """
    # ------------------------------
    # Prüfen, ob alle Inputs gesetzt sind
    # ------------------------------
    if not sensor_label or number_value is None or not time_unit:
        return None

    # ------------------------------
    # Daten abrufen
    # ------------------------------
    df = get_sensor_data(sensor_label, number_value, time_unit)

    # ------------------------------
    # CSV zum Download zurückgeben
    # ------------------------------
    filename = f"{sensor_label}_{number_value}_{time_unit}.csv"
    return dcc.send_data_frame(df.to_csv, filename, index=False)


# ------------------------------
# Funktion: Log Datenstruktur
# ------------------------------
def add_log(event_type, component, value=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "event": event_type,
        "component": component,
        "value": value
    }
    log_data.append(log_entry)

    # CSV schreiben (append)
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "event", "component", "value"])
        if not file_exists:  # Header nur einmal schreiben
            writer.writeheader()
        writer.writerow(log_entry)


# ------------------------------
# Funktion: Log Updaten
# ------------------------------
@callback(
    Output("error-log", "value", allow_duplicate=True),
    Input("log-update", "n_intervals"),
    prevent_initial_call=True
)
def update_log_text(n):
    if not os.path.exists(LOG_FILE):
        return ""

    df = pd.read_csv(LOG_FILE)
    return "\n".join([
        f"{row['timestamp']} | {row['event']} | {row['component']} | {row['value']}"
        for _, row in df.iterrows()
    ])


# ------------------------------
# Funktion: Log Downloaden
# ------------------------------
@callback(
    Output("download-log", "data"),
    Input("download-btn", "n_clicks"),
    prevent_initial_call=True,
    allow_duplicate=True
)
def download_log(n_clicks):
    if os.path.exists(LOG_FILE):
        return dcc.send_file(LOG_FILE)  # Direkt die bestehende CSV liefern
    return None


# ------------------------------
# Funktion: Log leeren
# ------------------------------
@callback(
    Output("error-log", "value", allow_duplicate=True),  # Textarea sofort leeren
    Input("clear-log-btn", "n_clicks"),  # Button klick
    prevent_initial_call=True
)
def clear_log(n_clicks):
    global log_data
    log_data = []

    # CSV leeren
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "event", "component", "value"])
        writer.writeheader()  # Header bleibt bestehen, Inhalt wird gelöscht

    return ""


# ------------------------------
# Funktion: Sensoren überprüfen
# ------------------------------
SENSOR_LIMITS = {
    "EC_Sensor": (0.6, 1.8),
    "Humidity_Sensor": (20, 80),
    "PH_Sensor": (5.5, 7.5),
    "Temp_Sensor": (18, 30),
    "Ultrasonic_Sensor": (30, 99),
    "WaterLevel_Sensor": (0, 25),
}
SENSOR_STATUS = {
    "Fan": None,
    "Light": None,
    "Pump": None,
    "FlowRate_Sensor": None
}


def check_sensors():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        for sensor, (low, high) in SENSOR_LIMITS.items():
            result = cursor.execute(f"SELECT live_value FROM {sensor}").fetchone()
            if result:
                value = result[0]
                if value < low or value > high:
                    add_log("WARNING", sensor, value)

        for sensor_name in SENSOR_STATUS:
            result = cursor.execute(f"SELECT status FROM {sensor_name}").fetchone()
            if result:
                status = result[0]  # z.B. "ON" oder "OFF"

                # Nur loggen, wenn sich der Status geändert hat
                if SENSOR_STATUS[sensor_name] != status:
                    SENSOR_STATUS[sensor_name] = status
                    add_log("INFO", sensor_name, status)


# ------------------------------
# Funktion: check_sensors aufrufen
# ------------------------------
@callback(
    Output("dummy-output", "children"),  # Dummy
    Input("log-update", "n_intervals")
)
def periodic_sensor_check(n):
    check_sensors()  # füllt log_data bei Grenzwertverletzungen
    return ""
