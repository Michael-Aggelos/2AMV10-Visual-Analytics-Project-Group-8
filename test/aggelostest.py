import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import player_app
import plotly.express as px
import team_app

# Load the team CSV file for scatter plot
scatter_df = pd.read_csv('team_season_stats.csv')

# Initialize the main Dash app with a dark theme
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dbc.Row(dbc.Col(html.H1("NBA Dashboard", className="text-center my-4"), width=12)),
    
    dbc.Row([
        dbc.Col(html.Label("Select Player or Team:"), width=2),
        dbc.Col(dcc.Dropdown(
            id='entity-dropdown',
            options=[
                {'label': 'Player', 'value': 'player'},
                {'label': 'Team', 'value': 'team'}
            ],
            value='player'
        ), width=10)
    ]),
    
    dbc.Row(dbc.Col(html.Div(id='conditional-content'))),
    
    dbc.Row(dbc.Col(html.H4('Animated 2-pts and 3-pts shots attempts by teams in the NBA (2004-2023)', className="text-center my-4"), width=12)),
    
    dbc.Row([
        dbc.Col(dcc.RadioItems(
            id='scatter-selection',
            options=[
                {'label': "2-pts", 'value': '2-pts'},
                {'label': "3-pts", 'value': '3-pts'}
            ],
            value='2-pts',
            inline=True
        ), width=12)
    ]),
    
    dbc.Row(dbc.Col(dcc.Loading(dcc.Graph(id="scatter-graph"), type="cube"), width=12))
], fluid=True)

# Callback to display conditional content based on selection
@app.callback(
    Output('conditional-content', 'children'),
    Input('entity-dropdown', 'value')
)
def render_content(selected_entity):
    if selected_entity == 'player':
        return player_app.player_app.layout
    elif selected_entity == 'team':
        return team_app.team_app.layout

# Include player app callbacks
@app.callback(
    Output('season-dropdown', 'options'),
    Output('season-dropdown', 'value'),
    Input('player-dropdown', 'value')
)
def update_season_dropdown(selected_player_name):
    return player_app.update_season_dropdown(selected_player_name)

@app.callback(
    Output('player-graph-container', 'children'),
    Input('player-dropdown', 'value'),
    Input('season-dropdown', 'value')
)
def update_player_graph(selected_player_name, selected_season):
    return player_app.update_player_graph(selected_player_name, selected_season)

# Include team app callbacks
@app.callback(
    Output('team-season-dropdown', 'options'),
    Output('team-season-dropdown', 'value'),
    Input('team-dropdown', 'value')
)
def update_team_season_dropdown(selected_team_name):
    return team_app.update_team_season_dropdown(selected_team_name)

@app.callback(
    Output('team-graph-container', 'children'),
    Input('team-dropdown', 'value'),
    Input('team-season-dropdown', 'value')
)
def update_team_graph(selected_team_name, selected_season):
    return team_app.update_team_graph(selected_team_name, selected_season)

# Callback for scatter plot
@app.callback(
    Output("scatter-graph", "figure"), 
    Input("scatter-selection", "value")
)
def display_animated_graph(selection):
    animations = {
        '2-pts': px.scatter(
           scatter_df, x="total_2pt_attempted", y="total_shots_attempted", animation_frame="SEASON_2", 
            animation_group="TEAM_NAME", size="total_2pt_made", color="TEAM_NAME", 
            hover_name="TEAM_NAME", range_x=[3000,7000], range_y=[5000,8000]),
        '3-pts': px.scatter(
            scatter_df, x="total_3pt_attempted", y="total_shots_attempted", color="TEAM_NAME", 
            animation_frame="SEASON_2", animation_group="TEAM_NAME", size="total_3pt_made",
            range_x=[0,4000], range_y=[5000,8000]),
    }
    for key in animations:
        animations[key].update_layout(
            paper_bgcolor='#2c3e50',
            plot_bgcolor='#2c3e50',
            font=dict(color='#ecf0f1')
        )
    return animations[selection]

if __name__ == '__main__':
    app.run_server(debug=True)
