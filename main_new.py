import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
#read data from csv file and create a dataframe
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from ydata_profiling import ProfileReport

#read data from csv file
data = pd.read_csv('NBA_2004_2023_Shots.csv')
# print(data.head().describe())
# profile = ProfileReport(data, title='Pandas Profiling Report', explorative=True)
# profile.to_notebook_iframe()
# print(data.columns)
pd.set_option('display.max_columns', None)
# Display one instance for each team
# teams_sample = data.groupby('TEAM_NAME').first().reset_index()
# print(teams_sample)

# Create a new DataFrame for player season stats
player_season_stats = pd.DataFrame()

# Player Season Stats
grouped = data.groupby(['SEASON_2', 'PLAYER_ID', 'PLAYER_NAME'])

player_season_stats['position'] = grouped['POSITION'].first()
player_season_stats['total_shots_made'] = grouped['SHOT_MADE'].sum()
player_season_stats['total_shots_attempted'] = grouped['SHOT_MADE'].count()
player_season_stats['total_2pt_made'] = grouped.apply(lambda x: x[(x['SHOT_TYPE'] == '2PT Field Goal') & (x['SHOT_MADE'] == True)].shape[0])
player_season_stats['total_2pt_attempted'] = grouped.apply(lambda x: x[x['SHOT_TYPE'] == '2PT Field Goal'].shape[0])
player_season_stats['total_3pt_made'] = grouped.apply(lambda x: x[(x['SHOT_TYPE'] == '3PT Field Goal') & (x['SHOT_MADE'] == True)].shape[0])
player_season_stats['total_3pt_attempted'] = grouped.apply(lambda x: x[x['SHOT_TYPE'] == '3PT Field Goal'].shape[0])
player_season_stats['preferred_shot_zone'] = grouped['ZONE_NAME'].agg(lambda x: x.value_counts().idxmax())
player_season_stats['clutch_shots_made'] = grouped.apply(lambda x: x[(x['QUARTER'] == 4) & (x['MINS_LEFT'] < 2) & (x['SHOT_MADE'] == True)].shape[0])
player_season_stats['preferred_action_type'] = grouped['ACTION_TYPE'].agg(lambda x: x.value_counts().idxmax())
player_season_stats['average_shot_distance'] = grouped['SHOT_DISTANCE'].mean()


player_season_stats = player_season_stats.sort_values(by=['PLAYER_NAME','SEASON_2'], ascending=[True, True])

# Reset the index to have a clean DataFrame
player_season_stats = player_season_stats.reset_index()

# Save the new dataset to a CSV file
player_season_stats.to_csv('player_season_stats.csv', index=False)

# Display the first few rows of the new dataset
print(player_season_stats.head())

# Update rows where TEAM_NAME is 'Charlotte Bobcats' and change 'CHA' to 'CHB' in HOME_TEAM and AWAY_TEAM
data.loc[(data['TEAM_NAME'] == 'Charlotte Bobcats') & (data['HOME_TEAM'] == 'CHA'), 'HOME_TEAM'] = 'CHB'
data.loc[(data['TEAM_NAME'] == 'Charlotte Bobcats') & (data['AWAY_TEAM'] == 'CHA'), 'AWAY_TEAM'] = 'CHB'

# Dictionary mapping acronyms to full team names
team_full_names = {
    'ATL': 'Atlanta Hawks',
    'BOS': 'Boston Celtics',
    'BKN': 'Brooklyn Nets',
    'CHA': 'Charlotte Hornets',
    'CHB': 'Charlotte Bobcats',  # Newly added
    'CHI': 'Chicago Bulls',
    'CLE': 'Cleveland Cavaliers',
    'DAL': 'Dallas Mavericks',
    'DEN': 'Denver Nuggets',
    'DET': 'Detroit Pistons',
    'GSW': 'Golden State Warriors',
    'HOU': 'Houston Rockets',
    'IND': 'Indiana Pacers',
    'LAC': 'Los Angeles Clippers',
    'LAL': 'Los Angeles Lakers',
    'MEM': 'Memphis Grizzlies',
    'MIA': 'Miami Heat',
    'MIL': 'Milwaukee Bucks',
    'MIN': 'Minnesota Timberwolves',
    'NJN': 'New Jersey Nets',  # Historical team
    'NOH': 'New Orleans Hornets',
    'NOP': 'New Orleans Pelicans',
    'NOK': 'New Orleans/Oklahoma City Hornets',  # Historical team
    'NYK': 'New York Knicks',
    'OKC': 'Oklahoma City Thunder',
    'ORL': 'Orlando Magic',
    'PHI': 'Philadelphia 76ers',
    'PHX': 'Phoenix Suns',
    'POR': 'Portland Trail Blazers',
    'SAC': 'Sacramento Kings',
    'SAS': 'San Antonio Spurs',
    'SEA': 'Seattle SuperSonics',  # Historical team
    'TOR': 'Toronto Raptors',
    'UTA': 'Utah Jazz',
    'VAN': 'Vancouver Grizzlies',  # Historical team
    'WAS': 'Washington Wizards'
}

# Replace acronyms with full team names in HOME_TEAM and AWAY_TEAM
data['HOME_TEAM'] = data['HOME_TEAM'].map(lambda x: team_full_names.get(x, x))
data['AWAY_TEAM'] = data['AWAY_TEAM'].map(lambda x: team_full_names.get(x, x))

# Teams Dataset
team_season_stats = pd.DataFrame()

grouped_team = data.groupby(['SEASON_2', 'TEAM_ID', 'TEAM_NAME'])

team_season_stats['total_shots_made'] = grouped_team['SHOT_MADE'].sum()
team_season_stats['total_shots_attempted'] = grouped_team['SHOT_MADE'].count()
team_season_stats['total_2pt_made'] = grouped_team.apply(lambda x: x[(x['SHOT_TYPE'] == '2PT Field Goal') & (x['SHOT_MADE'] == True)].shape[0])
team_season_stats['total_2pt_attempted'] = grouped_team.apply(lambda x: x[x['SHOT_TYPE'] == '2PT Field Goal'].shape[0])
team_season_stats['total_3pt_made'] = grouped_team.apply(lambda x: x[(x['SHOT_TYPE'] == '3PT Field Goal') & (x['SHOT_MADE'] == True)].shape[0])
team_season_stats['total_3pt_attempted'] = grouped_team.apply(lambda x: x[x['SHOT_TYPE'] == '3PT Field Goal'].shape[0])
team_season_stats['preferred_shot_zone'] = grouped_team['ZONE_NAME'].agg(lambda x: x.value_counts().idxmax())
team_season_stats['clutch_shots_made'] = grouped_team.apply(lambda x: x[(x['QUARTER'] == 4) & (x['MINS_LEFT'] < 2) & (x['SHOT_MADE'] == True)].shape[0])
team_season_stats['average_shot_distance'] = grouped_team['SHOT_DISTANCE'].mean()
team_season_stats['home_performance'] = grouped_team.apply(lambda x: x[x['HOME_TEAM'] == x['TEAM_NAME']]['SHOT_MADE'].mean())
team_season_stats['away_performance'] = grouped_team.apply(lambda x: x[x['AWAY_TEAM'] == x['TEAM_NAME']]['SHOT_MADE'].mean())

team_season_stats = team_season_stats.sort_values(by=['TEAM_NAME','SEASON_2'], ascending=[True, True])

# Reset the index to have a clean DataFrame
team_season_stats = team_season_stats.reset_index()

# Save the new dataset to a CSV file
team_season_stats.to_csv('team_season_stats.csv', index=False)

# Display the first few rows of the new dataset
print(team_season_stats.head())
