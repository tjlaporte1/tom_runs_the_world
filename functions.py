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

def get_strava_data() -> pd.DataFrame:
    '''This function builds the dataframe from Strava API data. It is used to then cache the dataframe for faster loading in the Streamlit app.
    
    Returns:
        pre_df (DataFrame): DataFrame of activities and gear data'''
    
    with st.status('Downloading Data...', expanded=True) as status:
        
        # Strava API only allows 200 results per page. This function loops through until all results are collected
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
            
            st.write('Fetching Activities...')
            
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
                    print('Stopping after 20 pages to avoid excessive API calls.')
                    
                    return None
                
            return pd.json_normalize(data)
              
        # get all activities data
        activities = get_activities_data()
        
        if activities == None:
            return pd.read_pickle('./data/full_data_backup.pkl')
        
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
        
        def add_weather_data(df: pd.DataFrame, max_workers=30) -> pd.DataFrame:
            '''This function gets weather data from Meteostat and adds it onto the activities DataFrame
            
            Args:
                df (DataFrame): Activities data frame that uses latitude, longitude, and timestamps to get weather data
                max_worker (int): Number of threads to use in the multi-threading process
                
            Returns:
                df (DataFrame): Original df with weatehr data appended'''
                
            def get_weather(row):
                '''This function takes the latitude, longitude, and timestamp for each row and calls the Meteostat API for data
                
                Args:
                    row: The row in the DataFrame used in the parent function
                    
                Returns:
                    weather_data (dict): The temperature and relative humidity of the row's activity as a dictionary'''
                
                # get the location of the activity
                location = Point(row['start_latitude'], row['start_longitude'])
                # get the time of the activity
                timestamp = pd.to_datetime(row['start_date_local'])
                # only use the hour it started
                start = end = timestamp.replace(tzinfo=None, minute=0, second=0, microsecond=0)

                # call meteostat API
                try:
                    data = Hourly(location, start, end)
                    data = data.convert(units.imperial).fetch()
                    if not data.empty:
                        # only get the first row of data
                        weather = data[['temp', 'rhum']].iloc[0]
                        return {'temp': weather['temp'], 'rhum': weather['rhum']}
                    else:
                        return {'temp': None, 'rhum': None}
                except Exception as e:
                    print(f"Error fetching weather for {timestamp}: {e}")
                    return {'temp': None, 'rhum': None}
                
            # separate the latitude and longitude from the activity data
            df[['start_latitude', 'start_longitude']] = pd.DataFrame(df['start_latlng'].tolist(), index=df.index)

            # multi-threading so the function can call the API and iterate through rows faster
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                weather_data = list(executor.map(get_weather, [row for _, row in df.iterrows()]))

            # get the weatehr data and concat the two DataFrames
            weather_df = pd.DataFrame(weather_data)
            Hourly.clear_cache()
            return pd.concat([df.reset_index(drop=True), weather_df.reset_index(drop=True)], axis=1)
        
        st.write('Sprinkling in Weather Data...')
        
        activities_df = add_weather_data(activities_df)

        # get distinct gear id's
        gear_id_list = activities_df['gear_id'].unique()
        gear_id_list = gear_id_list[~pd.isnull(gear_id_list)]

        def get_gear_data(gear_list: list) -> pd.DataFrame:
            '''This function gets gear data from Strava API
            
            Args:
                gear_list (array): List of distinct gear ids
                
                Returns:
                    data (DataFrame): Normalized JSON data of gear'''
            # set the URL for the Strava API
            gear_url = 'https://www.strava.com/api/v3/gear/{id}'
            # create empty list to store gear data
            data = []
            # loop through gear_list and get gear data
            for gear_id in gear_list:
                get_gear = requests.get(gear_url.format(id=gear_id), headers=header).json()
                data.append(get_gear)
            return pd.json_normalize(data)

        st.write('Appending Gear Data...')
        
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
        pre_df['start_time_local_24h_hour'] = pd.to_datetime(pre_df['start_date_local']).dt.round('H').dt.hour
        pre_df['start_time_local_12h'] = pd.to_datetime(pre_df['start_date_local']).dt.strftime("%I:%M %p")

        # add day of week
        pre_df['weekday'] = pd.to_datetime(pre_df['start_date_local']).dt.day_name()
        pre_df['weekday_num'] = pd.to_datetime(pre_df['start_date_local']).dt.weekday

        # add month
        pre_df['month'] = pd.to_datetime(pre_df['start_date_local']).dt.month_name()
        pre_df['month_num'] = pd.to_datetime(pre_df['start_date_local']).dt.month
        pre_df['monthly_date'] = pd.to_datetime(pd.to_datetime(pre_df['start_date_local']).dt.strftime('%Y-%m')).apply(lambda x: x.replace(year=2025))

        # add month year
        pre_df['month_year'] = pd.to_datetime(pd.to_datetime(pre_df['start_date_local']).dt.strftime('%Y-%m'))
        
        # add month year name
        pre_df['month_year_name'] = pd.to_datetime(pre_df['start_date_local']).dt.strftime('%b %Y')

        # add year label
        pre_df['year'] = pd.to_datetime(pre_df['start_date_local']).dt.year
        
        pre_df.drop(columns=['start_latlng', 'end_latlng', 'start_latitude', 'start_longitude'], inplace=True)
    
        status.update(label='Data is Served!', state='complete', expanded=False)
        
        return pre_df

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

def default_activity_selection(highlighted_activities: list) -> list:
    
    '''This function sets the default activity type selection for the filter and captures the selection to use across the app.
    
    Args:
        highlighted_activities (list): List of highlighted activities
        
    Returns:
        act_filter (list): List of selected activities'''
    
    if 'act_type_selection' not in st.session_state:
        act_filter = highlighted_activities
    else:
        act_filter = st.session_state.act_type_selection
    
    return act_filter

def default_year_selection() -> str:
    
    '''This function sets the default year selection for the filter and captures the selection to use across the app.'''
    
    if 'year_selection' not in st.session_state:
        year_filter_1 = 'Rolling 12 Months'
    else:
        year_filter_1 = st.session_state.year_selection
    
    return year_filter_1

def default_gear_brand_selection(gear_brand_list: list) -> list:
    
    '''This function sets the default gear brand selection for the filter and captures the selection to use across the app.
    
    Args:
        gear_brand_list (list): List of gear brands
        
    Returns:
        gear_filter (list): List of selected gear brands'''
    
    if 'gear_brand_selection' not in st.session_state:
        gear_filter = gear_brand_list
    else:
        gear_filter = st.session_state.gear_brand_selection
    
    return gear_filter

def df_query_builder(df: pd.DataFrame, year_selection: str, local_vars: dict) -> pd.DataFrame:
    '''This function builds a query to filter the dataframe based on the selected activity type, year and gear brand.
    
    Args:
        df (DataFrame): DataFrame to filter
        year_selection (str): Selected year from filter
        local_vars (dict): Local variables to use in the query
        
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
    
    return df.query(query, local_dict=local_vars)

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