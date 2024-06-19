import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc

# Load the team CSV file
team_file_path = 'team_season_stats.csv'
team_df = pd.read_csv(team_file_path)

# Define column names for teams
team_id_column = 'TEAM_ID'
team_name_column = 'TEAM_NAME'
season_column = 'SEASON_2'
team_categories = ['total_shots_made', 'total_shots_attempted', 'total_2pt_made', 'total_2pt_attempted',
                   'total_3pt_made', 'total_3pt_attempted', 'clutch_shots_made']
team_additional_categories = ['average_shot_distance', 'home_performance', 'away_performance']

# Create a dictionary to map team names to IDs
team_id_map = team_df.set_index(team_name_column)[team_id_column].to_dict()

team_app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])

team_app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Team Stats Visualization", className="text-center my-4"), width=12)),
    
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col(html.Label("Select Team 1:"), width=3),
                dbc.Col(dcc.Dropdown(
                    id='team-dropdown-1',
                    options=[{'label': name, 'value': name} for name in team_df[team_name_column].unique()],
                    value=team_df[team_name_column].iloc[0]
                ), width=9)
            ]),
            dbc.Row([
                dbc.Col(html.Label("Select Season 1:"), width=3),
                dbc.Col(dcc.Dropdown(
                    id='team-season-dropdown-1'
                ), width=9)
            ])
        ], md=6),
        dbc.Col([
            dbc.Row([
                dbc.Col(html.Label("Select Team 2:"), width=3),
                dbc.Col(dcc.Dropdown(
                    id='team-dropdown-2',
                    options=[{'label': name, 'value': name} for name in team_df[team_name_column].unique()],
                    value=team_df[team_name_column].iloc[0]
                ), width=9)
            ]),
            dbc.Row([
                dbc.Col(html.Label("Select Season 2:"), width=3),
                dbc.Col(dcc.Dropdown(
                    id='team-season-dropdown-2'
                ), width=9)
            ])
        ], md=6)
    ]),
    
    dbc.Row(dbc.Col(html.Div(id='team-graph-container'), className="mt-4"))
], fluid=True)

def update_team_season_dropdown(selected_team_name):
    if selected_team_name:
        selected_team_id = team_id_map[selected_team_name]
        seasons = team_df[team_df[team_id_column] == selected_team_id][season_column].unique()
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

def update_team_graph(selected_team_name_1, selected_season_1, selected_team_name_2, selected_season_2):
    if not selected_team_name_1 or not selected_season_1 or not selected_team_name_2 or not selected_season_2:
        return ""

    selected_team_id_1 = team_id_map[selected_team_name_1]
    team_stats_row_1 = team_df[(team_df[team_id_column] == selected_team_id_1) & (team_df[season_column] == selected_season_1)]
    
    selected_team_id_2 = team_id_map[selected_team_name_2]
    team_stats_row_2 = team_df[(team_df[team_id_column] == selected_team_id_2) & (team_df[season_column] == selected_season_2)]

    if team_stats_row_1.empty or team_stats_row_2.empty:
        return ""

    team_stats_1 = team_stats_row_1.iloc[0][team_categories].tolist()
    additional_stats_1 = team_stats_row_1.iloc[0][team_additional_categories].to_dict()

    team_stats_2 = team_stats_row_2.iloc[0][team_categories].tolist()
    additional_stats_2 = team_stats_row_2.iloc[0][team_additional_categories].to_dict()

    additional_stats_1['average_shot_distance'] = round(additional_stats_1['average_shot_distance'], 2)
    additional_stats_2['average_shot_distance'] = round(additional_stats_2['average_shot_distance'], 2)
    
    values_1 = team_stats_1 + team_stats_1[:1]
    values_2 = team_stats_2 + team_stats_2[:1]
    categories_loop = team_categories + team_categories[:1]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_1,
        theta=categories_loop,
        fill='toself',
        name=f"{selected_team_name_1} - {selected_season_1}"
    ))

    fig.add_trace(go.Scatterpolar(
        r=values_2,
        theta=categories_loop,
        fill='toself',
        name=f"{selected_team_name_2} - {selected_season_2}"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(max(values_1), max(values_2))]
            )
        ),
        showlegend=True,
        title=f"Comparison between {selected_team_name_1} and {selected_team_name_2} for {selected_season_1} and {selected_season_2}",
        paper_bgcolor='#2c3e50',  # Set the background color for the plot
        font_color='#ecf0f1'      # Set the font color for the plot
    )

    additional_stats_html_1 = update_additional_stats_html(additional_stats_1, selected_team_name_1)
    additional_stats_html_2 = update_additional_stats_html(additional_stats_2, selected_team_name_2)

    return html.Div([
        dbc.Row([
            dbc.Col(html.Div(id='additional-stats-1', children=additional_stats_html_1), width=6),
            dbc.Col(html.Div(id='additional-stats-2', children=additional_stats_html_2), width=6)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig), width=12)
        ])
    ])

# @team_app.callback(
#     Output('team-season-dropdown-1', 'options'),
#     Output('team-season-dropdown-1', 'value'),
#     Input('team-dropdown-1', 'value')
# )
def update_team_season_dropdown_1(selected_team_name_1):
    return update_team_season_dropdown(selected_team_name_1)

# @team_app.callback(
#     Output('team-season-dropdown-2', 'options'),
#     Output('team-season-dropdown-2', 'value'),
#     Input('team-dropdown-2', 'value')
# )
def update_team_season_dropdown_2(selected_team_name_2):
    return update_team_season_dropdown(selected_team_name_2)

# @team_app.callback(
#     Output('team-graph-container', 'children'),
#     Input('team-dropdown-1', 'value'),
#     Input('team-season-dropdown-1', 'value'),
#     Input('team-dropdown-2', 'value'),
#     Input('team-season-dropdown-2', 'value')
# )
def update_team_graph_callback(selected_team_name_1, selected_season_1, selected_team_name_2, selected_season_2):
    return update_team_graph(selected_team_name_1, selected_season_1, selected_team_name_2, selected_season_2)

if __name__ == '__main__':
    team_app.run_server(debug=True)
