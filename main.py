import pandas as pd
import requests
import urllib3
import streamlit as st

import login as login

##### STRAVA API DATA EXTRACTION ####
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

auth_url = 'https://www.strava.com/oauth/token'
activities_url = 'https://www.strava.com/api/v3/athlete/activities'
gear_url = 'https://www.strava.com/api/v3/gear/{id}'

payload = {
    'client_id': f'{login.client_id}',
    'client_secret': f'{login.client_secret}',
    'refresh_token': f'{login.refresh_token}',
    'grant_type': 'refresh_token',
    'f': 'json'
}

res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']

header = {'Authorization': 'Bearer ' + access_token}

# Strava API only allows 200 results per page. This function loops through until all results are collected
def get_activities_data():
    '''This function gets all activities data from Strava API'''
    # set value of page to start at page 1
    page = 1
    # create an empty list to store all data
    data = []
    # set new_results to True to start the loop
    new_results = True
    while new_results:
        # requests one page at a time (200 results)
        get_activities = requests.get(activities_url, headers=header, params={'per_page': 200, 'page': page}).json()
        # feedback
        print(f"Fetching page {page}")
        print(f"Number of activities fetched: {len(get_activities)}")
        # if there are no results, the loop will stop
        new_results = get_activities
        # add the results to the data list
        data.extend(get_activities)
        # increment the page number
        page += 1
    return pd.json_normalize(data)
        
# get all activities data
activities = get_activities_data()

# convert meters to miles
activities.distance = (activities.distance / 1609.34).round(2)
# convert to mph
activities.average_speed = (activities.average_speed * 2.23694).round(2)
activities.max_speed = (activities.max_speed * 2.23694).round(2)
# convert to feet
activities.total_elevation_gain = (activities.total_elevation_gain * 3.28084).round(2)
activities.elev_high = (activities.elev_high * 3.28084).round(2)
activities.elev_low = (activities.elev_low * 3.28084).round(2)

activities_df = pd.DataFrame(activities)

# get distinct gear id's
gear_list = activities_df['gear_id'].unique()

gear_list = gear_list[~pd.isnull(gear_list)]

def get_gear_data(gear_list):
    '''This function gets gear data from Strava API
    
    Args:
        gear_list (array): List of distinct gear ids
        
        Returns:
            data (JSON): JSON data of gear
        '''
    # create empty list to store gear data
    data = []
    # loop through gear_list and get gear data
    for gear_id in gear_list:
        get_gear = requests.get(gear_url.format(id=gear_id), headers=header).json()
        data.append(get_gear)
    return pd.json_normalize(data)

# get all gear data
gear = get_gear_data(gear_list)

# convert meters to miles
gear.distance = gear.distance / 1609.34

gear = gear.drop(columns=['converted_distance'])

##### DATA CLEANING AND TRANSFORMATION #####
# create base dataframe joining activity and gear data
df = pd.merge(activities_df, gear, how='left', left_on='gear_id', right_on='id', suffixes=('_activity', '_gear')).drop(columns='id_gear')

# convert moving_time and elapsed time to H% M% S% format
df['moving_time'] = pd.to_datetime(df['moving_time'], unit='s').dt.strftime('%H:%M:%S')
df['elapsed_time'] = pd.to_datetime(df['elapsed_time'], unit='s').dt.strftime('%H:%M:%S')

# convert start_date and start_date_local to datetime
df['start_date'] = pd.to_datetime(df['start_date']).dt.strftime('%Y-%m-%d %H:%M:%S')
df['start_date_local'] = pd.to_datetime(df['start_date_local']).dt.strftime('%Y-%m-%d %H:%M:%S')

# add start time for analysis and in am/pm format
df['start_time_local_24h'] = pd.to_datetime(df['start_date_local']).dt.strftime('%H:%M:%S')
df['start_time_local_12h'] = pd.to_datetime(df['start_date_local']).dt.strftime("%I:%M %p")

# add day of week
df['day_of_week'] = pd.to_datetime(df['start_date_local']).dt.day_name()

# add year label
df['year'] = pd.to_datetime(df['start_date_local']).dt.year

# max date
max_date = df['start_date_local'].max()

# TODO create distict activity type list
# TODO create distinct gear type list
# TODO create distinct year list
# TODO create rolling 12 mo variable

##### STREAMLIT DASHBOARD #####
# TODO - create streamlit dashboard
st.title('Tom Runs The World')
st.subheader('Strava Data Analysis')
st.caption('Data as of: ' + max_date)
st.button('Refresh Data')
st.divider()
with st.sidebar:
  st.subheader('Filters')
  st.segmented_control('Activity Type', ['All', 'distinct activity types'])
  st.selectbox('Years', [2025, 2024, 'All', 'Rolling 12 mo'])
st.header('Total Activities')

tot_act_col1, tot_act_col2, tot_act_col3, tot_act_col4 = st.columns(4)

with tot_act_col1:
    st.metric('Activities', 12)
with tot_act_col2:
    st.metric('Distance', '12 mi')
with tot_act_col3:
    st.metric('Elevation', '12 ft')
with tot_act_col4:
    st.metric('Time', '12:00:00')