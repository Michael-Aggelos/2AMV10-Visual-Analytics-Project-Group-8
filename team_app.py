import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load team data
team_df = pd.read_csv('team_season_stats.csv')

# Define the layout
layout = html.Div([
    dcc.Dropdown(
        id='team-dropdown',
        options=[{'label': team, 'value': team} for team in team_df['TEAM_NAME'].unique()],
        value=team_df['TEAM_NAME'].unique()[0]
    ),
    dcc.Dropdown(
        id='team-season-dropdown'
    ),
    dcc.Graph(id='team-graph-container')
])

# Define callbacks
@dash.callback(
    Output('team-season-dropdown', 'options'),
    Output('team-season-dropdown', 'value'),
    Input('team-dropdown', 'value')
)
def update_team_season_dropdown(selected_team_name):
    filtered_df = team_df[team_df['TEAM_NAME'] == selected_team_name]
    season_options = [{'label': season, 'value': season} for season in filtered_df['SEASON'].unique()]
    return season_options, season_options[0]['value']

@dash.callback(
    Output('team-graph-container', 'figure'),
    Input('team-dropdown', 'value'),
    Input('team-season-dropdown', 'value')
)
def update_team_graph(selected_team_name, selected_season):
    filtered_df = team_df[(team_df['TEAM_NAME'] == selected_team_name) & (team_df['SEASON'] == selected_season)]
    fig = px.line(filtered_df, x='GAME_DATE', y='WINS', title=f'{selected_team_name} - {selected_season}')
    return fig
