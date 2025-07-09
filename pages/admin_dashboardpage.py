from dash import html, Output, Input, dcc, callback, dash, callback_context
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash.dependencies import State
import plotly.graph_objs as go
from datetime import datetime
import sqlite3
import json
import os

DB_PATH = r"C:\Users\steve\PycharmProjects\Farming-Station\SQLight\sensors.db"

# Aktualisiertes Farbschema
COLOR_SCHEME = {
    'background': '#ffffff',    # Weißer Hintergrund
    'card_bg': '#f8f9fa',      # Helles Grau für Karten
    'accent': '#2563eb',       # Moderne Blau Akzentfarbe
    'text_primary': '#1e293b', # Dunkles Blau-Grau für Text
    'text_secondary': '#64748b',# Mittleres Grau für sekundären Text
    'success': '#22c55e',      # Grün für positive Status
    'warning': '#f59e0b',      # Orange für Warnungen
    'border': '#e2e8f0',       # Hellgrau für Borders
    'graph_grid': '#e2e8f0',   # Hellgrau für Graphenraster
    'log_bg': '#e5e7eb',       # Leicht dunkleres Grau für Log/Kamera Bereiche
    'control_bg': '#e5e7eb',   # Leicht dunkleres Grau für Steuerungselemente
    'transparent': 'rgba(0, 0, 0, 0)',  # komplett transparent
}

def admin_dashboard_layout():
    # Lade gespeicherte Zeitstempel
    licht_data = get_light_data()
    start_time = licht_data.get("start_time")
    end_time = licht_data.get("end_time")
    
    system_card = dbc.Card([
        dbc.CardHeader(
            html.H3("System 1", style={"color": COLOR_SCHEME['text_primary']}),
            style={"background-color": COLOR_SCHEME['card_bg']}
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
                                dbc.Button("Graph", id="fuellstand-graph-btn", size="sm", color="primary"),
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
                                dbc.Button("Graph", id="ph-graph-btn", size="sm", color="primary"),
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
                                dbc.Button("Graph", id="ec-graph-btn", size="sm", color="primary"),
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
                                dbc.Button("Graph", id="temp-graph-btn", size="sm", color="primary"),
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
                                dbc.Button("Graph", id="luft-graph-btn", size="sm", color="primary"),
                                className="d-flex justify-content-end",
                                width=True,
                            ),
                        ], align="center", className="mb-2"),
                    ], style={"background-color": COLOR_SCHEME['transparent'], "width": "27%", "border": "none"}),
                ], md=6),

                dbc.Col([
                    html.Div(
                        dcc.Graph(
                            id="sensor-graph",
                            style={"height": "300px"},
                            config = {
                                "displayModeBar": True,
                                "modeBarButtonsToRemove": [
                                    "zoom2d", "select2d", "lasso2d",
                                    "autoscale2d"
                                ],
                                "displaylogo": False
                            }
                        ),
                        id="graph-container",
                        style={"display": "none"}
                    )
                ], md=6),
                dcc.Interval(id='werte-refresh', interval=5000, n_intervals=0)
            ]),



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

            # Steuerungselemente
            dbc.Row([

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
                                        value=False,
                                        className="float-end"
                                    ),
                                    className="d-flex justify-content-end"
                                ),
                            ]),
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
                                        value=False,
                                        className="float-end"
                                    ),
                                    className="d-flex justify-content-end"
                                ),
                            ]),

                            # Zeiteinstellung
                            html.Div([
                                dbc.Label("Eingeschaltet von:", html_for="licht-start-time", className="me-2 mb-0", style={"color": COLOR_SCHEME['text_primary']}),
                                dmc.TimeInput(
                                    id="licht-start-time",
                                    value=licht_data["start_time"],
                                    placeholder="HH:mm",
                                    className="me-2",
                                    size="sm"
                                ),
                                dbc.Label("bis:", html_for="licht-end-time", className="me-2 mb-0", style={"color": COLOR_SCHEME['text_primary']}),
                                dmc.TimeInput(
                                    id="licht-end-time",
                                    value=licht_data["end_time"],
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
                    ],className="mb-3", style={"background-color": COLOR_SCHEME['control_bg'], "width": "100%"}),
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
                                        value=False,
                                        className="float-end"
                                    ),
                                    className="d-flex justify-content-end"
                                ),
                            ]),
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
        ], style={"background-color": COLOR_SCHEME['card_bg']})
    ], className="shadow-sm")

    return dbc.Container(
        dbc.Row([
            dbc.Col(system_card, width=12)
        ], className="g-0 vh-100 py-4"),
        fluid=True,
        style={"background-color": COLOR_SCHEME['background']}
    )
# Werte lesen
def get_light_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT last_change, start_time, end_time FROM Light LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "last_change": result[0],
            "start_time": result[1],
            "end_time": result[2]
        }
    else:
        return {
            "last_change": "-",
            "start_time": "06:00",
            "end_time": "22:00"
        }

def get_last_change(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT last_change FROM {table_name} LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "-"

def get_data_from_db(table_name: str, value_column: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now = datetime.now()
    past_24h = now - timedelta(hours=24)

    query = f"""
        SELECT timestamp, {value_column}
        FROM {table_name}
        WHERE timestamp >= ?
        ORDER BY timestamp
    """

    cursor.execute(query, (past_24h.strftime("%Y-%m-%d %H:%M:%S"),))
    rows = cursor.fetchall()
    conn.close()

    # Split in X and Y
    times = [row[0] for row in rows]
    values = [row[1] for row in rows]

    return times, values


# Werte schreiben
def update_light_data(last_change=None, start_time=None, end_time=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Existiert schon ein Eintrag?
    cursor.execute("SELECT COUNT(*) FROM Light")
    exists = cursor.fetchone()[0] > 0

    if exists:
        if last_change is not None:
            cursor.execute("UPDATE Light SET last_change = ?", (last_change,))
        if start_time is not None:
            cursor.execute("UPDATE Light SET start_time = ?", (start_time,))
        if end_time is not None:
            cursor.execute("UPDATE Light SET end_time = ?", (end_time,))
    else:
        # Fallback-Eintrag
        cursor.execute("INSERT INTO Light (last_change, start_time, end_time) VALUES (?, ?, ?)", (
            last_change or "-", start_time or "06:00", end_time or "22:00"
        ))

    conn.commit()
    conn.close()

def update_last_change(table_name, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    exists = cursor.fetchone()[0] > 0

    if exists:
        cursor.execute(f"UPDATE {table_name} SET last_change = ?", (value,))
    else:
        cursor.execute(f"INSERT INTO {table_name} (last_change) VALUES (?)", (value,))

    conn.commit()
    conn.close()


# Neue Callbacks für die Zeitstempel-Aktualisierung
@callback(
    [Output("luefter-last-change", "children"),
     Output("pumpe-last-change", "children"),
     Output("licht-last-change", "children")],
    [Input("luefter-switch", "value"),
     Input("pumpe-switch", "value"),
     Input("licht-start-time", "value"),
     Input("licht-end-time", "value"),
     Input("licht-switch", "value")]
)
def update_timestamps(luefter_value, pumpe_value, start_time, end_time, licht_switch):
    ctx = callback_context
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if ctx.triggered:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger_id == "luefter-switch":
            update_last_change("Fan", current_time)

        elif trigger_id == "pumpe-switch":
            update_last_change("Pump", current_time)

        elif trigger_id in ["licht-start-time", "licht-end-time", "licht-switch"]:
            update_light_data(
                last_change=current_time,
                start_time=start_time if trigger_id == "licht-start-time" else None,
                end_time=end_time if trigger_id == "licht-end-time" else None
            )

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
     Input("luft-graph-btn", "n_clicks")],
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
    table = ""
    column = ""

    if button_id == "fuellstand-graph-btn":
        title += "Füllstand"
        table, column = "WaterLevel_Sensor", "value"
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
    tabellen = ["WaterLevel_Sensor", "PH_Sensor", "EC_Sensor", "Temp_Sensor", "Humidity_Sensor"]
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
        f"{werte['WaterLevel_Sensor']}%",
        f"{werte['PH_Sensor']}",
        f"{werte['EC_Sensor']} mS/cm",
        f"{werte['Temp_Sensor']} °C",
        f"{werte['Humidity_Sensor']} %",
    )


