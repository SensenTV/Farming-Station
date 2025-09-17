from flask import Flask, session as flask_session
from dash import Dash, html, dcc, Output, Input, State, ALL
import dash
import dash_bootstrap_components as dbc
import sqlite3
import bcrypt
import dash_mantine_components as dmc
from pages.loginpage import login_layout
from pages.registerpage import register_layout
from authentification.auth import verify_user
from pages.user_dashboardpage import user_dashboard_layout
from pages.admin_dashboardpage import admin_dashboard_layout
from apscheduler.schedulers.background import BackgroundScheduler
from SQLite import data_deletion
from Sensors import sensors
from Sensors.dht_sensor_test import read_dht
import asyncio

# ----------------- Flask Server -----------------
server = Flask(__name__)
server.secret_key = "ein_geheimes_schluesselwort"

# ----------------- Dash App -----------------
app = Dash(__name__, server=server, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Farming Station"

# ----------------- Layout -----------------
app.layout = dmc.MantineProvider(
    withGlobalClasses=True,
    withCssVariables=True,
    children=[
        dbc.Container([
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content'),
        ], fluid=True),
        html.Div([
            html.Meta(name='viewport', content='width=device-width, initial-scale=1.0, shrink-to-fit=yes'),
        ]),
    ]
)

# ----------------- Page Routing -----------------
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
)
def display_page(pathname):
    if flask_session.get('logged_in'):
        role = flask_session.get('role')
        if pathname == "/admin" and role == "admin":
            return admin_dashboard_layout()
        elif pathname == "/user" and role == "user":
            return user_dashboard_layout()
        elif role == "admin":
            return admin_dashboard_layout()
        elif role == "user":
            return user_dashboard_layout()
        else:
            return login_layout()
    if pathname == "/register":
        return register_layout()
    return login_layout()

# ----------------- Login Callback -----------------
@app.callback(
    Output('login-output', 'children'),
    Output('url', 'pathname', allow_duplicate=True),
    Input('login-button', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value'),
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    if not n_clicks:  # Kein Klick, nichts anzeigen
        raise dash.exceptions.PreventUpdate

    if not username or not password:
        return dbc.Alert("Bitte Benutzername und Passwort eingeben.", color="danger"), dash.no_update

    valid, role = verify_user(username, password)
    if valid:
        flask_session['logged_in'] = True
        flask_session['role'] = role
        return dash.no_update, '/admin' if role == 'admin' else '/user'

    return dbc.Alert("Benutzername oder Passwort falsch", color="danger"), dash.no_update

# ----------------- Register Callback -----------------
@app.callback(
    Output('register-output', 'children'),
    Input('register-button', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value'),
    State('confirm_password', 'value'),
    prevent_initial_call=True
)
def handle_register(n_clicks, username, password, confirm_password):
    if not username or not password or not confirm_password:
        return dbc.Alert("Bitte alle Felder ausfüllen.", color="danger")
    if password != confirm_password:
        return dbc.Alert("Die Passwörter stimmen nicht überein.", color="danger")

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        conn = sqlite3.connect('SQLite/users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        return dbc.Alert("Registrierung erfolgreich! Du kannst dich jetzt einloggen.", color="success")
    except sqlite3.IntegrityError:
        return dbc.Alert("Benutzername existiert bereits.", color="danger")

# ----------------- Logout Callback -----------------
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input({'type': 'logout-btn', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def logout(n_clicks_list):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    flask_session.clear()
    return '/'

# ----------------- Scheduler -----------------
scheduler = BackgroundScheduler()
scheduler.add_job(data_deletion.delete_old_data, 'cron', hour=0, minute=1)
# scheduler.add_job(sensors.add_to_db, "interval", seconds=10)
#scheduler.add_job(sensors.sensor_activate, "interval", seconds=5, max_instances=1, coalesce=True, misfire_grace_time=10)
scheduler.start()

async def dht_loop():
    while True:
        await read_dht()
        await asyncio.sleep(5)

async def sensor_loop():
    while True:
        await sensors.sensor_activate()
        await asyncio.sleep(5)

async def db_add_loop():
    while True:
        await sensors.add_to_db()
        await asyncio.sleep(60)

async def main():
    # Sensor-Loop im Hintergrund starten
    asyncio.create_task(sensor_loop())
    asyncio.create_task(dht_loop())
    asyncio.create_task(db_add_loop())

    # Dash im Executor laufen lassen (blockierend)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: app.run(host='0.0.0.0', port=8050))

# ----------------- App starten -----------------
if __name__ == '__main__':
    asyncio.run(main())
    #app.run(debug=True, host='0.0.0.0', port=8050)
