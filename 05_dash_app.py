"""
Capstone step 5 — Plotly Dash dashboard.
Run:  python 05_dash_app.py     then open http://127.0.0.1:8050

Screenshots needed:
  slide 39 — pie chart with "All Sites" selected
  slide 40 — pie chart with KSC LC-39A selected (highest success ratio)
  slide 41 — scatter plot at two or three different payload slider ranges
"""

import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output

URL = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
       "IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")

spacex_df = pd.read_csv(URL)
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
sites = spacex_df['Launch Site'].unique().tolist()

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                [{'label': s, 'value': s} for s in sites],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),

    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),

    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df[spacex_df['class'] == 1],
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        filtered = spacex_df[spacex_df['Launch Site'] == entered_site]
        counts = filtered['class'].value_counts().reset_index()
        counts.columns = ['class', 'count']
        counts['Outcome'] = counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            counts, values='count', names='Outcome',
            title=f'Success vs. Failure for {entered_site}'
        )
    return fig


@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = spacex_df['Payload Mass (kg)'].between(low, high)
    filtered = spacex_df[mask]

    if entered_site != 'ALL':
        filtered = filtered[filtered['Launch Site'] == entered_site]

    title = ('Payload vs. Launch Outcome — All Sites' if entered_site == 'ALL'
             else f'Payload vs. Launch Outcome — {entered_site}')

    return px.scatter(
        filtered, x='Payload Mass (kg)', y='class',
        color='Booster Version Category', title=title
    )


if __name__ == '__main__':
    app.run(debug=True, port=8050)
