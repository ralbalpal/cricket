# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 12:12:36 2021

@author: Admin
"""

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import warnings

warnings.filterwarnings("ignore") #suppress all warnings

def get_player_id(player_name):
    players = pd.read_csv('cricket_data.csv')
    players['NAME'] = players['NAME'].str.lower()
    player_search = players[players['NAME'] == player_name]
    return player_search['ID']

def batting_stats(data_df):    
    data_df = data_df.drop(data_df.columns[[9, 13]], axis = 1) #remove unwanted columns
    data_df.columns = ['Runs', 'Mins', 'BF', '4s', '6s','SR', 'Pos','Dismissal', 
                      'Inns', 'Opposition','Ground', 'Start Date'] #column headers
    #data cleaning
    data_df['Runs'] = data_df['Runs'].str.rstrip('*')
    data_df = data_df[data_df['Runs'].str.contains('DNB|TDNB')==False]
    data_df['Runs'] = pd.to_numeric(data_df['Runs'])
    data_df['Opposition'] = data_df['Opposition'].str[2:]
    #cumulative no. of outs for rolling average
    outs = [0] * len(data_df)
    data_df = data_df.reset_index(drop=True)
    if data_df['Dismissal'][0] != 'not out':
        outs[0] = 1
    elif data_df['Dismissal'][0] == 'not out':
        outs[0] = 0
    for i in range(1, len(data_df)):
        if data_df['Dismissal'][i] != 'not out':
            outs[i] = outs[i - 1] + 1
        elif data_df['Dismissal'][i] == 'not out':
            outs[i] = outs[i - 1]
    data_df['No. of innings'] = data_df.index + 1
    #rolling average
    data_df['No. of outs'] = outs
    data_df['Cumulative runs'] = data_df['Runs'].cumsum() #cumulative runs
    data_df['Rolling Avg'] = data_df['Cumulative runs'] / data_df['No. of outs']
    #retun
    return data_df
    
player_name = input('Enter player (min. 10 innings played): ').lower()
player_id = get_player_id(player_name).iloc[0]
cric_format = input('Enter format (Test, ODI, T20): ').lower()
#exit if incorrect format
if cric_format == 'test' or cric_format == 'odi' or cric_format == 't20':
    pass
else:
    print('Cricket format incorrect. Please run again.')
    sys.exit()
#update url for cric_format
if cric_format == 'test':
    cric_format = '1'
elif cric_format == 'odi':
    cric_format = '2'
else: 
    cric_format = '3'
    
record_type = input('Do you want to search for: \n 1. batting stats \n 2. or bowling stats \n Enter 1 or 2 \n')
if record_type == '1':
    record_type = 'batting'
elif record_type == '2':
  record_type = 'bowling'
else:
    print('User input incorrect. Please run again.')
    sys.exit()

match_range = input('How many matches do you want to analyse (min. 10 innings)? Leave blank for all innings ')
if match_range == '':
    match_range = 0
elif match_range != '' and match_range.isdigit() == False:
    print('Please run again and input a numeric value.')
    sys.exit()
elif int(match_range) < 10:
    print('Min. 10 innings required. Please run again.')
    sys.exit()
match_range = int(match_range)

url = str('https://stats.espncricinfo.com/ci/engine/player/' + str(player_id) + '.html?class=' + cric_format + ';template=results;type=' + record_type + ';view=innings')
r = requests.get(url)
soup = bs(r.content, 'html.parser')
for caption in soup.find_all('caption'):
    if caption.get_text() == 'Innings by innings list':
        table = caption.find_parent('table', {'class': 'engineTable'})

data = []

# get all the rows and columns
rows = table.find_all('tr')
for row in rows:   
    columns = row.find_all('td')
    columns = [x.text.strip() for x in columns]
    data.append([x for x in columns])

data_df = pd.DataFrame(data) # convert to dataframe
data_df.drop(index = data_df.index[0], axis = 0, inplace = True) # drop the first row

batting_df = batting_stats(data_df)
if match_range != 0:
    batting_df = batting_df.tail(match_range)
    
graph_1 = batting_df.plot(x = 'No. of innings', y = 'Rolling Avg')
plt.show(graph_1)

group_avg_runs = batting_df.groupby('Opposition')['Runs'].mean()
group_sum_runs = batting_df.groupby('Opposition')['Runs'].sum()

group_sum_runs = group_sum_runs.to_frame().reset_index()
plt.title('Total Runs by Team')
graph_2 = sns.barplot(x = 'Opposition', y = 'Runs', data = group_sum_runs)
plt.show(graph_2)

group_avg_runs = group_avg_runs.to_frame().reset_index()
plt.title('Average Runs by Team')
graph_3 = sns.lineplot(x = 'Opposition', y = 'Runs', data = group_avg_runs, sort=False)
plt.show(graph_3)