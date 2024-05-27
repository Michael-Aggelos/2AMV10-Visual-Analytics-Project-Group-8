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


# Player Shot Accuracy
player_shot_accuracy = data.groupby('PLAYER_NAME')['SHOT_MADE'].mean().reset_index()
player_shot_accuracy.columns = ['PLAYER_NAME', 'Player_Shot_Accuracy']

# Preferred Shot Zone
preferred_shot_zone = data[data['SHOT_MADE'] == True].groupby('PLAYER_NAME')['BASIC_ZONE'].agg(lambda x: x.mode()[0] if not x.mode().empty else 'Unknown').reset_index()
preferred_shot_zone.columns = ['PLAYER_NAME', 'Preferred_Shot_Zone']

# Clutch Shots Made
clutch_shots_made = data[(data['QUARTER'] == 4) & (data['MINS_LEFT'] < 2)].groupby('PLAYER_NAME')['SHOT_MADE'].sum().reset_index()
clutch_shots_made.columns = ['PLAYER_NAME', 'Clutch_Shots_Made']

# Average Shot Distance
average_shot_distance = data.groupby('PLAYER_NAME')['SHOT_DISTANCE'].mean().reset_index()
average_shot_distance.columns = ['PLAYER_NAME', 'Avg_Shot_Distance']

# Combine all player features into a single DataFrame
player_features = player_shot_accuracy.merge(preferred_shot_zone, on='PLAYER_NAME').merge(clutch_shots_made, on='PLAYER_NAME').merge(average_shot_distance, on='PLAYER_NAME')

# Display the new player features
print(player_features.head())



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

# Team Shot Accuracy
team_shot_accuracy = data.groupby('TEAM_NAME')['SHOT_MADE'].mean().reset_index()
team_shot_accuracy.columns = ['TEAM_NAME', 'Team_Shot_Accuracy']

# Home vs Away Performance
home_performance = data[data['HOME_TEAM'] == data['TEAM_NAME']].groupby('TEAM_NAME')['SHOT_MADE'].mean().reset_index()
away_performance = data[data['AWAY_TEAM'] == data['TEAM_NAME']].groupby('TEAM_NAME')['SHOT_MADE'].mean().reset_index()
home_performance.columns = ['TEAM_NAME', 'Home_Performance']
away_performance.columns = ['TEAM_NAME', 'Away_Performance']

# Ensure team names are unique
home_performance = home_performance.drop_duplicates(subset=['TEAM_NAME'])
away_performance = away_performance.drop_duplicates(subset=['TEAM_NAME'])

# Combine team features into a single DataFrame
team_features = team_shot_accuracy.merge(home_performance, on='TEAM_NAME', how='left').merge(away_performance, on='TEAM_NAME', how='left')

# Display the new team features
print(team_features.head())

# Display one instance for each team
teams_sample = data.groupby('TEAM_NAME').first().reset_index()
print(teams_sample)
