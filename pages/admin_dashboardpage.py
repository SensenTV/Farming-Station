import dash_bootstrap_components as dbc
from dash import html, Output, Input, dcc, callback, dash, callback_context
import plotly.graph_objs as go
from datetime import datetime
import json
from dash.dependencies import State
import os

# Funktion zum Laden der gespeicherten Zeitstempel
def load_timestamps():
    try:
        with open('switch_timestamps.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"luefter": "-", "pumpe": "-"}

# Funktion zum Speichern der Zeitstempel
def save_timestamps(timestamps):
    with open('switch_timestamps.json', 'w') as f:
        json.dump(timestamps, f)

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
}

def admin_dashboard_layout():
    # Lade gespeicherte Zeitstempel
    timestamps = load_timestamps()
    
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
                    html.Div([
                        html.Strong("Füllstand: ", style={"color": COLOR_SCHEME['text_primary']}),
                        html.Span(id="fuellstand-wert", children="-", style={"color": COLOR_SCHEME['accent']}),
                        dbc.Button("Graph", id="fuellstand-graph-btn", size="sm",
                                 className="ms-2", color="primary")
                    ],
                    className="mb-2"),
                    html.Div([
                        html.Strong("PH: ", style={"color": COLOR_SCHEME['text_primary']}),
                        html.Span(id="ph-wert", children="-", style={"color": COLOR_SCHEME['accent']}),
                        dbc.Button("Graph", id="ph-graph-btn", size="sm",
                                 className="ms-2", color="primary")
                    ],
                    className="mb-2"),
                    html.Div([
                        html.Strong("EC: ", style={"color": COLOR_SCHEME['text_primary']}),
                        html.Span(id="ec-wert", children="-", style={"color": COLOR_SCHEME['accent']}),
                        dbc.Button("Graph", id="ec-graph-btn", size="sm",
                                 className="ms-2", color="primary")
                    ],
                    className="mb-2"),
                    html.Div([
                        html.Strong("Temp: ", style={"color": COLOR_SCHEME['text_primary']}),
                        html.Span(id="temp-wert", children="-", style={"color": COLOR_SCHEME['accent']}),
                        dbc.Button("Graph", id="temp-graph-btn", size="sm",
                                 className="ms-2", color="primary")
                    ],
                    className="mb-2"),
                    html.Div([
                        html.Strong("Luftfeuchtigkeit: ", style={"color": COLOR_SCHEME['text_primary']}),
                        html.Span(id="luft-wert", children="-", style={"color": COLOR_SCHEME['accent']}),
                        dbc.Button("Graph", id="luft-graph-btn", size="sm",
                                 className="ms-2", color="primary")
                    ], className="mb-2"),
                ], md=6),

                dbc.Col([
                    html.Div(
                        dcc.Graph(id="sensor-graph", style={"height": "300px"}),
                        id="graph-container",
                        style={"display": "none"}  # Anfangs versteckt
                    )
                ], md=6)

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
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col(
                                    html.Span("Lüfter", style={
                                        "color": COLOR_SCHEME['text_primary'],
                                        "font-weight": "500"
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
                                f"Last change: {timestamps['luefter']}",
                                id="luefter-last-change",
                                className="d-block mt-2",
                                style={"color": COLOR_SCHEME['text_secondary']}
                            )
                        ])
                    ], className="mb-3", style={"background-color": COLOR_SCHEME['control_bg']}),
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col(
                                    html.Span("Wasserpumpe", style={
                                        "color": COLOR_SCHEME['text_primary'],
                                        "font-weight": "500"
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
                                f"Last change: {timestamps['pumpe']}",
                                id="pumpe-last-change",
                                className="d-block mt-2",
                                style={"color": COLOR_SCHEME['text_secondary']}
                            )
                        ])
                    ], className="mb-3", style={"background-color": COLOR_SCHEME['control_bg']}),
                ], md=6),
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

# Neue Callbacks für die Zeitstempel-Aktualisierung
@callback(
    [Output("luefter-last-change", "children"),
     Output("pumpe-last-change", "children")],
    [Input("luefter-switch", "value"),
     Input("pumpe-switch", "value")]
)
def update_timestamps(luefter_value, pumpe_value):
    ctx = callback_context
    if not ctx.triggered:
        timestamps = load_timestamps()
        return [
            f"Last change: {timestamps['luefter']}",
            f"Last change: {timestamps['pumpe']}"
        ]

    timestamps = load_timestamps()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if ctx.triggered[0]["prop_id"].split(".")[0] == "luefter-switch":
        timestamps["luefter"] = current_time
    elif ctx.triggered[0]["prop_id"].split(".")[0] == "pumpe-switch":
        timestamps["pumpe"] = current_time
    
    save_timestamps(timestamps)
    
    return [
        f"Last change: {timestamps['luefter']}",
        f"Last change: {timestamps['pumpe']}"
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
    times = [datetime.now().strftime("%H:%M") for _ in range(24)]
    values = [0] * 24

    title = "24h Verlauf: "
    if button_id == "fuellstand-graph-btn":
        title += "Füllstand"
    elif button_id == "ph-graph-btn":
        title += "PH-Wert"
    elif button_id == "ec-graph-btn":
        title += "EC-Wert"
    elif button_id == "temp-graph-btn":
        title += "Temperatur"
    elif button_id == "luft-graph-btn":
        title += "Luftfeuchtigkeit"

    fig = {
        "data": [{
            "x": times,
            "y": values,
            "type": "scatter",
            "mode": "lines+markers",
            "line": {"color": COLOR_SCHEME['accent']},
            "marker": {"color": COLOR_SCHEME['accent']}
        }],
        "layout": {
            "title": {"text": title, "font": {"color": COLOR_SCHEME['text_primary']}},
            "paper_bgcolor": COLOR_SCHEME['card_bg'],
            "plot_bgcolor": COLOR_SCHEME['card_bg'],
            "font": {"color": COLOR_SCHEME['text_primary']},
            "xaxis": {
                "gridcolor": COLOR_SCHEME['graph_grid'],
                "color": COLOR_SCHEME['text_primary']
            },
            "yaxis": {
                "gridcolor": COLOR_SCHEME['graph_grid'],
                "color": COLOR_SCHEME['text_primary']
            }
        }
    }

    return fig, {"display": "block"}
