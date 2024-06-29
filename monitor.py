from dash import Dash, html, dcc, callback, Output, Input
# from dash.exceptions import PreventUpdate
import plotly.express as px

import pandas as pd

import datetime

import numpy as np
from json import loads

# Constants
R = 8.31  # Universal gas constant in J/(mol*K)
T = 298  # Room temperature in K
mu = 131.5  # Molar mass of air in g/mol (assuming air)

PATH = "./data/record.log"

SLEEP = 5000

# plot definition
df = pd.read_csv(PATH)
# df['flow'] -= 0.4962225274725274
# df['low_pressure'] += 1.0683760683760681

trange = [pd.to_datetime(df.iloc[-1]['datetime'])-pd.Timedelta('1 day'), pd.to_datetime(df.iloc[-1]['datetime'])]

# check the closest point to the left side of plot window as base line
ft = np.abs((pd.to_datetime(df['datetime']) - pd.to_datetime(df.iloc[-1]['datetime']) + pd.Timedelta('1 day')) / pd.Timedelta('1 day'))
m = np.argmin(ft)

# set integrated mass
f = df['flow'][:-1] * 1e-3
t = (pd.to_datetime(df['datetime'][1:]) - pd.to_datetime(df['datetime'][:-1])) / pd.Timedelta('1 min')
p = df['low_pressure'][:-1] * 1000
dm = (p * f * t * mu) / (R * T) / 1000
mass_integral = np.array(list(map(lambda x: dm.sum(), range(dm.size))))
mass_integral -= mass_integral[m]

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
ax_flow = px.line(x=df['datetime'], y=[df['flow'], mass_integral], labels={'x': '', 'y': 'flow'}, title="Flow")
ax_flow.update_xaxes(range=trange)
ax_flow.data[0].name = 'flow(L/min)'
ax_flow.data[1].name = 'mass(kg)'

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
    # dcc.RadioItems(options=['1 day', '1 hour', '5 minutes'], value='5 minutes', id='time-range'),
    html.Div([dcc.Graph(id='ax_temp_A', figure=ax_temp_A, style={'display': 'inline-block'}),
              dcc.Graph(id='ax_temp_B', figure=ax_temp_B, style={'display': 'inline-block'})]),
    html.Div([dcc.Graph(id='ax_strain_A', figure=ax_strain_A, style={'display': 'inline-block'}),
              dcc.Graph(id='ax_strain_B', figure=ax_strain_B, style={'display': 'inline-block'})]),
    html.Div([dcc.Graph(id='ax_pressure_high', figure=ax_pressure_high, style={'display': 'inline-block'}),
              dcc.Graph(id='ax_pressure_low', figure=ax_pressure_low, style={'display': 'inline-block'})]),
    html.Div([dcc.Graph(id='ax_vaccum', figure=ax_vaccum, style={'display': 'inline-block'}),
              dcc.Graph(id='ax_flow', figure=ax_flow, style={'display': 'inline-block'})]),
    dcc.Interval(id="graph-update", interval=SLEEP, n_intervals=0)
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
    Output('ax_flow', 'figure')],
    Input('graph-update', 'n_intervals'),
    Input('time-range', 'value')
)
def update_plot(n_intervals, t):

    # Constants
    R = 8.31  # Universal gas constant in J/(mol*K)
    T = 298  # Room temperature in K
    mu = 131.5  # Molar mass of air in g/mol (assuming air)
    
    df = pd.read_csv(PATH)
    # df['flow'] -= 0.4962225274725274
    # df['low_pressure'] += 1.0683760683760681
    dt = pd.Timedelta(f'{t} day')
    trange = [pd.to_datetime(df.iloc[-1]['datetime'])-dt, pd.to_datetime(df.iloc[-1]['datetime'])]
    
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
    # p = ax_pressure_low.data[0]['y'][-1] * 1000
    ax_pressure_low.data[0]['y'] = df['low_pressure'] * 1e-2
    ax_pressure_low.update_xaxes(range=trange)
    ax_vaccum.data[0]['x'] = df['datetime']
    ax_vaccum.data[0]['y'] = df['vaccum']
    ax_vaccum.update_xaxes(range=trange)
    ax_flow.data[0]['x'] = df['datetime']
    # f = ax_flow.data[0]['y'][-1] * 1e-3
    ax_flow.data[0]['y'] = df['flow']
    ax_flow.update_xaxes(range=trange)

    # check the closest point to the left side of plot window as base line
    ft = np.abs((pd.to_datetime(df['datetime']) - pd.to_datetime(df.iloc[-1]['datetime']) + dt) / dt)
    m = np.argmin(ft)
    
    # t = pd.to_datetime(ax_flow.data[1]['x'][-1])
    # ax_flow.data[1]['x'] = df['datetime']
    # deltat = (pd.to_datetime(ax_flow.data[1]['x'][-1]) - t) / pd.Timedelta('1 minute')
    # if ax_flow.data[1]['y'].size < ax_flow.data[1]['x'].size:
    #     y = np.append(ax_flow.data[1]['y'], f * deltat)
    # else:
    #     y = np.append(ax_flow.data[1]['y'], ax_flow.data[1]['y'][-1] + p * f * deltat / R / T * mu / 1000)[1:]
    # y -= y[m]
    # ax_flow.data[1]['y'] = y
    
    # y = np.append(ax_flow.data[1]['y'], df['flow'][:-1].sum() * config['sleep'] / 60)[1:]
    # y[:-1] -= ax_flow.data[1]['y'][0]
    # ax_flow.data[1]['y'] = list(map(lambda x: df['flow'][:x].sum() * config['sleep'] / 60, range(df['flow'].size)))

    # set integrated mass
    f = df['flow'][:-1] * 1e-3
    t = (pd.to_datetime(df['datetime'][1:]) - pd.to_datetime(df['datetime'][:-1])) / pd.Timedelta('1 min')
    p = df['low_pressure'][:-1] * 1000
    dm = (p * f * t * mu) / (R * T) / 1000
    mass_integral = np.array(list(map(lambda x: dm.sum(), range(dm.size))))
    mass_integral -= mass_integral[m]
    ax_flow.data[1]['y'] = mass_integral
    
    return ax_temp_A, ax_temp_B, ax_strain_A, ax_strain_B, ax_pressure_high, ax_pressure_low, ax_vaccum, ax_flow


# Run the app

if __name__ == '__main__':
    app.run(debug=True)