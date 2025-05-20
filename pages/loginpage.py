from dash import html, dcc

def login_layout():
    return html.Div([
        html.H2("Login or Register"),
        dcc.Input(id='username', placeholder='Username', type='text'),
        dcc.Input(id='password', placeholder='Password', type='password'),
        dcc.Input(id='confirm-password', placeholder='Confirm Password (for register)', type='password'),
        html.Button('Login', id='login-button', n_clicks=0),
        html.Button('Register', id='register-button', n_clicks=0, style={'marginLeft': '10px'}),
        html.Div(id='login-output', style={'color': 'red', 'marginTop': '10px'}),
    ])
