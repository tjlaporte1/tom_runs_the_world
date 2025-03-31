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

@st.cache_data
def get_data() -> pd.DataFrame:
    '''This function builds the dataframe from Strava API data. It is used to then cache the dataframe for faster loading in the Streamlit app.
    
    Returns:
        pre_df (DataFrame): DataFrame of activities and gear data'''
    
    # Strava API only allows 200 results per page. This function loops through until all results are collected
    def get_activities_data() -> pd.DataFrame:
        '''This function gets all activities data from Strava API
        
        Returns:
            data (DataFrame): Normalized JSON data of activities'''
            
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
    gear_id_list = activities_df['gear_id'].unique()
    gear_id_list = gear_id_list[~pd.isnull(gear_id_list)]

    def get_gear_data(gear_list: list) -> pd.DataFrame:
        '''This function gets gear data from Strava API
        
        Args:
            gear_list (array): List of distinct gear ids
            
            Returns:
                data (DataFrame): Normalized JSON data of gear'''
            
        # create empty list to store gear data
        data = []
        # loop through gear_list and get gear data
        for gear_id in gear_list:
            get_gear = requests.get(gear_url.format(id=gear_id), headers=header).json()
            data.append(get_gear)
        return pd.json_normalize(data)

    # get all gear data
    gear = get_gear_data(gear_id_list)

    # convert meters to miles
    gear.distance = gear.distance / 1609.34

    gear = gear.drop(columns=['converted_distance'])

    ##### DATA CLEANING AND TRANSFORMATION #####
    # create base dataframe joining activity and gear data
    pre_df = pd.merge(activities_df,
                    gear, 
                    how='left',
                    left_on='gear_id',
                    right_on='id',
                    suffixes=('_activity', '_gear')).drop(columns='id_gear')

    # convert moving_time and elapsed time to H% M% S% format
    pre_df['moving_time'] = pd.to_timedelta(pd.to_datetime(pre_df['moving_time'], unit='s').dt.strftime('%H:%M:%S'))
    pre_df['elapsed_time'] = pd.to_timedelta(pd.to_datetime(pre_df['elapsed_time'], unit='s').dt.strftime('%H:%M:%S'))

    # convert start_date and start_date_local to datetime
    pre_df['start_date'] = pd.to_datetime(pd.to_datetime(pre_df['start_date']).dt.strftime('%Y-%m-%d %H:%M:%S'))
    pre_df['start_date_local'] = pd.to_datetime(pd.to_datetime(pre_df['start_date_local']).dt.strftime('%Y-%m-%d %H:%M:%S'))

    # add start time for analysis and in am/pm format
    pre_df['start_time_local_24h'] = pd.to_datetime(pre_df['start_date_local']).dt.time
    pre_df['start_time_local_12h'] = pd.to_datetime(pre_df['start_date_local']).dt.strftime("%I:%M %p")

    # add day of week
    pre_df['day_of_week'] = pd.to_datetime(pre_df['start_date_local']).dt.day_name()

    # add month
    pre_df['month'] = pd.to_datetime(pre_df['start_date_local']).dt.month_name()

    # add month year
    pre_df['month_year'] = pd.to_datetime(pd.to_datetime(pre_df['start_date_local']).dt.strftime('%Y-%m'))
    
    # add month year name
    pre_df['month_year_name'] = pd.to_datetime(pre_df['start_date_local']).dt.strftime('%b %Y')

    # add year label
    pre_df['year'] = pd.to_datetime(pre_df['start_date_local']).dt.year
    
    return pre_df

df = get_data()

# max date
max_date = pd.to_datetime(df['start_date_local']).dt.strftime('%Y-%m-%d %I:%M %p').max()

# distict activity type list
highlighted_activities = ['Run', 'Hike', 'Walk', 'Ride']
act_type_filter = df['type'].value_counts().index.tolist()
#act_type_filter = [activity if activity in highlighted_activities else 'Other' for activity in act_type_filter]
act_type_filter = list(dict.fromkeys(act_type_filter))
#act_type_filter.insert(0, 'All')
# distinct year list
year_filter = sorted(df['year'].unique().tolist(), reverse=True)
year_filter.insert(0, 'All')
year_filter.insert(1, 'Rolling 12 Months')
# rolling 12 mo variable
today = pd.to_datetime(max_date)
rolling_12_months = today - pd.DateOffset(months=12)

##### STREAMLIT DASHBOARD #####
with st.container(): # page header
    st.title('Tom Runs The World')
    st.subheader('Strava Data Analysis')
    st.caption('Data as of: ' + max_date)
    st.divider()

# filters
filter_col1, filter_col2 = st.columns([3, 1])
with filter_col1:
    act_type_selection = st.segmented_control('Activity Type', act_type_filter, default=highlighted_activities, selection_mode='multi')
with filter_col2:
    year_selection = st.selectbox('Years', year_filter, index=1)

def df_query_builder(year_selection, gear_brand_selection=None) -> pd.DataFrame:
    '''This function builds a query to filter the dataframe based on the selected activity type, year and gear brand.
    
    Args:
        year_selection (str): Selected year from filter
        gear_brand_selection (str): Selected gear brand (optional)
        
    Returns:
        df (DataFrame): Filtered dataframe based on the selected filters'''
        
    conditions = []
    
    # activity type filter
    conditions.append("type in @act_type_selection")

    # year filter
    if year_selection == 'All':
        conditions.append("year != 'None'")
    elif year_selection == 'Rolling 12 Months':
        conditions.append("start_date_local >= @rolling_12_months")
    else:
        conditions.append("year == @year_selection")

    query = ' and '.join(conditions)
    
    return df.query(query)

def convert_timedelta(td: pd.Timedelta) -> str:
    '''This function converts a timedelta object to a string in hours and minutes
    
    Args:
        td (timedelta): timedelta object
        
    Returns:
        str: string in hours and minutes
    '''
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours} hrs {minutes} min"

st.subheader('Activity Metrics')

with st.container(border=True): # metrics
    a, metrics_col1, metrics_col2= st.columns([1, 3.5, 3])
    with metrics_col1:
        st.metric('Activities', df_query_builder(year_selection)['upload_id'].nunique())
    with metrics_col2:
        st.metric('Distance', f"{round(df_query_builder(year_selection)['distance_activity'].sum(), 2):,} mi")
        
    a, metrics_col3, metrics_col4 = st.columns([1, 3.5, 3])
    with metrics_col3:
        st.metric('Elevation', f"{int(round(df_query_builder(year_selection)['total_elevation_gain'].sum(), 0)):,} ft")
    with metrics_col4:
        st.metric('Time', convert_timedelta(df_query_builder(year_selection)['moving_time'].sum()))

with st.container(border=True):
    st.subheader('Total Activities')
    st.caption('All Activities By Month')
    temp_df = df_query_builder(year_selection).sort_values(by='start_date_local').groupby('month_year', sort=False).size().reset_index(name='Activities').rename(columns={'month_year': 'Month'})
    st.line_chart(temp_df, x='Month', y='Activities', use_container_width=True)
    st.caption('Activities By Type')
    temp_df2 = df_query_builder(year_selection).sort_values(by='start_date_local').groupby(['month_year', 'type'], sort=False).size().reset_index(name='Activities').rename(columns={'month_year': 'Month'})
    st.line_chart(temp_df2, x='Month', y='Activities', color='type', use_container_width=True)

st.subheader('Total Distance')

with st.container():
    temp_df = df_query_builder(year_selection).sort_values(by='start_date_local').groupby('month_year', sort=False).agg({'distance_activity': 'sum'}).reset_index().rename(columns={'month_year': 'Month', 'distance_activity': 'Distance'})
    st.line_chart(temp_df, x='Month', y='Distance', color=None, use_container_width=True)