import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import player_app
import team_app
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import seaborn as sns

# Load the team CSV file for scatter plot
scatter_df = pd.read_csv('NBA_Teams_with_Conference.csv')

grouped = pd.read_csv('NBA_Team_Zone_Aggregated_Shots_2.csv')
# Create the DataFrame for the bar plot
bar_df = pd.read_csv('barplot_df.csv')

################## FOR SHOTS ####################

shots_df = pd.read_csv("NBA_2004_2023_Shots_2.csv")

player_name_column = 'PLAYER_NAME'
team_name_column = 'TEAM_NAME'
team_id_column = 'TEAM_ID'
player_id_column = 'PLAYER_ID'
season_column = 'SEASON_2'

# Create a dictionary to map player names to IDs
player_id_map = shots_df.set_index(player_name_column)[player_id_column].to_dict()

#Create a dictionary to map team names to IDs
team_id_map = shots_df.set_index(team_name_column)[team_id_column].to_dict()


################## ^^^^^ ####################

################# FOR 2-3PT RATIO ################
# # Create the Ratio_df dataframe
# Ratio_df = scatter_df.groupby(['SEASON_2']).agg({'total_2pt_made':'sum','total_2pt_attempted':'sum','total_3pt_made':'sum','total_3pt_attempted':'sum'}).reset_index()
# Ratio_df['3pt2pt_attempts_ratio'] = Ratio_df['total_3pt_attempted']/Ratio_df['total_2pt_attempted']

# # # save the Ratio_df to a csv file
# # Ratio_df.to_csv('2-3pt_Ratio_df.csv', index=False)

Ratio_df = pd.read_csv('2-3pt_Ratio_df.csv')

################## ^^^^^ ####################

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
    
    dbc.Row(dbc.Col(html.H4('Animated 3-pts shots attempts, 3pt/2pt ratio, and bar plot  by teams in the NBA (2004-2023)', className="text-center my-4"), width=12)),
    
    dbc.Row([
        dbc.Col(dcc.RadioItems(
            id='scatter-selection',
            options=[
                {'label': "3-pts Attempts", 'value': '3-pts'},
                {'label': "3pt/2pt Ratio", 'value': 'ratio'},
                {'label': "Bar Plot", 'value': 'bar-plot'}
            ],
            value='3-pts',
            inline=True
        ), width=12)
    ]),
    
    dbc.Row(dbc.Col(dcc.Loading(dcc.Graph(id="scatter-graph"), type="cube"), width=12)),

    dcc.Tab(label='Shot Charts', children=[
                # Content from shots_app layout
                dbc.Container([
                    dbc.Row([
                        dbc.Col([
                            dbc.Row([
                                dbc.Col(html.Label("Select Team:"), width=3),
                                dbc.Col(dcc.Dropdown(
                                    id='team-dropdown',
                                    options=[{'label': name, 'value': name} for name in shots_df[team_name_column].unique()],
                                    value=shots_df[team_name_column].iloc[0]
                                ), width=9)
                            ]),
                            dbc.Row([
                                dbc.Col(html.Label("Select Season:"), width=3),
                                dbc.Col(dcc.Dropdown(
                                    id='team-season-dropdown'
                                ), width=9)
                            ])
                        ], md=6)   ]),

                    dbc.Row([
                        dcc.Graph(id='shot-chart-team', style={'height': '62vh', 'width' :'40%'}),
                        dcc.Graph(id='shot-chart-2-team', style={'height': '80vh','width' :'60%'})
                    ])
                ], fluid=True)
            ])
        
    # dbc.Row(basketball_plot.shots_app.layout),

    # dbc.Row(basketball_plot.shots_app_team.layout),
    # dbc.Row([
    #     dbc.Col(html.Label("Select Player or Team:"), width=2),
    #     dbc.Col(dcc.Dropdown(
    #         id='entity-dropdown-plot-shot',
    #         options=[
    #             {'label': 'Player', 'value': 'player'},
    #             {'label': 'Team', 'value': 'team'}
    #         ],
    #         value='player'
    #     ), width=10)
    # ])


], fluid=True)

# @app.callback(
#     Output('conditional-content-plot-shot', 'children'),
#     Input('entity-dropdown-plot-shot', 'value')
# )
# def render_shot_charts(selected_entity):
#     if selected_entity == 'player':
#         return shots_app_player_layout()  # Define this as a function returning the layout
#     elif selected_entity == 'team':
#         return shots_app_team_layout()  # Define this as a function returning the layout

@app.callback(
    Output('season-dropdown', 'options'),
    Output('season-dropdown', 'value'),
    Input('player-dropdown', 'value')
)
def update_season_dropdown(selected_player_name):
    if selected_player_name:
        selected_player_id = player_id_map[selected_player_name]
        seasons = shots_df[shots_df[player_id_column] == selected_player_id][season_column].unique()
        options = [{'label': season, 'value': season} for season in seasons]
        value = seasons[0] if len(seasons) > 0 else None
        return options, value
    return [], None

# Include team app callbacks
@app.callback(
    Output('team-season-dropdown', 'options'),
    Output('team-season-dropdown', 'value'),
    Input('team-dropdown', 'value')
)
def update_season_dropdown(selected_team_name):
        #debug print
    # print("selected_player_name")
    # print(selected_player_name)
    if selected_team_name:
        selected_team_id = team_id_map[selected_team_name]
        seasons = shots_df[shots_df[team_id_column] == selected_team_id][season_column].unique()
        options = [{'label': season, 'value': season} for season in seasons]
        value = seasons[0] if len(seasons) > 0 else None
        return options, value
    return [], None

# Callback to update the shot chart based on selected player and date
@app.callback(
    Output('shot-chart-2', 'figure'),
    Input('player-dropdown', 'value'),
    Input('season-dropdown', 'value')
)
def update_shot_chart(selected_player, selected_season):
    player_shots = shots_df[(shots_df['PLAYER_NAME'] == selected_player) & (shots_df['SEASON_2'] == selected_season)]
    
    fig, ax = plt.subplots(figsize=(5, 4.7))
    ax = draw_court(ax, outer_lines=True)

    # Plotting the scatter plot
    sns.scatterplot(x='LOC_X', y='LOC_Y', hue='EVENT_TYPE', data=player_shots, palette={'Missed Shot': 'red', 'Made Shot': 'green'}, s=30, ax=ax)


    # Hide axes
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    # Set the limits for the axes
    ax.set_xlim(250, -250)
    ax.set_ylim(-47.5, 422.5)

    # Invert the x-axis
    ax.invert_xaxis()

    # Convert plot to base64 string
    buffer = io.BytesIO()
    FigureCanvas(fig).print_png(buffer)
    plot_data = base64.b64encode(buffer.getvalue()).decode()

    return {
        'data': [],
        'layout': {
            'images': [{
                'source': 'data:image/png;base64,{}'.format(plot_data),
                'xref': 'paper',
                'yref': 'paper',
                'x': 0,
                'y': 1,
                'sizex': 1,
                'sizey': 1,
                'sizing': 'contain',
                'opacity': 1,
                'layer': 'below'
            }],
            'xaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
            'yaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
        }
    }

# Callback to update the shot chart based on selected player and date
@app.callback(
    Output('shot-chart', 'figure'),
    Input('player-dropdown', 'value'),
    Input('season-dropdown', 'value')
)
def update_shot_chart(selected_player, selected_season):
    player_shots = shots_df[(shots_df['PLAYER_NAME'] == selected_player) & (shots_df['SEASON_2'] == selected_season)]
        # Set facecolor to 'none' for transparency
    fig, ax = plt.subplots(figsize=(5, 4.7))
     
    # ax.set_facecolor('none')  # Set the axes background color to 'none' (transparent)

    # Set axis limits
    ax.set_xlim(250, -250)
    ax.set_ylim(-47.5, 422.5)

    # Create a hexbin plot
    hb = ax.hexbin(x=player_shots.LOC_X, y=player_shots.LOC_Y, C=player_shots.shot_made,
                    gridsize=40, edgecolors='orange', cmap='Blues')

    # Hide axes
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax = draw_court(ax, outer_lines=True)
    # ax.set_facecolor('none')  # Set the axes background color to 'none' (transparent)
    # Optionally add text to the plot
    # ax.text(240, 400, 'Blue indicates shot accuracy', horizontalalignment='right',
    #         fontsize=12, color='black')

    # Show colorbar
    cb = fig.colorbar(hb, ax=ax, orientation='vertical')
    cb.set_label('Accuracy')

    # Invert the x-axis
    ax.invert_xaxis()

    # Convert plot to base64 string
    buffer = io.BytesIO()
    FigureCanvas(fig).print_png(buffer)
    plot_data = base64.b64encode(buffer.getvalue()).decode()

    return {
        'data': [],
        'layout': {
            'images': [{
                'source': 'data:image/png;base64,{}'.format(plot_data),
                'xref': 'paper',
                'yref': 'paper',
                'x': 0,
                'y': 1,
                'sizex': 1,
                'sizey': 1,
                'sizing': 'contain',
                'opacity': 1,
                'layer': 'below'
            }],
            'xaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
            'yaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
        }
    }

# Callback to update the shot chart based on selected player and date
@app.callback(
    Output('shot-chart-2-team', 'figure'),
    Input('team-dropdown', 'value'),
    Input('team-season-dropdown', 'value')
)
def update_plot_shot(selected_team, selected_season):
    fig = go.Figure()
    draw_plotly_court(fig)
    # Filter the data based on the selected team and season
    filtered_df = grouped[(grouped['team_name'] == selected_team) & (grouped['season'] == selected_season)]
    filtered_df = filtered_df.reset_index(drop=True)
    
    max_freq = filtered_df['frequency'].max()  # Determine the max frequency for scaling
    min_freq = filtered_df['frequency'].min()  # Determine the min frequency for scaling
    colorscale = 'YlOrRd'
    
    # Dynamically set cmin and cmax based on the actual data
    marker_cmin = filtered_df['accuracy_percentage'].min()
    marker_cmax = filtered_df['accuracy_percentage'].max()
    
    ticktexts = [str(marker_cmin)+'%', "", str(marker_cmax)+'%']

    xlocs = filtered_df['average_x']
    ylocs = filtered_df['average_y']
    accs_by_hex = filtered_df['accuracy_percentage']
    freq_by_hex = filtered_df['frequency']

    hexbin_text = [
        '<i>Accuracy: </i>' + str(round(accs_by_hex[i], 1)) + '%<BR>'
        '<i>Frequency: </i>' + str(round(freq_by_hex[i], 2))
        for i in range(len(freq_by_hex))
    ]

    # Clear existing traces
    fig.data = []

    # Calculate sizes
    sizes = 10 + (freq_by_hex - min_freq) / (max_freq - min_freq) * 50  # Scale sizes between 10 and 60

    # Add new trace
    fig.add_trace(go.Scatter(
        x=xlocs, y=ylocs, mode='markers', name='markers',
        marker=dict(
            size=sizes,  # Use the calculated sizes
            sizemode='diameter',
            color=accs_by_hex, colorscale=colorscale,
            colorbar=dict(
                thickness=15,
                x=0.84,
                y=0.87,
                yanchor='middle',
                len=0.2,
                title=dict(
                    text="<B>Accuracy</B>",
                    font=dict(
                        size=11,
                        color='#4d4d4d'
                    ),
                ),
                tickvals=[marker_cmin, (marker_cmin + marker_cmax) / 2, marker_cmax],
                ticktext=ticktexts,
                tickfont=dict(
                    size=11,
                    color='#4d4d4d'
                )
            ),
            cmin=marker_cmin, cmax=marker_cmax,
            line=dict(width=1, color='#333333'), symbol='hexagon',
        ),
        text=hexbin_text,
        hoverinfo='text'
    ))

    return fig

def draw_plotly_court(fig, fig_width=600, margins=10):

    import numpy as np
        
    def ellipse_arc(x_center=0.0, y_center=0.0, a=10.5, b=10.5, start_angle=0.0, end_angle=2 * np.pi, N=200, closed=False):
        t = np.linspace(start_angle, end_angle, N)
        x = x_center + a * np.cos(t)
        y = y_center + b * np.sin(t)
        path = f'M {x[0]}, {y[0]}'
        for k in range(1, len(t)):
            path += f'L{x[k]}, {y[k]}'
        if closed:
            path += ' Z'
        return path

    fig_height = fig_width * (470 + 2 * margins) / (500 + 2 * margins)
    fig.update_layout(width=fig_width, height=fig_height)

    # Set axes ranges
    fig.update_xaxes(range=[-250 - margins, 250 + margins], fixedrange=False)
    fig.update_yaxes(range=[-52.5 - margins, 417.5 + margins], fixedrange=False)

    threept_break_y = 89.47765084
    three_line_col = "#777777"
    main_line_col = "#777777"

    fig.update_layout(
        # Line Horizontal
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        yaxis=dict(
            scaleanchor="x",
            scaleratio=1,
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False,
            fixedrange=False,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False,
            fixedrange=False,
        ),
        shapes=[
            dict(
                type="rect", x0=-250, y0=-52.5, x1=250, y1=417.5,
                line=dict(color=main_line_col, width=1),
                # fillcolor='#333333',
                layer='below'
            ),
            dict(
                type="rect", x0=-80, y0=-52.5, x1=80, y1=137.5,
                line=dict(color=main_line_col, width=1),
                # fillcolor='#333333',
                layer='below'
            ),
            dict(
                type="rect", x0=-60, y0=-52.5, x1=60, y1=137.5,
                line=dict(color=main_line_col, width=1),
                # fillcolor='#333333',
                layer='below'
            ),
            dict(
                type="circle", x0=-60, y0=77.5, x1=60, y1=197.5, xref="x", yref="y",
                line=dict(color=main_line_col, width=1),
                # fillcolor='#dddddd',
                layer='below'
            ),
            dict(
                type="line", x0=-60, y0=137.5, x1=60, y1=137.5,
                line=dict(color=main_line_col, width=1),
                layer='below'
            ),

            dict(
                type="rect", x0=-2, y0=-7.25, x1=2, y1=-12.5,
                line=dict(color="#ec7607", width=1),
                fillcolor='#ec7607',
            ),
            dict(
                type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5, xref="x", yref="y",
                line=dict(color="#ec7607", width=1),
            ),
            dict(
                type="line", x0=-30, y0=-12.5, x1=30, y1=-12.5,
                line=dict(color="#ec7607", width=1),
            ),

            dict(type="path",
                 path=ellipse_arc(a=40, b=40, start_angle=0, end_angle=np.pi),
                 line=dict(color=main_line_col, width=1), layer='below'),
            dict(type="path",
                 path=ellipse_arc(a=237.5, b=237.5, start_angle=0.386283101, end_angle=np.pi - 0.386283101),
                 line=dict(color=main_line_col, width=1), layer='below'),
            dict(
                type="line", x0=-220, y0=-52.5, x1=-220, y1=threept_break_y,
                line=dict(color=three_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-220, y0=-52.5, x1=-220, y1=threept_break_y,
                line=dict(color=three_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=220, y0=-52.5, x1=220, y1=threept_break_y,
                line=dict(color=three_line_col, width=1), layer='below'
            ),

            dict(
                type="line", x0=-250, y0=227.5, x1=-220, y1=227.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=250, y0=227.5, x1=220, y1=227.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-90, y0=17.5, x1=-80, y1=17.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-90, y0=27.5, x1=-80, y1=27.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-90, y0=57.5, x1=-80, y1=57.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-90, y0=87.5, x1=-80, y1=87.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=90, y0=17.5, x1=80, y1=17.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=90, y0=27.5, x1=80, y1=27.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=90, y0=57.5, x1=80, y1=57.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=90, y0=87.5, x1=80, y1=87.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),

            dict(type="path",
                 path=ellipse_arc(y_center=417.5, a=60, b=60, start_angle=-0, end_angle=-np.pi),
                 line=dict(color=main_line_col, width=1), layer='below'),

        ]
    )
    return True

# def update_shot_chart(selected_team, selected_season):
#     player_shots = shots_df[(shots_df['TEAM_NAME'] == selected_team) & (shots_df['SEASON_2'] == selected_season)]
    
#     fig, ax = plt.subplots(figsize=(5, 4.7))
#     ax = draw_court(ax, outer_lines=True)

#     # Plotting the scatter plot
#     sns.scatterplot(x='LOC_X', y='LOC_Y', hue='EVENT_TYPE', data=player_shots, palette={'Missed Shot': 'red', 'Made Shot': 'green'}, s=30, ax=ax)


#     # Hide axes
#     ax.xaxis.set_visible(False)
#     ax.yaxis.set_visible(False)

#     # Set the limits for the axes
#     ax.set_xlim(250, -250)
#     ax.set_ylim(-47.5, 422.5)

#     # Invert the x-axis
#     ax.invert_xaxis()

#     # Convert plot to base64 string
#     buffer = io.BytesIO()
#     FigureCanvas(fig).print_png(buffer)
#     plot_data = base64.b64encode(buffer.getvalue()).decode()

#     return {
#         'data': [],
#         'layout': {
#             'images': [{
#                 'source': 'data:image/png;base64,{}'.format(plot_data),
#                 'xref': 'paper',
#                 'yref': 'paper',
#                 'x': 0,
#                 'y': 1,
#                 'sizex': 1,
#                 'sizey': 1,
#                 'sizing': 'contain',
#                 'opacity': 1,
#                 'layer': 'below'
#             }],
#             'xaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
#             'yaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
#         }
#     }



# Callback to update the shot chart based on selected player and date
@app.callback(
    Output('shot-chart-team', 'figure'),
    Input('team-dropdown', 'value'),
    Input('team-season-dropdown', 'value')
)
def update_shot_chart(selected_team, selected_season):
    player_shots = shots_df[(shots_df['TEAM_NAME'] == selected_team) & (shots_df['SEASON_2'] == selected_season)]
    
    
    fig, ax = plt.subplots(figsize=(5, 4.7))
    # Set axis limits
    ax.set_xlim(250, -250)
    ax.set_ylim(-47.5, 422.5)

    # Create a hexbin plot
    hb = ax.hexbin(x=player_shots.LOC_X, y=player_shots.LOC_Y, C=player_shots.shot_made,
                    gridsize=40, edgecolors='orange', cmap='Blues')

    # Hide axes
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax = draw_court(ax, outer_lines=True)

    # Optionally add text to the plot
    # ax.text(240, 400, 'Blue indicates shot accuracy', horizontalalignment='right',
    #         fontsize=12, color='black')

    # Show colorbar
    cb = fig.colorbar(hb, ax=ax, orientation='vertical')
    cb.set_label('Accuracy')

    # Invert the x-axis
    ax.invert_xaxis()

    # Convert plot to base64 string
    buffer = io.BytesIO()
    FigureCanvas(fig).print_png(buffer)
    plot_data = base64.b64encode(buffer.getvalue()).decode()

    return {
        'data': [],
        'layout': {
            'images': [{
                'source': 'data:image/png;base64,{}'.format(plot_data),
                'xref': 'paper',
                'yref': 'paper',
                'x': 0,
                'y': 1,
                'sizex': 1,
                'sizey': 1,
                'sizing': 'stretch',
                'opacity': 1,
                'layer': 'below'
            }],
            'xaxis': {
                'showgrid': False, 
                'zeroline': False, 
                'visible': False
            },
            'yaxis': {
                'showgrid': False, 
                'zeroline': False, 
                'visible': False
            },
            'margin': {
                'l': 0,
                'r': 0,
                't': 0,
                'b': 0
            },
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'autosize': True
        }
    }


def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    from matplotlib.patches import Circle, Rectangle, Arc

    if ax is None:
        ax = plt.gca()

    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False)
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False)
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180, linewidth=lw, color=color, fill=False)
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color, linestyle='dashed')
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color)
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw, color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color)
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0, linewidth=lw, color=color)

    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw, bottom_free_throw,
                      restricted, corner_three_a, corner_three_b, three_arc, center_outer_arc, center_inner_arc]

    if outer_lines:
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw, color=color, fill=False)
        court_elements.append(outer_lines)

    for element in court_elements:
        ax.add_patch(element)

    return ax


# def shots_app_player_layout():
#     return dbc.Container([
#         dbc.Row([
#                 dbc.Col([
#                     dbc.Row([
#                         dbc.Col(html.Label("Select Player:"), width=2),
#                         dbc.Col(dcc.Dropdown(
#                             id='player-dropdown',
#                             options=[{'label': name, 'value': name} for name in shots_df[player_name_column].unique()],
#                             value=shots_df[player_name_column].iloc[0]
#                         ), width=10)
#                     ]),
#                     dbc.Row([
#                         dbc.Col(html.Label("Select Season:"), width=2),
#                         dbc.Col(dcc.Dropdown(
#                             id='season-dropdown'
#                         ), width=10)
#                     ])
#                 ], md=6)
#             ]),
#             dbc.Row([
#                 dcc.Graph(id='shot-chart', style={'height': '80vh', 'width' :'50%'}),
#                 dcc.Graph(id='shot-chart-2', style={'height': '80vh','width' :'50%'})
#             ])
#     ], fluid=True)

def shots_app_team_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col(html.Label("Select Team:"), width=3),
                    dbc.Col(dcc.Dropdown(
                        id='team-dropdown',
                        options=[{'label': name, 'value': name} for name in shots_df[team_name_column].unique()],
                        value=shots_df[team_name_column].iloc[0]
                    ), width=9)
                ]),
                dbc.Row([
                    dbc.Col(html.Label("Select Season:"), width=3),
                    dbc.Col(dcc.Dropdown(
                        id='team-season-dropdown'
                    ), width=9)
                ])
            ], md=6)   ]),

        dbc.Row([
            dcc.Graph(id='shot-chart-team', style={'height': '80vh', 'width' :'50%'}),
            dcc.Graph(id='shot-chart-2-team', style={'height': '80vh','width' :'50%'})
        ])
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
    Output('season-dropdown-1', 'options'),
    Output('season-dropdown-1', 'value'),
    Input('player-dropdown-1', 'value')
)
def update_season_dropdown_1(selected_player_name):
    return player_app.update_season_dropdown(selected_player_name)

@app.callback(
    Output('season-dropdown-2', 'options'),
    Output('season-dropdown-2', 'value'),
    Input('player-dropdown-2', 'value')
)
def update_season_dropdown_2(selected_player_name):
    return player_app.update_season_dropdown(selected_player_name)

@app.callback(
    Output('player-graph-container', 'children'),
    Input('player-dropdown-1', 'value'),
    Input('season-dropdown-1', 'value'),
    Input('player-dropdown-2', 'value'),
    Input('season-dropdown-2', 'value')
)
def update_player_graph(selected_player_name_1, selected_season_1, selected_player_name_2, selected_season_2):
    return player_app.update_player_graph(selected_player_name_1, selected_season_1, selected_player_name_2, selected_season_2)

# Include team app callbacks
@app.callback(
    Output('team-season-dropdown-1', 'options'),
    Output('team-season-dropdown-1', 'value'),
    Input('team-dropdown-1', 'value')
)
def update_team_season_dropdown_1(selected_team_name):
    return team_app.update_team_season_dropdown(selected_team_name)

@app.callback(
    Output('team-season-dropdown-2', 'options'),
    Output('team-season-dropdown-2', 'value'),
    Input('team-dropdown-2', 'value')
)
def update_team_season_dropdown_2(selected_team_name):
    return team_app.update_team_season_dropdown(selected_team_name)

@app.callback(
    Output('team-graph-container', 'children'),
    Input('team-dropdown-1', 'value'),
    Input('team-season-dropdown-1', 'value'),
    Input('team-dropdown-2', 'value'),
    Input('team-season-dropdown-2', 'value')
)
def update_team_graph(selected_team_name_1, selected_season_1, selected_team_name_2, selected_season_2):
    return team_app.update_team_graph(selected_team_name_1, selected_season_1, selected_team_name_2, selected_season_2)

# Callback for scatter plot and line plot
@app.callback(
    Output("scatter-graph", "figure"), 
    Input("scatter-selection", "value")
)
def display_graph(selection):
    if selection == '3-pts':
        fig = px.scatter(
            scatter_df, x="total_3pt_attempted", y="total_shots_attempted", color="conference", 
            animation_frame="SEASON_2", animation_group="TEAM_NAME", size="total_3pt_made", hover_data=["TEAM_NAME"],
            range_x=[0,4000], range_y=[4000,8200])
    elif selection == 'ratio':
        fig = px.line(
            Ratio_df, x="SEASON_2", y="3pt2pt_attempts_ratio", markers=True,
            labels={'3pt2pt_attempts_ratio': '3pt/2pt Attempts Ratio', 'SEASON_2': 'Season'},
            title=f'3pt/2pt Attempts Ratio Over Seasons (2004-2023)')
        fig.update_xaxes(type='category')
        fig.update_traces(mode='lines+markers', hovertemplate='Season: %{x}<br>Ratio: %{y:.2f}')
    elif selection == 'bar-plot':
        fig = px.bar(bar_df, x="TEAM_NAME", y="Total Shots", color="Shot Type",
                     barmode='group', animation_frame="SEASON_2",
                     title="Bar Plot of Total Shots (2pts, 3pts, Total) by Teams Over Seasons")
        fig.update_xaxes(tickangle=45, tickmode='linear', dtick=1)
        fig.update_yaxes(range=[0, 8500])

    fig.update_layout(
        paper_bgcolor='#2c3e50',
        plot_bgcolor='#2c3e50',
        font=dict(color='#ecf0f1'),
        xaxis_tickfont_size=10,
        xaxis_categoryorder='category ascending'
    )
    
    return fig



if __name__ == '__main__':
    app.run_server(debug=True)