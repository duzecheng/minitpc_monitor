from dash import Dash, html, dcc, callback, Output, Input
import dash_daq as daq
# from dash.exceptions import PreventUpdate
import plotly.express as px

import pandas as pd

import datetime

import numpy as np
from json import loads, dumps

# Constants
R = 8.31  # Universal gas constant in J/(mol*K)
T = 298  # Room temperature in K
mu = 131.5  # Molar mass of Xe in g/mol (assuming Xe)

PATH = "./data/test.log"

with open('./python/config.json',"r") as config_file:
    SLEEP = loads(config_file.readline())['sleep']

# plot definition
df = pd.read_csv(PATH)

trange = [pd.to_datetime(df.iloc[-1]['datetime'])-pd.Timedelta('1 day'), pd.to_datetime(df.iloc[-1]['datetime'])]

ax_temp_A = px.line(x=df['datetime'], y=df['tempA'], labels={'x': '', 'y': f"temp({chr(0xb0)}C)"}, title="Temperature A")
ax_temp_A.update_xaxes(range=trange)
ax_temp_B = px.line(x=df['datetime'], y=df['tempB'], labels={'x': '', 'y': f"temp({chr(0xb0)}C)"}, title="Temperature B")
ax_temp_B.update_xaxes(range=trange)
ax_strain_A = px.line(x=df['datetime'], y=df['massA'], labels={'x': '', 'y': 'mass(kg)'}, title="Mass A")
ax_strain_A.update_xaxes(range=trange)
ax_strain_B = px.line(x=df['datetime'], y=df['massB'], labels={'x': '', 'y': 'mass(kg)'}, title="Mass B")
ax_strain_B.update_xaxes(range=trange)
ax_pressure_high = px.line(x=df['datetime'], y=df['high_pressure'] * 10, labels={'x': '', 'y': 'pressure(bar)'}, title="Pressure high")
ax_pressure_high.update_xaxes(range=trange)
ax_pressure_low = px.line(x=df['datetime'], y=df['low_pressure'] * 1e-2, labels={'x': '', 'y': 'pressure(bar)'}, title="Pressure low")
ax_pressure_low.update_xaxes(range=trange)
ax_vaccum = px.line(x=df['datetime'], y=df['vaccum'], labels={'x': '', 'y': 'vaccum(pa)'}, title="Vaccum", log_y=True)
ax_vaccum.update_xaxes(range=trange)
ax_flow = px.line(x=df['datetime'], y=df['flow'], labels={'x': '', 'y': 'flow'}, title="Flow")
ax_flow.update_xaxes(range=trange)

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div(children='Minitpc Monitor',
             style={'textAlign': 'center', 'fontSize': '2em'}),
    html.Div(children='Time range(day)'),
    dcc.Slider(
        id='time-range',
        min=0.001,
        max=1,
        value=1),
    daq.Indicator(
        id='alert-indicator',
      label="alert",
      value=False
    ),
    daq.BooleanSwitch(id='alert', on=False),
    daq.LEDDisplay(
        id='xe-mass',
        label="Xe mass(kg)",
        value=0
    ),
    html.Button('Reset', id='reset-mass', n_clicks=0),
    html.Div([dcc.Graph(id='ax_temp_A', figure=ax_temp_A, style={'display': 'inline-block'}),
              dcc.Graph(id='ax_temp_B', figure=ax_temp_B, style={'display': 'inline-block'})]),
    html.Div([dcc.Graph(id='ax_strain_A', figure=ax_strain_A, style={'display': 'inline-block'}),
              dcc.Graph(id='ax_strain_B', figure=ax_strain_B, style={'display': 'inline-block'})]),
    html.Div([dcc.Graph(id='ax_pressure_high', figure=ax_pressure_high, style={'display': 'inline-block'}),
              dcc.Graph(id='ax_pressure_low', figure=ax_pressure_low, style={'display': 'inline-block'})]),
    html.Div([dcc.Graph(id='ax_vaccum', figure=ax_vaccum, style={'display': 'inline-block'}),
              dcc.Graph(id='ax_flow', figure=ax_flow, style={'display': 'inline-block'})]),
    dcc.Interval(id="graph-update", interval=SLEEP * 1000, n_intervals=0),
    dcc.Interval(id="set-update", interval=200, n_intervals=0)
])


# update plot
@callback(
    [Output('ax_temp_A', 'figure'),
    Output('ax_temp_B', 'figure'),
    Output('ax_strain_A', 'figure'),
    Output('ax_strain_B', 'figure'),
    Output('ax_pressure_high', 'figure'),
    Output('ax_pressure_low', 'figure'),
    Output('ax_vaccum', 'figure'),
    Output('ax_flow', 'figure'),
    Output('xe-mass', 'value')],
    Input('graph-update', 'n_intervals'),
    Input('time-range', 'value'),
    Input('xe-mass', 'value'),
)
def update_plot(n_intervals, t, m):
    
    df = pd.read_csv(PATH)
    dt = pd.Timedelta(f'{t} day')
    trange = [pd.to_datetime(df.iloc[-1]['datetime'])-dt, pd.to_datetime(df.iloc[-1]['datetime'])]

    p = df['low_pressure'].iloc[-1] * 1000
    f = df['flow'].iloc[-1] * 1e-3
    dm = (p * f * SLEEP * mu) / (R * T) / 60 / 1000
    m += dm
    
    ax_temp_A.data[0]['x'] = df['datetime']
    ax_temp_A.data[0]['y'] = df['tempA']
    ax_temp_A.update_xaxes(range=trange)
    ax_temp_B.data[0]['x'] = df['datetime']
    ax_temp_B.data[0]['y'] = df['tempB']
    ax_temp_B.update_xaxes(range=trange)
    ax_strain_A.data[0]['x'] = df['datetime']
    ax_strain_A.data[0]['y'] = df['massA']
    ax_strain_A.update_xaxes(range=trange)
    ax_strain_B.data[0]['x'] = df['datetime']
    ax_strain_B.data[0]['y'] = df['massB']
    ax_strain_B.update_xaxes(range=trange)
    ax_pressure_high.data[0]['x'] = df['datetime']
    ax_pressure_high.data[0]['y'] = df['high_pressure'] * 10
    ax_pressure_high.update_xaxes(range=trange)
    ax_pressure_low.data[0]['x'] = df['datetime']
    ax_pressure_low.data[0]['y'] = df['low_pressure'] * 1e-2
    ax_pressure_low.update_xaxes(range=trange)
    ax_vaccum.data[0]['x'] = df['datetime']
    ax_vaccum.data[0]['y'] = df['vaccum']
    ax_vaccum.update_xaxes(range=trange)
    ax_flow.data[0]['x'] = df['datetime']
    ax_flow.data[0]['y'] = df['flow']
    ax_flow.update_xaxes(range=trange)
    
    return ax_temp_A, ax_temp_B, ax_strain_A, ax_strain_B, ax_pressure_high, ax_pressure_low, ax_vaccum, ax_flow, m

# set alert status
@callback(
    Output('alert-indicator', 'value', allow_duplicate=True),
    Input('alert', 'on'),
    prevent_initial_call=True
)
def alert(on):
    if on:
        with open('./alert/hold.txt',"w") as hold_file:
            hold_file.write(dumps(0))
        return False
    else:
        with open('./alert/hold.txt',"w") as hold_file:
            hold_file.write(dumps(1))
        return False

# update setting
@callback(
    Output('alert-indicator', 'value'),
    Input('set-update', 'n_intervals'),
    Input('alert', 'on')
)
def alert(n_intervals, on):
    with open('./alert/hold.txt',"r") as hold_file:
        hold = loads(hold_file.readline())
    if on:
        if hold:
            return True
        else:
            return False
    else:
        return False

@callback(
    Output('xe-mass', 'value', allow_duplicate=True),
    Input('reset-mass', 'n_clicks'),
    prevent_initial_call=True
)
def reset_mass(n_clicks):
    return 0


# Run the app

if __name__ == '__main__':
    app.run(debug=True)