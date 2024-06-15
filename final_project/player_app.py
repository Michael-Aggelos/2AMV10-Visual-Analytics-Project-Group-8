import dash
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load player data
player_df = pd.read_csv('player_season_stats.csv')

# Define the layout
layout = html.Div([
    dcc.Dropdown(
        id='player-dropdown',
        options=[{'label': player, 'value': player} for player in player_df['PLAYER_NAME'].unique()],
        value=player_df['PLAYER_NAME'].unique()[0]
    ),
    dcc.Dropdown(
        id='season-dropdown'
    ),
    dcc.Graph(id='player-graph-container')
])

# Define callbacks
@dash.callback(
    Output('season-dropdown', 'options'),
    Output('season-dropdown', 'value'),
    Input('player-dropdown', 'value')
)
def update_season_dropdown(selected_player_name):
    filtered_df = player_df[player_df['PLAYER_NAME'] == selected_player_name]
    season_options = [{'label': season, 'value': season} for season in filtered_df['SEASON'].unique()]
    return season_options, season_options[0]['value']

@dash.callback(
    Output('player-graph-container', 'figure'),
    Input('player-dropdown', 'value'),
    Input('season-dropdown', 'value')
)
def update_player_graph(selected_player_name, selected_season):
    filtered_df = player_df[(player_df['PLAYER_NAME'] == selected_player_name) & (player_df['SEASON'] == selected_season)]
    fig = px.bar(filtered_df, x='GAME_DATE', y='POINTS', title=f'{selected_player_name} - {selected_season}')
    return fig
