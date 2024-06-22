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
                dbc.Col(html.Label("Select Player 1:"), width=3),
                dbc.Col(dcc.Dropdown(
                    id='player-dropdown-1',
                    options=[{'label': name, 'value': name} for name in player_df[player_name_column].unique()],
                    value=player_df[player_name_column].iloc[0]
                ), width=9)
            ]),
            dbc.Row([
                dbc.Col(html.Label("Select Season 1:"), width=3),
                dbc.Col(dcc.Dropdown(
                    id='season-dropdown-1'
                ), width=9)
            ])
        ], md=6),
        dbc.Col([
            dbc.Row([
                dbc.Col(html.Label("Select Player 2:"), width=3),
                dbc.Col(dcc.Dropdown(
                    id='player-dropdown-2',
                    options=[{'label': name, 'value': name} for name in player_df[player_name_column].unique()],
                    value=player_df[player_name_column].iloc[0]
                ), width=9)
            ]),
            dbc.Row([
                dbc.Col(html.Label("Select Season 2:"), width=3),
                dbc.Col(dcc.Dropdown(
                    id='season-dropdown-2'
                ), width=9)
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

def update_additional_stats_html(additional_stats, entity_name):
    stats_html = [
        html.H3(f"Additional Stats for {entity_name}"),
        html.Ul([html.Li(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}") for key, value in additional_stats.items()])
    ]
    return stats_html

def update_player_graph(selected_player_name_1, selected_season_1, selected_player_name_2, selected_season_2):
    if not selected_player_name_1 or not selected_season_1 or not selected_player_name_2 or not selected_season_2:
        return ""

    selected_player_id_1 = player_id_map[selected_player_name_1]
    player_stats_row_1 = player_df[(player_df[player_id_column] == selected_player_id_1) & (player_df[season_column] == selected_season_1)]
    
    selected_player_id_2 = player_id_map[selected_player_name_2]
    player_stats_row_2 = player_df[(player_df[player_id_column] == selected_player_id_2) & (player_df[season_column] == selected_season_2)]

    if player_stats_row_1.empty or player_stats_row_2.empty:
        return ""

    player_stats_1 = player_stats_row_1.iloc[0][player_categories].tolist()
    additional_stats_1 = player_stats_row_1.iloc[0][player_additional_categories].to_dict()

    player_stats_2 = player_stats_row_2.iloc[0][player_categories].tolist()
    additional_stats_2 = player_stats_row_2.iloc[0][player_additional_categories].to_dict()

    additional_stats_1['average_shot_distance'] = round(additional_stats_1['average_shot_distance'], 2)
    additional_stats_2['average_shot_distance'] = round(additional_stats_2['average_shot_distance'], 2)
    
    values_1 = player_stats_1 + player_stats_1[:1]
    values_2 = player_stats_2 + player_stats_2[:1]
    categories_loop = player_categories + player_categories[:1]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_1,
        theta=categories_loop,
        fill='toself',
        name=f"{selected_player_name_1} - {selected_season_1}"
    ))

    fig.add_trace(go.Scatterpolar(
        r=values_2,
        theta=categories_loop,
        fill='toself',
        name=f"{selected_player_name_2} - {selected_season_2}"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(max(values_1), max(values_2))]
            )
        ),
        showlegend=True,
        title=f"Comparison between {selected_player_name_1} and {selected_player_name_2} for {selected_season_1} and {selected_season_2}",
        paper_bgcolor='#2c3e50',  # Set the background color for the plot
        font_color='#ecf0f1'      # Set the font color for the plot
    )

    additional_stats_html_1 = update_additional_stats_html(additional_stats_1, selected_player_name_1)
    additional_stats_html_2 = update_additional_stats_html(additional_stats_2, selected_player_name_2)

    return html.Div([
        dbc.Row([
            dbc.Col(html.Div(id='additional-stats-1', children=additional_stats_html_1), width=6),
            dbc.Col(html.Div(id='additional-stats-2', children=additional_stats_html_2), width=6)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig), width=12)
        ])
    ])

# @player_app.callback(
#     Output('season-dropdown-1', 'options'),
#     Output('season-dropdown-1', 'value'),
#     Input('player-dropdown-1', 'value')
# )
def update_season_dropdown_1(selected_player_name_1):
    return update_season_dropdown(selected_player_name_1)

# @player_app.callback(
#     Output('season-dropdown-2', 'options'),
#     Output('season-dropdown-2', 'value'),
#     Input('player-dropdown-2', 'value')
# )
def update_season_dropdown_2(selected_player_name_2):
    return update_season_dropdown(selected_player_name_2)

# @player_app.callback(
#     Output('player-graph-container', 'children'),
#     Input('player-dropdown-1', 'value'),
#     Input('season-dropdown-1', 'value'),
#     Input('player-dropdown-2', 'value'),
#     Input('season-dropdown-2', 'value')
# )
def update_player_graph_callback(selected_player_name_1, selected_season_1, selected_player_name_2, selected_season_2):
    return update_player_graph(selected_player_name_1, selected_season_1, selected_player_name_2, selected_season_2)

if __name__ == '__main__':
    player_app.run_server(debug=True)
