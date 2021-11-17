# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 12:12:36 2021

@author: Admin
"""

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import sys

def get_country_players(cric_format, data_df):
    format_stats = []
    format_stats.append(data_df[0])
    if cric_format.lower() == 'test':
        x, y = 1, 6
    elif cric_format.lower() == 'odi':
        x, y = 6, 11
    else: 
        x, y = 11, 16
    for i in range(x, y):
        format_stats.append(data_df[i])
    format_stats = pd.DataFrame(format_stats)
    format_stats = format_stats.T
    format_stats.columns = format_stats.iloc[0]
    format_stats = format_stats.iloc[1 :].reset_index(drop = True)
    format_stats['M'].replace('', np.nan, inplace=True)
    format_stats.dropna(subset = ['M'], inplace=True)
    return format_stats

def check_name(country_name):
    name_code = {'afghanistan': 'AFG', 'australia': 'AUS', 'bangladesh': 'BAN', 'england': 'ENG', 'india': 'IND',
                 'ireland': 'IRE', 'kenya': 'KEN', 'namibia': 'NAM', 'nepal': 'NEP', 'netherlands': 'NED',
                 'new zealand': 'NZL', 'pakistan': 'PAK', 'scotland': 'sco', 'south africa': 'SAF', 'sri lanka': 'SRL',
                 'west indies': 'WIN', 'zimbabwe': 'ZIM'}
    if country_name in name_code:
        country_code = name_code[country_name]
    else: 
        print('Country name incorrect. Please run again.')
        sys.exit()
    return country_code

def country_numb(country_name):
    country_num = {'afghanistan': '25', 'australia': '01', 'bangladesh': '10', 'england': '02', 'india': '03',
                   'ireland': '24', 'kenya': '13', 'namibia': '17', 'nepal': '30', 'netherlands': '14',
                   'new zealand': '04', 'pakistan': '05', 'scotland': '15', 'south africa': '06', 'sri lanka': '07',
                   'west indies': '08', 'zimbabwe': '09'}
    return country_num[country_name]

def get_data(url, user_input):
    r = requests.get(url)
    soup = bs(r.content, 'html.parser')
    table = soup.find('table', {'class': 'TableLined'})
    data = []

    # get all the rows and columns
    rows = table.find_all('tr')
    for row in rows:   
        columns = row.find_all('td')
        columns = [x.text.strip() for x in columns]
        data.append([x for x in columns])

    data_df = pd.DataFrame(data) # convert to dataframe
    data_df.drop(index = data_df.index[0], axis = 0, inplace = True) # drop the first row
    
    out_df = []
    if user_input == '1' or user_input == '3':
        out_df = get_country_players(cric_format, data_df)
        if len(out_df['Name']) == 0:
            print(country_name.title() + ' has not played any matches in the ' + cric_format + ' format')
            sys.exit()
    elif user_input == '2':
        out_df = data_df.loc[1:6, 0:1]
        out_df = out_df.set_axis(['Attributes', 'Stats'], axis=1, inplace=False)
    return out_df
    
country_name = input('Country name: ').lower()
country_code = check_name(country_name)
country_num = country_numb(country_name)
user_input = input('Do you want to search for: \n 1. Country wise stats of all players \n 2. Overall country stats \n 3. Particular player \n Enter 1 or 2 or 3 \n')
#exit if incorrect user input
if user_input == '1' or user_input == '2':
    pass
elif user_input == '3':
    player_name = input('Enter player name: ').lower()
else:
    print('User input incorrect. Please run again.')
    sys.exit()
    
cric_format = input('Enter format (Test, ODI, T20): ').lower()
#exit if incorrect format
if cric_format == 'test' or cric_format == 'odi' or cric_format == 't20':
    pass
else:
    print('Cricket format incorrect. Please run again.')
    sys.exit()

if user_input == '1':
    url = str('http://www.howstat.com/cricket/Statistics/Players/PlayerCountryList.asp?Country=' + country_code)
    output_df = get_data(url, user_input)
    file_name = country_name + '_' + cric_format + '_' + 'players.csv'
elif user_input == '2':
    if cric_format == 'test':
        url = str('http://www.howstat.com/cricket/Statistics/Countries/CountryStats.asp?CountryCode=' + country_num)
    elif cric_format == 'odi':
        url = str('http://www.howstat.com/cricket/Statistics/Countries/CountryStats_ODI.asp?CountryCode=' + country_num)
    else:
        url = str('http://www.howstat.com/cricket/Statistics/Countries/CountryStats_T20.asp?CountryCode=' + country_num)
    output_df = get_data(url, user_input)
    file_name = country_name + '_' + cric_format + '_' + 'overall_stats.csv'
elif user_input == '3':
    url = str('http://www.howstat.com/cricket/Statistics/Players/PlayerCountryList.asp?Country=' + country_code)
    output_df = get_data(url, user_input)
    output_df['Name'] = output_df['Name'].str.rstrip('*')
    output_df['Name'] = output_df['Name'].str.lower()
    if output_df['Name'].str.contains(player_name).sum() > 0:
        output_df = output_df[output_df['Name'] == player_name]
        output_df['Name'] = output_df['Name'].str.title()
    else:
        print(player_name + ' has not played in this format. Please run again.')
        sys.exit()

output_df.index = np.arange(1, len(output_df) + 1)

save_file = input('Do you want to save the output?: ').lower()

if save_file == 'yes' or save_file == 'y':
    output_df.to_csv(file_name)
else:
    print(output_df)