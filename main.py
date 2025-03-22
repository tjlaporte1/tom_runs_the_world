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

# res = requests.post(auth_url, data=payload, verify=False)
# access_token = res.json()['access_token']

# header = {'Authorization': 'Bearer ' + access_token}

# # Strava API only allows 200 results per page. This function loops through until all results are collected
# def get_activities_data():
#     '''This function gets all activities data from Strava API'''
#     # set value of page to start at page 1
#     page = 1
#     # create an empty list to store all data
#     data = []
#     # set new_results to True to start the loop
#     new_results = True
#     while new_results:
#         # requests one page at a time (200 results)
#         get_activities = requests.get(activities_url, headers=header, params={'per_page': 200, 'page': page}).json()
#         # feedback
#         print(f"Fetching page {page}")
#         print(f"Number of activities fetched: {len(get_activities)}")
#         # if there are no results, the loop will stop
#         new_results = get_activities
#         # add the results to the data list
#         data.extend(get_activities)
#         # increment the page number
#         page += 1

#         if page > 20:
#             print('Stopping after 20 pages to avoid excessive API calls')
#             break
        
#     return pd.json_normalize(data)
        
# # get all activities data
# activities = get_activities_data()

# # convert meters to miles
# activities.distance = (activities.distance / 1609.34).round(2)
# # convert to mph
# activities.average_speed = (activities.average_speed * 2.23694).round(2)
# activities.max_speed = (activities.max_speed * 2.23694).round(2)
# # convert to feet
# activities.total_elevation_gain = (activities.total_elevation_gain * 3.28084).round(2)
# activities.elev_high = (activities.elev_high * 3.28084).round(2)
# activities.elev_low = (activities.elev_low * 3.28084).round(2)

# activities_df = pd.DataFrame(activities)

# # get distinct gear id's
# gear_id_list = activities_df['gear_id'].unique()
# gear_id_list = gear_id_list[~pd.isnull(gear_id_list)]

# def get_gear_data(gear_list):
#     '''This function gets gear data from Strava API
    
#     Args:
#         gear_list (array): List of distinct gear ids
        
#         Returns:
#             data (JSON): JSON data of gear
#         '''
#     # create empty list to store gear data
#     data = []
#     # loop through gear_list and get gear data
#     for gear_id in gear_list:
#         get_gear = requests.get(gear_url.format(id=gear_id), headers=header).json()
#         data.append(get_gear)
#     return pd.json_normalize(data)

# # get all gear data
# gear = get_gear_data(gear_id_list)

# # convert meters to miles
# gear.distance = gear.distance / 1609.34

# gear = gear.drop(columns=['converted_distance'])

# ##### DATA CLEANING AND TRANSFORMATION #####
# # create base dataframe joining activity and gear data
# pre_df = pd.merge(activities_df,
#                   gear, 
#                   how='left',
#                   left_on='gear_id',
#                   right_on='id',
#                   suffixes=('_activity', '_gear')).drop(columns='id_gear')

# # convert moving_time and elapsed time to H% M% S% format
# pre_df['moving_time'] = pd.to_datetime(pre_df['moving_time'], unit='s').dt.strftime('%H:%M:%S')
# pre_df['elapsed_time'] = pd.to_datetime(pre_df['elapsed_time'], unit='s').dt.strftime('%H:%M:%S')

# # convert start_date and start_date_local to datetime
# pre_df['start_date'] = pd.to_datetime(pd.to_datetime(pre_df['start_date']).dt.strftime('%Y-%m-%d %H:%M:%S'))
# pre_df['start_date_local'] = pd.to_datetime(pd.to_datetime(pre_df['start_date_local']).dt.strftime('%Y-%m-%d %H:%M:%S'))

# # add start time for analysis and in am/pm format
# pre_df['start_time_local_24h'] = pd.to_datetime(pre_df['start_date_local']).dt.time
# pre_df['start_time_local_12h'] = pd.to_datetime(pre_df['start_date_local']).dt.strftime("%I:%M %p")

# # add day of week
# pre_df['day_of_week'] = pd.to_datetime(pre_df['start_date_local']).dt.day_name()

# # add month
# pre_df['month'] = pd.to_datetime(pre_df['start_date_local']).dt.month_name()

# # add year label
# pre_df['year'] = pd.to_datetime(pre_df['start_date_local']).dt.year

# df = pre_df.copy()

df = pd.read_csv('df.csv')

df['moving_time'] = pd.to_timedelta(df['moving_time'])
# max date
max_date = pd.to_datetime(df['start_date_local']).dt.strftime('%Y-%m-%d %I:%M %p').max()

# distict activity type list
act_type_filter = df['type'].value_counts().index.tolist()
act_type_filter = [activity if activity in ['Run', 'Hike', 'Walk', 'Ride'] else 'Other' for activity in act_type_filter]
act_type_filter = list(dict.fromkeys(act_type_filter))
act_type_filter.insert(0, 'All')
# distinct year list
year_filter = sorted(df['year'].unique().tolist(), reverse=True)
year_filter.insert(0, 'All')
year_filter.insert(1, 'Rolling 12 Months')
# rolling 12 mo variable
today = pd.to_datetime(max_date)
rolling_12_months = today - pd.DateOffset(months=12)

# cache df
@st.cache_data
def cache_df(df):
    '''This function caches the dataframe for faster laoding'''
    return df

df = cache_df(df)

##### STREAMLIT DASHBOARD #####
page_head = st.container()
page_head.title('Tom Runs The World')
page_head.subheader('Strava Data Analysis')
page_head.caption('Data as of: ' + max_date)
page_head.button('Refresh Data')
page_head.divider()

filter_col1, filter_col2 = st.columns([2, 1])
with filter_col1:
    act_type_selection = st.segmented_control('Activity Type', act_type_filter, default='All')
with filter_col2:
    year_selection = st.selectbox('Years', year_filter, index=1)
  
st.header('Total Activities')

def metric_calc(act_type_selection, year_selection, metric=['Activities', 'Distance', 'Elevation', 'Time'], field=['upload_id', 'distance_activity', 'total_elevation_gain', 'moving_time']):
    '''This function calculates the metrics for the overview section
    
    Args:
        metric (str): The metric to calculate, becomes the metrics name
        field (str): The field in the dataframe to use to calculate the metric which is used to sum or view distinct count
        act_type_selection (str): The selected activity type
        year_selection (str): The selected year
        
        Returns:
            metric_result (int): The calculated metric
    '''
    def convert_timedelta(td):
        '''This function converts a timedelta object to a string in hours and minutes'''
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours} hrs {minutes} min"

    if metric == 'Activities':
        if act_type_selection == 'All' and year_selection == 'All':
            metric_result = st.metric(metric, df[field].nunique())
            
        elif act_type_selection == 'All' and year_selection not in ['All', 'Rolling 12 Months']:
            metric_result = st.metric(metric, (df.loc[df['year'] == year_selection, field].nunique()))
            
        elif act_type_selection == 'All' and year_selection == 'Rolling 12 Months':
            metric_result = st.metric(metric, df.loc[pd.to_datetime(df['start_date_local']) >= rolling_12_months, field].nunique())
            
        elif act_type_selection == 'Other' and year_selection == 'All':
            metric_result = st.metric(metric, df.loc[~df['type'].isin(['Run', 'Hike', 'Walk', 'Ride']), field].nunique())
            
        elif act_type_selection == 'Other' and year_selection not in ['All', 'Rolling 12 Months']:
            metric_result = st.metric(metric, df.loc[(~df['type'].isin(['Run', 'Hike', 'Walk', 'Ride']))
                                                     & (df['year'] == year_selection), field].nunique())
            
        elif act_type_selection == 'Other' and year_selection == 'Rolling 12 Months':
            metric_result = st.metric(metric, df.loc[(~df['type'].isin(['Run', 'Hike', 'Walk', 'Ride']))
                                            & (pd.to_datetime(df['start_date_local']) >= rolling_12_months), field].nunique())
            
        elif act_type_selection == 'Other' and year_selection not in ['All', 'Rolling 12 Months']:
            metric_result = st.metric(metric, (df.loc[(~df['type'].isin(['Run', 'Hike', 'Walk', 'Ride']))
                                                      & (df['year'] == year_selection), field].nunique()))
            
        elif act_type_selection not in ['All', 'Other'] and year_selection == 'All':
            metric_result = st.metric(metric, df.loc[df['type'] == act_type_selection, field].nunique())
            
        elif act_type_selection not in ['All', 'Other'] and year_selection == 'Rolling 12 Months':
            metric_result = st.metric(metric, df.loc[(df['type'] == act_type_selection)
                                            & (pd.to_datetime(df['start_date_local']) >= rolling_12_months), field].nunique())
        else:
            metric_result = st.metric(metric, df.loc[(df['type'] == act_type_selection)
                                        & (df['year'] == year_selection), field].nunique())
    elif metric == 'Time':
        if act_type_selection == 'All' and year_selection == 'All':
            metric_result = st.metric(metric, convert_timedelta(df[field].sum()))
        elif act_type_selection == 'All' and year_selection not in ['All', 'Rolling 12 Months']:
            metric_result = st.metric(metric, convert_timedelta(df.loc[df['year'] == year_selection, field].sum()))
        elif act_type_selection == 'All' and year_selection == 'Rolling 12 Months':
            metric_result = st.metric(metric, convert_timedelta(df.loc[pd.to_datetime(df['start_date_local']) >= rolling_12_months, field].sum()))
        elif act_type_selection == 'Other' and year_selection == 'All':
            metric_result = st.metric(metric, convert_timedelta(df.loc[~df['type'].isin(['Run', 'Hike', 'Walk', 'Ride']), field].sum()))
        elif act_type_selection == 'Other' and year_selection not in ['All', 'Rolling 12 Months']:
            metric_result = st.metric(metric, convert_timedelta(df.loc[(~df['type'].isin(['Run', 'Hike', 'Walk', 'Ride']))
                                                     & (df['year'] == year_selection), field].sum()))
        elif act_type_selection == 'Other' and year_selection == 'Rolling 12 Months':
            metric_result = st.metric(metric, convert_timedelta(df.loc[(~df['type'].isin(['Run', 'Hike', 'Walk', 'Ride']))
                                            & (pd.to_datetime(df['start_date_local']) >= rolling_12_months), field].sum()))
        elif act_type_selection == 'Other' and year_selection not in ['All', 'Rolling 12 Months']:
            metric_result = st.metric(metric, convert_timedelta(df.loc[(~df['type'].isin(['Run', 'Hike', 'Walk', 'Ride']))
                                                      & (df['year'] == year_selection), field].sum()))
        elif act_type_selection not in  ['All', 'Other'] and year_selection == 'All':
            metric_result = st.metric(metric, convert_timedelta(df.loc[df['type'] == act_type_selection, field].sum()))
        elif act_type_selection not in ['All', 'Other'] and year_selection == 'Rolling 12 Months':
            metric_result = st.metric(metric, convert_timedelta(df.loc[(df['type'] == act_type_selection)
                                            & (pd.to_datetime(df['start_date_local']) >= rolling_12_months), field].sum()))
        else:
            metric_result = st.metric(metric, convert_timedelta(df.loc[(df['type'] == act_type_selection)
                                        & (df['year'] == year_selection), field].sum()))
    else:
        if act_type_selection == 'All' and year_selection == 'All':
            metric_result = st.metric(metric, df[field].sum())
        elif act_type_selection == 'All' and year_selection not in ['All', 'Rolling 12 Months']:
            metric_result = st.metric(metric, int(df.loc[df['year'] == year_selection, field].sum()))
        elif act_type_selection == 'All' and year_selection == 'Rolling 12 Months':
            metric_result = st.metric(metric, df.loc[pd.to_datetime(df['start_date_local']) >= rolling_12_months, field].sum())
        elif act_type_selection != 'All' and year_selection == 'All':
            metric_result = st.metric(metric, df.loc[df['type'] == act_type_selection, field].sum())
        elif act_type_selection != 'All' and year_selection == 'Rolling 12 Months':
            metric_result = st.metric(metric, df.loc[(df['type'] == act_type_selection)
                                            & (pd.to_datetime(df['start_date_local']) >= rolling_12_months), field].sum())
        else:
            metric_result = st.metric(metric, df.loc[(df['type'] == act_type_selection)
                                        & (df['year'] == year_selection), field].sum())
            
    return metric_result

tot_act_col1, tot_act_col2, tot_act_col3, tot_act_col4 = st.columns(4)
with tot_act_col1:
    metric_calc(act_type_selection, year_selection, 'Activities', 'upload_id')
with tot_act_col2:
    metric_calc(act_type_selection, year_selection, 'Distance', 'distance_activity')
with tot_act_col3:
    metric_calc(act_type_selection, year_selection, 'Elevation', 'total_elevation_gain')
with tot_act_col4:
    metric_calc(act_type_selection, year_selection, 'Time', 'moving_time')