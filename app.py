from dash import Dash, html, dcc, Output, Input, State
import dash
import dash_bootstrap_components as dbc
import sqlite3
import bcrypt
import dash_mantine_components as dmc
from pages.loginpage import login_layout  # Login-Oberfläche
from pages.registerpage import register_layout  # Registrier-Oberfläche
from authentification.auth import verify_user  # Funktion zur Passwortprüfung
from pages.user_dashboardpage import user_dashboard_layout
from pages.admin_dashboardpage import admin_dashboard_layout
from apscheduler.schedulers.background import BackgroundScheduler
from SQLite import data_deletion


app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Farming Station"

# Layout mit Platzhalter für dynamischen Seiteninhalt
app.layout = dmc.MantineProvider(
    withGlobalClasses=True,
    withCssVariables=True,
    children=[
        dbc.Container([
            dcc.Location(id='url', refresh=False),
            dcc.Store(id='session-store', storage_type='session'),  # session = Tab/Browser geöffnet
            html.Div(id='page-content'),
        ], fluid=True),
        html.Div([
            html.Meta(name='viewport', content='width=device-width, initial-scale=1.0, shrink-to-fit=yes'),
        ]),
    ]
)


# Routing: Zeigt Login- oder Dashboard-Ansicht
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('session-store', 'data')
)
def display_page(pathname, session_data):
    if session_data and session_data.get("logged_in"):

        # Admin Dashboard
        if pathname == "/admin" and session_data.get("role") == "admin":
            return admin_dashboard_layout()

        # User Dashboard
        elif pathname == "/user" and session_data.get("role") == "user":
            return user_dashboard_layout()

        # Default Dashboard, wenn kein spezieller Pfad
        elif session_data.get("role") == "admin":
            return admin_dashboard_layout()
        elif session_data.get("role") == "user":
            return user_dashboard_layout()

        # Falls Rolle unbekannt, Logout erzwingen oder Login anzeigen
        else:
            return login_layout()

    # Für Register-Seite
    if pathname == "/register":
        return register_layout()

    # Standard: Login-Seite
    return login_layout()


# Login Callback: Session in dcc.Store speichern und redirect setzen
@app.callback(
    Output('login-output', 'children'),
    Output('session-store', 'data', allow_duplicate=True),
    Output('url', 'pathname', allow_duplicate=True),
    Input('login-button', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value'),
    prevent_initial_call=True
)
def handle_login(login_clicks, username, password):
    if not username or not password:
        return dbc.Alert("Bitte Benutzername und Passwort eingeben.", color="danger"), dash.no_update, dash.no_update

    valid, role = verify_user(username, password)

    if valid:
        session_data = {"logged_in": True, "role": role}
        if role == "admin":
            return dash.no_update, session_data, '/admin'
        else:
            return dash.no_update, session_data, '/user'

    return dbc.Alert("Benutzername oder Passwort falsch", color="danger"), dash.no_update, dash.no_update


@app.callback(
    Output('register-output', 'children'),
    Input('register-button', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value'),
    State('confirm_password', 'value'),
    prevent_initial_call=True
)
def handle_register(register_clicks, username, password, confirm_password):
    if not username or not password or not confirm_password:
        return dbc.Alert("Bitte alle Felder ausfüllen.", color="danger")

    if password != confirm_password:
        return dbc.Alert("Die Passwörter stimmen nicht überein.", color="danger")

    # Passwort sicher hashen
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

# Logout Callback: Session leeren und zurück zum Login
@app.callback(
    Output('session-store', 'data', allow_duplicate=True),
    Output('url', 'pathname', allow_duplicate=True),
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def logout(n_clicks):
    return {}, '/'

scheduler = BackgroundScheduler()
# Methode ohne () übergeben!
scheduler.add_job(data_deletion.delete_old_data, 'cron', hour=0, minute=1)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
