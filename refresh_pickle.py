import requests
import urllib3
import streamlit as st
import pandas as pd
import warnings

from meteostat import Point, Hourly, units
from concurrent.futures import ThreadPoolExecutor

warnings.simplefilter(action='ignore', category=FutureWarning)

##### STRAVA API DATA EXTRACTION ####
# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

auth_url = 'https://www.strava.com/oauth/token'

payload = {
    'client_id': st.secrets['client_id'],
    'client_secret': st.secrets['client_secret'],
    'refresh_token': st.secrets['refresh_token'],
    'grant_type': 'refresh_token',
    'f': 'json'
}

res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']

header = {'Authorization': 'Bearer ' + access_token}

def get_activities_data() -> pd.DataFrame:
    '''This function gets all activities data from Strava API
    
    Returns:
        data (DataFrame): Normalized JSON data of activities'''
        
    # set the URL for the Strava API
    activities_url = 'https://www.strava.com/api/v3/athlete/activities'
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

        if page > 20:
            print('Stopping after 20 pages to avoid excessive API calls')
            break
        
    return pd.json_normalize(data)

activity_data_backup = get_activities_data()
activity_data_backup.to_pickle('data/activity_data_backup.pkl')
print("Activity backup file saved in data folder.")