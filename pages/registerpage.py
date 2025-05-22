from dash import html, dcc

def register_layout():
    return html.Div([
        html.H2("Register"),
        dcc.Input(id='username', placeholder='Username', type='text'),
        dcc.Input(id='password', placeholder='Password', type='password'),
        dcc.Input(id='confirm_password', placeholder='Confirm Password', type='password'),
        html.Button('Register', id='register-button', n_clicks=0, style={'marginLeft': '10px'}),
        html.Div(id='register-output', style={'color': 'red', 'marginTop': '10px'}),
        dcc.Link('Back to Login', href='/'),
    ])