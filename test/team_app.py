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
                dbc.Col(html.Label("Select Team:"), width=2),
                dbc.Col(dcc.Dropdown(
                    id='team-dropdown',
                    options=[{'label': name, 'value': name} for name in team_df[team_name_column].unique()],
                    value=team_df[team_name_column].iloc[0]
                ), width=10)
            ]),
            dbc.Row([
                dbc.Col(html.Label("Select Season:"), width=2),
                dbc.Col(dcc.Dropdown(
                    id='team-season-dropdown'
                ), width=10)
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

def update_team_graph(selected_team_name, selected_season):
    if not selected_team_name or not selected_season:
        return ""

    selected_team_id = team_id_map[selected_team_name]
    team_stats_row = team_df[(team_df[team_id_column] == selected_team_id) & (team_df[season_column] == selected_season)]
    
    if team_stats_row.empty:
        return ""
    
    team_stats = team_stats_row.iloc[0][team_categories].tolist()
    additional_stats = team_stats_row.iloc[0][team_additional_categories].to_dict()

    additional_stats['average_shot_distance'] = round(additional_stats['average_shot_distance'], 2)
    
    values = team_stats + team_stats[:1]
    categories_loop = team_categories + team_categories[:1]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories_loop,
        fill='toself',
        name=f"{selected_team_name} - {selected_season}"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values)]
            )
        ),
        showlegend=False,
        title=f"Stats for {selected_team_name} in {selected_season}",
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
    team_app.run_server(debug=True)
