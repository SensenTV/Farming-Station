from dash import html, dcc

def login_layout():
    return html.Div([
        html.H2("Login"),
        dcc.Input(id='username', placeholder='Username', type='text'),
        dcc.Input(id='password', placeholder='Password', type='password'),
        html.Button('Login', id='login-button', n_clicks=0),
        html.Br(),
        dcc.Link('Register', href='/register'),
        html.Div(id='login-output', style={'color': 'red', 'marginTop': '10px'}),
    ])
