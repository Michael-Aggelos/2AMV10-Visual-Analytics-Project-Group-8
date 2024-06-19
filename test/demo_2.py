import dash
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State, ALL, MATCH
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
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV
from PyALE import ale
from sklearn.inspection import permutation_importance
from sklearn.ensemble import RandomForestRegressor

# Load the team CSV file for scatter plot
scatter_df = pd.read_csv('NBA_Teams_with_Conference.csv')

grouped = pd.read_csv('NBA_Team_Zone_Aggregated_Shots_2023.csv')

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

df_task1_final = pd.read_csv('FGA_Percentage_2023.csv')

nba_task4_final = pd.read_csv('3PT_Jumps_2023.csv')

df_ml = pd.read_csv('Team stats complete incl offrts.csv')
# drop rows with null values
# df_og = df_og.dropna().reset_index().drop(['index', 'Unnamed: 0'], axis=1)
# #save the adjusted data to an updated csv file
# df_og.to_csv('Team stats complete incl offrts.csv', index=False)


# Initialize the main Dash app with a dark theme
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])

options = [
    {'label': 'Total 2pt Made', 'value': 'total_2pt_made'},
    {'label': 'Total 2pt Attempted', 'value': 'total_2pt_attempted'},
    {'label': 'Total 3pt Made', 'value': 'total_3pt_made'},
    {'label': 'Total 3pt Attempted', 'value': 'total_3pt_attempted'},
    {'label': 'Clutch Shots Made', 'value': 'clutch_shots_made'},
    {'label': 'Average Shot distance', 'value': 'average_shot_distance'},
    {'label': 'Home Performance', 'value': 'home_performance'},
    {'label': 'Away Performance', 'value': 'away_performance'}
]


app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("NBA DASHBOARD", className="text-center my-4"),width=12)),
    
    dbc.Row([
        dbc.Col(html.Label("Select Analysis Dashboard"),style={'fontSize': 25,'justifyContent': 'center', 'color': '#FFFFFF', 'marginBottom': '20px', 'marginTop':'50px'} ),
        # create 2 buttons for the user to select the entity to analyze
        dbc.Row([
            dbc.Col(dbc.Button('3PT Revolution', id='btn-3ptrevolution', n_clicks=0, color='primary', className='mr-2'), width='auto'),
            dbc.Col(dbc.Button('Extra Player/Team Comparison', id='btn-extracomparison', n_clicks=0, color='primary', className='mr-2'), style={'marginLeft': '30px'}, width='auto')
        ],style={'justifyContent': 'center', 'marginBottom': '20px'}),

    ],style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    dbc.Row(dbc.Col(html.Div(id='conditional-content-main'))),
 ], fluid=True)   

#if entinty-dropdown-main is 3ptrevolution then add the following layout
@app.callback(
    Output('conditional-content-main', 'children'),
    [Input('btn-3ptrevolution', 'n_clicks'),
     Input('btn-extracomparison', 'n_clicks')]
)
def render_content(n_clicks_3ptrevolution, n_clicks_extracomparison):
    ctx = callback_context

    if not ctx.triggered:
        button_id = 'btn-3ptrevolution'  # default button
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        
    if button_id == 'btn-3ptrevolution':
        return dbc.Container([
            #Select range make it always have a range of 1 year
            dbc.Row([
                dbc.Col(html.Label("Select Season Range to Analyse:"),style={'fontSize': 25, 'color': '#FFFFFF', 'marginBottom': '10px'}),
                dbc.Col(dcc.RangeSlider(
                    id='season-slider',
                    min=2003,
                    max=2023,
                    step=1,
                    marks={i: str(i) for i in range(2003, 2024)},
                    value=[2003, 2023],
                    allowCross=False,
                    pushable=1,
                    tooltip={"placement": "bottom", "always_visible": True}
                ), width=9)
            ],style={'margin': '40px 20px', 'padding': '20px', 'backgroundColor': '#2c3e50', 'borderRadius': '10px'}),
            
            dbc.Row(dbc.Col(html.H2('NBA Teams --- 3-pt shots --- 3pt/2pt ratio --- Shots Bar plot --- FGA Percentage', className="text-center my-4"), width=12)),

            dbc.Row([
                dbc.Col(dcc.RadioItems(
                    id='scatter-selection',
                    options=[
                        {'label': "3-pts Attempts", 'value': '3-pts'},
                        {'label': "3pt/2pt Ratio", 'value': 'ratio'},
                        {'label': "Bar Plot", 'value': 'bar-plot'},
                        {'label': "FGA by Shot Type", 'value': 'fga-shot-type'}
                    ],
                    value='3-pts',
                    labelStyle={'display': 'inline-block', 'margin-right': '30px'},
                    inline=True,
                ), width=12)
            ]),
    
            dbc.Row(dbc.Col(dcc.Loading(dcc.Graph(id="scatter-graph"), type="cube"), width=12)),
    
            dbc.Row(dbc.Col(html.H2('Top Players with Highest One-Season Jumps in 3PA/FGA', className="text-center my-4"),style={'marginTop':"30px"}, width=12)),
            
            dbc.Row([
                dbc.Col(html.Label("Select Number of Players:"), width=3),
                dbc.Col(dcc.Dropdown(
                    id='num-players-dropdown',
                    options=[{'label': i, 'value': i} for i in range(1, 21)],
                    value=15
                ), width=9)
            ]),
            
            dbc.Row(dbc.Col(dcc.Loading(dcc.Graph(id="3pa-jumps-bar-graph"), type="cube"), width=12)),

            dbc.Row(dbc.Col(html.H2('Teams Seasonal Court Shots Plot', className="text-center my-4"), width=12)),

            dcc.Tab(label='Shot Charts', children=[shots_app_team_layout()]),

            dbc.Row(dbc.Col(html.H2('Feature Importance Plot - Offensive Rating Prediction', className="text-center my-4"),style={'marginTop':"30px"}, width=12)),
            
            dbc.Row([
                dbc.Col(
                    dcc.Input(id="input-3ptmade_value", type="text", placeholder="Enter text", style={'width': '100%'}), width=12)
            ]),
            
            dbc.Row(dbc.Col(dcc.Loading(dcc.Graph(id="feature_importance"), type="cube"), width=12)),

            dbc.Row(dbc.Col(dcc.Loading(dcc.Graph(id="predicted_offRating"), type="cube"), width=12)),

            ################################################################
            dbc.Row([
                dbc.Col(
                    dbc.Checklist(
                        options=options,
                        value=[],
                        id='options-checklist',
                        inline=True
                    ),
                    width=12
                )
            ]),
            html.Div(id='dynamic-inputs'),
            dbc.Row([
                dbc.Col(
                    dbc.Button('Submit', id='submit-button', n_clicks=0),
                    width=12
                )
            ]),
            dbc.Row([
                dbc.Col(
                    html.Div(id='output-div'),
                    width=12
                )
            ])
            ################################################################

        ], fluid=True)
    

    elif button_id == 'btn-extracomparison':
        return dbc.Container([
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
            ])


    


#create a helper function to change the selected range into the correct format for the data
def change_range(selected_range):
    #if is for example [2004, 2023] then it will change it to 2004-05 & 2022-23
    return f"{str(selected_range[0])}-{str(selected_range[0]+1)[2:]}", f"{str(selected_range[1]-1)}-{str(selected_range[1])[2:]}"

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

def draw_plotly_court(fig, fig_width=800, margins=0):

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
    Input("scatter-selection", "value"),
    Input('season-slider', 'value')
)
def display_graph(selection, selected_range):
    selected_range = change_range(selected_range)
    
    if selection == '3-pts':
        filtered_scatter_df = scatter_df[(scatter_df['SEASON_2'] >= selected_range[0]) & (scatter_df['SEASON_2'] <= selected_range[1])]
        fig = px.scatter(
            filtered_scatter_df, x="total_3pt_attempted", y="total_shots_attempted", color="conference", 
            animation_frame="SEASON_2", animation_group="TEAM_NAME", size="total_3pt_made", hover_data=["TEAM_NAME"],
            range_x=[0,4000], range_y=[4000,8200])
    elif selection == 'ratio':
        filtered_ratio_df = Ratio_df[(Ratio_df['SEASON_2'] >= selected_range[0]) & (Ratio_df['SEASON_2'] <= selected_range[1])]
        fig = px.line(
            filtered_ratio_df, x="SEASON_2", y="3pt2pt_attempts_ratio", markers=True,
            labels={'3pt2pt_attempts_ratio': '3pt/2pt Attempts Ratio', 'SEASON_2': 'Season'},
            title=f'3pt/2pt Attempts Ratio Over Seasons (2004-2023)')
        fig.update_xaxes(type='category')
        fig.update_traces(mode='lines+markers', hovertemplate='Season: %{x}<br>Ratio: %{y:.2f}')
    elif selection == 'bar-plot':
        filtered_bar_df = bar_df[(bar_df['SEASON_2'] >= selected_range[0]) & (bar_df['SEASON_2'] <= selected_range[1])]
        fig = px.bar(filtered_bar_df, x="TEAM_NAME", y="Total Shots", color="Shot Type",
                     barmode='group', animation_frame="SEASON_2",
                     title="Bar Plot of Total Shots (2pts, 3pts, Total) by Teams Over Seasons")
        fig.update_xaxes(tickangle=45, tickmode='linear', dtick=1)
        fig.update_yaxes(range=[0, 8500])
    elif selection == 'fga-shot-type':
        filtered_task1_final_df = df_task1_final[(df_task1_final['SEASON_2'] >= selected_range[0]) & (df_task1_final['SEASON_2'] <= selected_range[1])]
        fig = px.line(filtered_task1_final_df, x='SEASON_2', y='FGA_percentage', color='BASIC_ZONE',
            labels={'SEASON_2': 'Season', 'FGA_percentage': 'Percentage of FGA', 'BASIC_ZONE': 'Zone'},
            title='League-wide Percentage of FGA by Shot Type')
        fig.update_xaxes(type='category')
        fig.update_traces(mode='lines+markers', hovertemplate='Season: %{x}<br>FGA: %{y}')

    fig.update_layout(
        paper_bgcolor='#2c3e50',
        plot_bgcolor='#2c3e50',
        font=dict(color='#ecf0f1'),
        xaxis_tickfont_size=10,
        xaxis_categoryorder='category ascending'
    )
    
    return fig


# Include the callback for the new visualization
@app.callback(
    Output('3pa-jumps-bar-graph', 'figure'),
    Input('num-players-dropdown', 'value'),
    Input('season-slider', 'value')
)
def update_3pa_jumps_bar_graph(num_players, selected_range):
    selected_range = change_range(selected_range)
    # Sort the dataframe by the 3PA_jump column in descending order and select the top 'num_players'
    # sorted_df = nba_task4_final.sort_values(by='3PA_jump', ascending=False).head(num_players)
    filtered_sorted_df = nba_task4_final[(nba_task4_final['SEASON_2'] >= selected_range[0]) & (nba_task4_final['SEASON_2'] <= selected_range[1])]
    filtered_sorted_df = filtered_sorted_df.sort_values(by='3PA_jump', ascending=False).head(num_players)
    
    
    fig = px.bar(
        filtered_sorted_df,
        x='3PA_jump',
        y='PLAYER_NAME',
        orientation='h',
        text='3PA_jump',
        labels={
            '3PA_jump': 'Percentage Jump in 3PA/FGA',
            'PLAYER_NAME': 'Player Name',
            'SEASON_2': 'Season',
            'prev_SEASON_2': 'Previous Season',
            'prev_3PA_percentage': 'Previous Season 3PA%',
            '3PA_percentage': 'Current Season 3PA%'
        },
        hover_data={
            'SEASON_2': True,  # Show season in hover data
            '3PA_jump': ':.2f'
        }
    )
    
    # Annotate the bars with the percentage jump values
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    
    fig.update_layout(
        paper_bgcolor='#2c3e50',
        plot_bgcolor='#2c3e50',
        font=dict(color='#ecf0f1'),
        xaxis_tickfont_size=10,
        xaxis_categoryorder='category ascending'
    )
    
    return fig


@app.callback(
    Output('feature_importance', 'figure'),
    Input('season-slider', 'value')
)
def update_feature_importance(selected_range):
    selected_range = change_range(selected_range)
    rf_df = df_ml[(df_ml['SEASON_2'] >= selected_range[0]) & (df_ml['SEASON_2'] <= selected_range[1])].dropna()

    X = rf_df.drop(['SEASON_2', 'TEAM_NAME', 'Offensive rating','total_shots_made', 'total_shots_attempted'], axis=1)
    y = rf_df['Offensive rating']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

    rf = RandomForestRegressor()

    # Define the parameter grid to search
    param_grid_rf = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }

    #Create the GridSearchCV object
    grid_search_rf = GridSearchCV(estimator=rf, param_grid=param_grid_rf, scoring='neg_mean_squared_error', cv=2)

    #Fit the grid search to the data
    grid_search_rf.fit(X_train, y_train)

    #Get the best model
    best_rf = grid_search_rf.best_estimator_

    #Get the feature importances
    feature_importances = best_rf.feature_importances_

    #Create a dataframe to store the feature importances
    feature_importances_df = pd.DataFrame({'Feature': X.columns, 'Importance': feature_importances})

    #Sort the dataframe by importance
    feature_importances_df = feature_importances_df.sort_values(by='Importance', ascending=True)

    fig = px.bar(
        feature_importances_df,
        x='Importance',
        y='Feature',
        orientation='h',
        labels={
            'Importance': 'Feature Importance',
            'Feature': 'Feature'
        }
    )

    fig.update_layout(
        paper_bgcolor='#2c3e50',
        plot_bgcolor='#2c3e50',
        font=dict(color='#ecf0f1'),
        xaxis_tickfont_size=10,
        xaxis_categoryorder='total ascending'
    )

    return fig


######################  ML TESTING  ############################
X = df_ml.drop(['SEASON_2', 'TEAM_NAME', 'Offensive rating','total_shots_made', 'total_shots_attempted'], axis=1)
y = df_ml['Offensive rating']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

rf = RandomForestRegressor()

# Define the parameter grid to search
param_grid_rf = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

#Create the GridSearchCV object
grid_search_rf = GridSearchCV(estimator=rf, param_grid=param_grid_rf, scoring='neg_mean_squared_error', cv=2)

#Fit the grid search to the data
grid_search_rf.fit(X_train, y_train)

#Get the best model
best_rf = grid_search_rf.best_estimator_
print('Best model:', best_rf)
#####################################################################################################################

@app.callback(
    Output('predicted_offRating', 'figure'),
    Input('submit-button', 'n_clicks'),
    State('options-checklist', 'value'),
    State({'type': 'dynamic-input', 'index': ALL}, 'value'),
    State({'type': 'dynamic-input', 'index': ALL}, 'id')
)
def update_predicted_offRating(n_clicks, selected_options, input_values, input_ids):  
    # X = df_ml.drop(['SEASON_2', 'TEAM_NAME', 'Offensive rating','total_shots_made', 'total_shots_attempted'], axis=1)
    # y = df_ml['Offensive rating']

    total_2pt_made=np.mean(X.iloc[:,0])
    total_2pt_attempted=np.mean(X.iloc[:,1])
    total_3pt_made=np.mean(X.iloc[:,2])
    total_3pt_attempted=np.mean(X.iloc[:,3])
    clutch_shots_made=np.mean(X.iloc[:,4])
    average_shot_distance=np.mean(X.iloc[:,5])
    home_performance=np.mean(X.iloc[:,6])
    away_performance=np.mean(X.iloc[:,7])
    print('pushtarapis', total_3pt_made)
    if n_clicks > 0:
        input_values_dict = {id['index']: val for id, val in zip(input_ids, input_values)}
        for option in selected_options:
            value = input_values_dict.get(option, 'None')
            print('value', value )
            print('option', option)
            if (value.replace('.','',1).isdigit()):
                value = float(value)
            else:
                continue
            if ((value < 1000) & (value >= 0)):
                print('value 2', value )
                print('option 2', option)
                value = float(value)
                print('value 3', value )
                if option == 'total_2pt_made':
                    total_2pt_made = value
                elif option == 'total_2pt_attempted':
                    total_2pt_attempted = value
                elif option == 'total_3pt_made':
                    total_3pt_made = value
                    print('o misos en mesa')
                elif option == 'total_3pt_attempted':
                    total_3pt_attempted = value
                elif option == 'clutch_shots_made':
                    clutch_shots_made = value
                elif option == 'average_shot_distance':
                    average_shot_distance = value
                elif option == 'home_performance':
                    home_performance = value
                elif option == 'away_performance':
                    away_performance = value
                else:
                    print(f'Error at option: {option}')               


            print(f'Option: {option}, Text: {value}')


    print('yo wassup', total_3pt_made)


    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

    # rf = RandomForestRegressor()

    # # Define the parameter grid to search
    # param_grid_rf = {
    #     'n_estimators': [50, 100, 200],
    #     'max_depth': [None, 10, 20],
    #     'min_samples_split': [2, 5, 10],
    #     'min_samples_leaf': [1, 2, 4]
    # }

    # #Create the GridSearchCV object
    # grid_search_rf = GridSearchCV(estimator=rf, param_grid=param_grid_rf, scoring='neg_mean_squared_error', cv=2)

    # #Fit the grid search to the data
    # grid_search_rf.fit(X_train, y_train)

    # #Get the best model
    # best_rf = grid_search_rf.best_estimator_

    input_data = X.iloc[:1].copy(deep=False)
    input_data.iloc[0,0] = total_2pt_made
    input_data.iloc[0,1] = total_2pt_attempted
    input_data.iloc[0,2] = total_3pt_made
    input_data.iloc[0,3] = total_3pt_attempted
    input_data.iloc[0,4] = clutch_shots_made
    input_data.iloc[0,5] = average_shot_distance
    input_data.iloc[0,6] = home_performance
    input_data.iloc[0,7] = away_performance

    print('developers',input_data.iloc[0,2])

    teams_average_offensive_rating = df_ml.groupby('TEAM_NAME')['Offensive rating'].mean().reset_index()
    teams_average_offensive_rating = teams_average_offensive_rating._append({'TEAM_NAME': 'User Team', 'Offensive rating': best_rf.predict(input_data)[0]}, ignore_index=True)

    # Create a color column where all teams are one color, except 'Users Team'
    teams_average_offensive_rating['color'] = ['User Team' if team == 'User Team' else 'Other Teams' for team in teams_average_offensive_rating['TEAM_NAME']]

# Create the bar plot
    fig = px.bar(teams_average_offensive_rating, x='TEAM_NAME', y='Offensive rating', color='color', 
            color_discrete_map={'User Team': 'red', 'Other Teams': 'blue'},
            title='Teams average offensive rating')
    fig.update_yaxes(range=[80, 120])
    
    fig.update_layout(
        paper_bgcolor='#2c3e50',
        plot_bgcolor='#2c3e50',
        font=dict(color='#ecf0f1'),
        xaxis_tickfont_size=10,
        xaxis_categoryorder='total ascending'
    )

    return fig


################ giorkos ################
@app.callback(
    Output('dynamic-inputs', 'children'),
    Input('options-checklist', 'value')
)
def display_inputs(selected_options):
    rows = []
    for opt in options:
        if opt['value'] in selected_options:
            rows.append(
                dbc.Row([
                    dbc.Col(
                        dbc.Label(opt['label']),
                        width=2
                    ),
                    dbc.Col(
                        dcc.Input(id={'type': 'dynamic-input', 'index': opt["value"]}, type='text', placeholder=f'Enter value for {opt["label"]}', style={'width': '100%'}),
                        width=10
                    )
                ], style={'marginBottom': '10px'})
            )
    return rows

############################################


if __name__ == '__main__':
    app.run_server(debug=True)