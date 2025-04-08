import pandas as pd
import requests
import urllib3
import streamlit as st

#import login as login

##### STRAVA API DATA EXTRACTION ####
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

auth_url = 'https://www.strava.com/oauth/token'
activities_url = 'https://www.strava.com/api/v3/athlete/activities'
gear_url = 'https://www.strava.com/api/v3/gear/{id}'

payload = {
    'client_id': f'{st.secrets['client_id']}',
    'client_secret': f'{st.secrets['client_secret']}',
    'refresh_token': f'{st.secrets['refresh_token']}',
    'grant_type': 'refresh_token',
    'f': 'json'
}

res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']

header = {'Authorization': 'Bearer ' + access_token}

def get_strava_data() -> pd.DataFrame:
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

def refresh_data_button():
    
    '''This function is used to refresh the data via the button.'''
        
    if st.session_state.refresh_counter == 0:
        return
    
    elif st.session_state.refresh_counter == 1:
        with st.spinner('Calling Strava API...', show_time=True):
            # get strava data
            local_df = get_strava_data()
            st.session_state.strava_data = local_df
            # archive the data
            local_df.to_csv('data/strava_data.csv', index=False)
            st.success('Data updated successfully!')
            # save the refresh data and time
            refresh_datetime = pd.Timestamp.now()
            refresh_datetime = refresh_datetime.strftime('%Y-%m-%d %I:%M %p')
            pd.DataFrame({'refresh_datetime': [refresh_datetime]}).to_csv('data/refresh_datetime.csv', index=False)
            
            st.session_state.refresh_counter += 1
        
    elif st.session_state.refresh_counter > 1 and st.session_state.refresh_counter < 5:
        st.info('Data is already refreshed')
        
    else:
        st.warning("No really, it's refreshed. I promise!")

@st.cache_data()
def load_data() -> pd.DataFrame:
    
    '''This function loads the dataframe from the session state. It then corrects the data types.
    
    Returns: DataFrame: Strave dataframe'''
    
    df = pd.DataFrame(st.session_state.strava_data)
    
    # convert moving_time and elapsed time to H% M% S% format
    df['moving_time'] = pd.to_timedelta(df['moving_time'])
    df['elapsed_time'] = pd.to_timedelta(df['elapsed_time'])
    
    # convert start_date and start_date_local to datetime
    df['start_date'] = pd.to_datetime(pd.to_datetime(df['start_date']).dt.strftime('%Y-%m-%d %H:%M:%S'))
    df['start_date_local'] = pd.to_datetime(pd.to_datetime(df['start_date_local']).dt.strftime('%Y-%m-%d %H:%M:%S'))
    
    # add start time for analysis and in am/pm format
    df['start_time_local_24h'] = pd.to_datetime(df['start_date_local']).dt.time
    df['start_time_local_12h'] = pd.to_datetime(df['start_date_local']).dt.strftime("%I:%M %p")

    # add month year
    df['month_year'] = pd.to_datetime(pd.to_datetime(df['start_date_local']).dt.strftime('%Y-%m'))
    
    return df

# load data
if 'strava_data' not in st.session_state:
    st.session_state.strava_data = pd.read_csv('data/strava_data.csv')
    
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0

df = load_data()

# max date
max_date = pd.to_datetime(df['start_date_local']).dt.strftime('%Y-%m-%d %I:%M %p').max()

# distict activity type list
highlighted_activities = ['Run', 'Hike', 'Walk', 'Ride']
act_type_filter = df['type'].value_counts().index.tolist()
act_type_filter = list(dict.fromkeys(act_type_filter))
    
def default_activity_selection():
    
    '''This function sets the default activity type selection for the filter and captures the selection to use across the app.'''
    
    if 'act_type_selection' not in st.session_state:
        act_filter = highlighted_activities
    else:
        act_filter = st.session_state.act_type_selection
    
    return act_filter

# distinct year list
year_filter = sorted(df['year'].unique().tolist(), reverse=True)
year_filter.insert(0, 'All')
year_filter.insert(1, 'Rolling 12 Months')

def default_year_selection():
    
    '''This function sets the default year selection for the filter and captures the selection to use across the app.'''
    
    if 'year_selection' not in st.session_state:
        year_filter_1 = 'Rolling 12 Months'
    else:
        year_filter_1 = st.session_state.year_selection
    
    return year_filter_1

# distinct gear type list
gear_brand_list = df['brand_name'].value_counts().index.tolist()

def default_gear_brand_selection():
    
    '''This function sets the default gear brand selection for the filter and captures the selection to use across the app.'''
    
    if 'gear_brand_selection' not in st.session_state:
        gear_filter = gear_brand_list
    else:
        gear_filter = st.session_state.gear_brand_selection
    
    return gear_filter

# rolling 12 mo variable
last_refresh = pd.read_csv('data/refresh_datetime.csv').iloc[0, 0]
today = pd.to_datetime(max_date)
rolling_12_months = today - pd.DateOffset(months=12)

##### STREAMLIT DASHBOARD #####
# page header
with st.container():
    st.title('Tom Runs The World')
    st.subheader('Strava Data Analysis')
    st.caption('Last Activity Date: ' + max_date)
    st.caption('Last Data Refresh: ' + last_refresh)
    if st.button('Refresh Data'):
        st.session_state.refresh_counter += 1
        refresh_data_button()
        last_refresh = pd.read_csv('data/refresh_datetime.csv').iloc[0, 0]
    st.divider()
    
# filters in sidebar
with st.sidebar:
    
    st.header('Filters')
    
    # initialize year selection
    st.session_state.year_selection = st.session_state.get('year_selection', default_year_selection())
    year_selection = st.selectbox('Years', year_filter, key='year_selection')
    
    # initialize activity type selection
    st.session_state.act_type_selection = st.session_state.get('act_type_selection', default_activity_selection())
    act_type_selection = st.multiselect('Activity Type', act_type_filter, placeholder='Select Activity Type', key='act_type_selection')
    
    # initialize gear brand selection
    st.session_state.gear_brand_selection = st.session_state.get('gear_brand_selection', default_gear_brand_selection())
    gear_brand_selection = st.multiselect('Gear Brand', gear_brand_list, placeholder='Select Gear Brand', key='gear_brand_selection')

def df_query_builder(year_selection) -> pd.DataFrame:
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
        
    # gear brand filter
    conditions.append("brand_name in @gear_brand_selection")

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

# metrics header
st.header('Activity Metrics')

# metrics
with st.container(border=True):
    
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

# tabs
tab_act, tab_dist, tab_ele, tab_time = st.tabs(['Activities', 'Distance', 'Elevation', 'Time'])

# activities tab
with tab_act:
    
    with st.container():
        
        st.subheader('Total Activities')
        
        st.caption('Activities By Month')
        temp_df = df_query_builder(year_selection).sort_values(by='start_date_local').groupby('month_year', sort=False).size().reset_index(name='Activities').rename(columns={'month_year': 'Month'})
        st.line_chart(temp_df, x='Month', y='Activities', y_label='# of Activities', use_container_width=True)
        
        st.caption('Activities By Activity Type')
        temp_df2 = df_query_builder(year_selection).sort_values(by='start_date_local').groupby(['month_year', 'type'], sort=False).size().reset_index(name='Activities').rename(columns={'month_year': 'Month', 'type': 'Activity Type'})
        st.line_chart(temp_df2, x='Month', y='Activities', y_label='# of Activities', color='Activity Type', use_container_width=True)

# distance tab
with tab_dist:
    
    with st.container():
        
        st.subheader('Total Distance')
        
        st.caption('Distance By Month')
        temp_df = df_query_builder(year_selection).sort_values(by='start_date_local').groupby('month_year', sort=False).agg({'distance_activity': 'sum'}).reset_index().rename(columns={'month_year': 'Month', 'distance_activity': 'Distance'})
        temp_df['Distance'] = temp_df['Distance'].round(2)
        st.line_chart(temp_df, x='Month', y='Distance', y_label='Distance (mi)', color=None, use_container_width=True)
        
        st.caption('Distance By Activity Type')
        temp_df2 = df_query_builder(year_selection).sort_values(by='start_date_local').groupby(['month_year', 'type'], sort=False).agg({'distance_activity': 'sum'}).reset_index().rename(columns={'month_year': 'Month', 'distance_activity': 'Distance', 'type': 'Activity Type'})
        temp_df2['Distance'] = temp_df2['Distance'].round(2)
        st.line_chart(temp_df2, x='Month', y='Distance', y_label='Distance (mi)', color='Activity Type', use_container_width=True)
 
# elevation tab
with tab_ele:
    
    with st.container():
        
        st.subheader('Total Elevation')
        
        st.caption('Elevation By Month')
        temp_df = df_query_builder(year_selection).sort_values(by='start_date_local').groupby('month_year', sort=False).agg({'total_elevation_gain': 'sum'}).reset_index().rename(columns={'month_year': 'Month', 'total_elevation_gain': 'Elevation'})
        temp_df['Elevation'] = temp_df['Elevation'].round(2).astype(int)
        st.line_chart(temp_df, x='Month', y='Elevation', y_label='Elevation (ft)', color=None, use_container_width=True)
        
        st.caption('Elevation By Activity Type')
        temp_df2 = df_query_builder(year_selection).sort_values(by='start_date_local').groupby(['month_year', 'type'], sort=False).agg({'total_elevation_gain': 'sum'}).reset_index().rename(columns={'month_year': 'Month', 'total_elevation_gain': 'Elevation', 'type': 'Activity Type'})
        temp_df2['Elevation'] = temp_df2['Elevation'].round(2).astype(int)
        st.line_chart(temp_df2, x='Month', y='Elevation', y_label='Elevation (ft)', color='Activity Type', use_container_width=True)
        
# time tab       
with tab_time:
    
    with st.container():
        
        st.subheader('Total Time')
        
        st.caption('Time By Month')
        temp_df = df_query_builder(year_selection).sort_values(by='start_date_local').groupby('month_year', sort=False).agg({'moving_time': 'sum'}).reset_index().rename(columns={'month_year': 'Month', 'moving_time': 'Time'})
        temp_df['Time'] = (temp_df['Time'].dt.total_seconds() / 3600).round(2)
        st.line_chart(temp_df, x='Month', y='Time', y_label='Time (hrs)', color=None, use_container_width=True)
        
        st.caption('Time By Activity Type')
        temp_df2 = df_query_builder(year_selection).sort_values(by='start_date_local').groupby(['month_year', 'type'], sort=False).agg({'moving_time': 'sum'}).reset_index().rename(columns={'month_year': 'Month', 'moving_time': 'Time', 'type': 'Activity Type'})
        temp_df2['Time'] = (temp_df2['Time'].dt.total_seconds() / 3600).round(2)
        st.line_chart(temp_df2, x='Month', y='Time', y_label='Time (hrs)', color='Activity Type', use_container_width=True)