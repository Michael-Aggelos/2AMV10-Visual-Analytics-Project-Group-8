import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc

# Load the player CSV file
player_file_path = 'player_season_stats.csv'
player_df = pd.read_csv(player_file_path)

# Define column names for players
player_id_column = 'PLAYER_ID'
player_name_column = 'PLAYER_NAME'
season_column = 'SEASON_2'
player_categories = ['total_shots_made', 'total_shots_attempted', 'total_2pt_made', 'total_2pt_attempted',
                     'total_3pt_made', 'total_3pt_attempted', 'clutch_shots_made']
player_additional_categories = ['preferred_shot_zone', 'preferred_action_type', 'average_shot_distance']

# Create a dictionary to map player names to IDs
player_id_map = player_df.set_index(player_name_column)[player_id_column].to_dict()

player_app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])

player_app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Player Stats Visualization", className="text-center my-4"), width=12)),
    
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col(html.Label("Select Player:"), width=2),
                dbc.Col(dcc.Dropdown(
                    id='player-dropdown',
                    options=[{'label': name, 'value': name} for name in player_df[player_name_column].unique()],
                    value=player_df[player_name_column].iloc[0]
                ), width=10)
            ]),
            dbc.Row([
                dbc.Col(html.Label("Select Season:"), width=2),
                dbc.Col(dcc.Dropdown(
                    id='season-dropdown'
                ), width=10)
            ])
        ], md=6)
    ]),
    
    dbc.Row(dbc.Col(html.Div(id='player-graph-container'), className="mt-4"))
], fluid=True)

def update_season_dropdown(selected_player_name):
    if selected_player_name:
        selected_player_id = player_id_map[selected_player_name]
        seasons = player_df[player_df[player_id_column] == selected_player_id][season_column].unique()
        options = [{'label': season, 'value': season} for season in seasons]
        value = seasons[0] if len(seasons) > 0 else None
        return options, value
    return [], None

def update_player_graph(selected_player_name, selected_season):
    if not selected_player_name or not selected_season:
        return ""

    selected_player_id = player_id_map[selected_player_name]
    player_stats_row = player_df[(player_df[player_id_column] == selected_player_id) & (player_df[season_column] == selected_season)]
    
    if player_stats_row.empty:
        return ""
    
    player_stats = player_stats_row.iloc[0][player_categories].tolist()
    additional_stats = player_stats_row.iloc[0][player_additional_categories].to_dict()

    additional_stats['average_shot_distance'] = round(additional_stats['average_shot_distance'], 2)
    
    values = player_stats + player_stats[:1]
    categories_loop = player_categories + player_categories[:1]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories_loop,
        fill='toself',
        name=f"{selected_player_name} - {selected_season}"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values)]
            )
        ),
        showlegend=False,
        title=f"Stats for {selected_player_name} in {selected_season}",
        paper_bgcolor='#2c3e50',  # Set the background color for the plot
        font_color='#ecf0f1'      # Set the font color for the plot
    )

    additional_stats_html = [
        html.H3("Additional Stats"),
        html.Ul([html.Li(f"{key}: {value}") for key, value in additional_stats.items()])
    ]

    return html.Div([
        html.Div(id='additional-stats', children=additional_stats_html, style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
        html.Div(dcc.Graph(figure=fig), style={'width': '68%', 'display': 'inline-block'})
    ])

if __name__ == '__main__':
    player_app.run_server(debug=True)
