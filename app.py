from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)


app.layout = html.Div([
    html.H4('Animated 2-pts and 3-pts shots attempts by teams in the NBA (2004-2023)'),
    html.P("Select an animation:"),
    dcc.RadioItems(
        id='selection',
        options=["2-pts", "3-pts"],
        value='2-pts',
    ),
    dcc.Loading(dcc.Graph(id="graph"), type="cube")
])


@app.callback(
    Output("graph", "figure"), 
    Input("selection", "value"))
def display_animated_graph(selection):
    df = pd.read_csv('team_season_stats.csv')
    animations = {
        '2-pts': px.scatter(
           df, x="total_2pt_attempted", y="total_shots_attempted", animation_frame="SEASON_2", 
            animation_group="TEAM_NAME", size="total_2pt_made", color="TEAM_NAME", 
            hover_name="TEAM_NAME", range_x=[3000,7000], range_y=[5000,8000]),
        '3-pts': px.scatter(
            df, x="total_3pt_attempted", y="total_shots_attempted", color="TEAM_NAME", 
            animation_frame="SEASON_2", animation_group="TEAM_NAME", size="total_3pt_made",
            range_x=[0,6000], range_y=[5000,8000]),
    }
    return animations[selection]


app.run_server(debug=True)