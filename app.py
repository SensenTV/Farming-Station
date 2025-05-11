from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

app = Dash()

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

])

if __name__ == '__main__':
    app.run(debug=True)