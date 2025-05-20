from dash import Dash, html, dcc, Output, Input, State
import dash
import sqlite3
import bcrypt
from pages.loginpage import login_layout  # Deine Login-/Registrier-Oberfläche
from ui.auth import verify_user  # Funktion zur Passwortprüfung

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Farming Station"

# Layout mit Platzhalter für dynamischen Seiteninhalt
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])

# Temporärer Login-Speicher
session = {"logged_in": False}

# Routing: Zeigt Login- oder Dashboard-Ansicht
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if session.get("logged_in"):
        return html.Div([
            html.H2("Willkommen! Du bist eingeloggt."),
            html.Button("Logout", id="logout-button", n_clicks=0)
        ])
    return login_layout()

# Login & Registrierung in einem Callback
@app.callback(
    Output('login-output', 'children'),
    Input('login-button', 'n_clicks'),
    Input('register-button', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value'),
    State('confirm-password', 'value'),
    prevent_initial_call=True
)
def handle_auth(login_clicks, register_clicks, username, password, confirm_password):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if not username or not password:
        return "Bitte Benutzername und Passwort eingeben."

    if trigger_id == 'login-button':
        if verify_user(username, password):
            session["logged_in"] = True
            return dcc.Location(pathname='/', id='redirect')
        else:
            return "Benutzername oder Passwort falsch."

    elif trigger_id == 'register-button':
        if password != confirm_password:
            return "Die Passwörter stimmen nicht überein."

        # Passwort sicher hashen
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            conn = sqlite3.connect('SQLight/users.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            conn.close()
            return "Registrierung erfolgreich! Du kannst dich jetzt einloggen."
        except sqlite3.IntegrityError:
            return "Benutzername existiert bereits."

# Optional: Logout-Funktion vorbereiten
@app.callback(
    Output('url', 'pathname'),
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def logout(n_clicks):
    session["logged_in"] = False
    return "/"

if __name__ == '__main__':
    app.run(debug=True)
