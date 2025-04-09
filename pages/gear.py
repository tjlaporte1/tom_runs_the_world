import pandas as pd
import streamlit as st

@st.cache_data()
def load_data() -> pd.DataFrame:
    
    '''This function loads the dataframe from the session state. It then corrects the data types.
    
    Returns: DataFrame: Strave dataframe'''
    
    df = pd.DataFrame(st.session_state.strava_data)
    
    # convert moving_time and elapsed time to H% M% S% format
    df['moving_time'] = pd.to_timedelta(df['moving_time'])
    df['elapsed_time'] = pd.to_timedelta(df['elapsed_time'])
    
    # convert start_date and start_date_local to datetime
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['start_date_local'] = pd.to_datetime(df['start_date_local'])
    
    # add start time for analysis and in am/pm format
    df['start_time_local_24h'] = pd.to_datetime(df['start_date_local']).dt.time
    df['start_time_local_12h'] = pd.to_datetime(df['start_date_local']).dt.strftime("%I:%M %p")
    
    # add month year
    df['month_year'] = pd.to_datetime(pd.to_datetime(df['start_date_local']).dt.strftime('%Y-%m'))
    
    return df

df = load_data()

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
# last_refresh = pd.read_csv('data/refresh_datetime.csv').iloc[0, 0]
today = pd.to_datetime(max_date)
rolling_12_months = today - pd.DateOffset(months=12)

# header
with st.container():
    st.title('Tom Runs The World')
    st.subheader('Strava Data Analysis')
    st.caption('Last Activity Date: ' + max_date)
    # st.caption('Last Data Refresh: ' + last_refresh)
    # st.page_link('Overview.py', label='Refresh Data on Overview Page', icon='🔄')
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
    
st.header('Gear Analysis')

# tabs
tab_act, tab_dist, tab_ele, tab_time = st.tabs(['Activities', 'Distance', 'Elevation', 'Time'])

with tab_act:
    
    with st.container():
        
        st.subheader('Total Activities')
        
        st.caption('Total Activities By Gear Brand')
        temp_df = df_query_builder(year_selection).groupby(['brand_name', 'name_gear']).agg({'upload_id': 'count'}).reset_index().rename(columns={'upload_id': 'Activities', 'brand_name': 'Gear Brand', 'name_gear': 'Gear'})
        st.bar_chart(temp_df, x='Gear Brand', y='Activities', y_label='# of Activities', color='Gear', use_container_width=True)
        
        st.caption('Total Activities By Gear')
        temp_df = df_query_builder(year_selection).groupby(['brand_name', 'name_gear']).agg({'upload_id': 'count'}).reset_index().rename(columns={'name_gear': 'Gear', 'upload_id': 'Activities', 'brand_name': 'Gear Brand'})
        st.bar_chart(temp_df, x='Gear', y='Activities', y_label='# of Activities', color='Gear', use_container_width=True)

        st.caption('Activities By Gear By Month')
        temp_df2 = df_query_builder(year_selection).sort_values(by='start_date_local').groupby(['month_year', 'name_gear'], sort=False).size().reset_index(name='Activities').rename(columns={'month_year': 'Month', 'name_gear': 'Gear'})
        st.line_chart(temp_df2, x='Month', y='Activities', y_label='# of Activities', color='Gear', use_container_width=True)
        
with tab_dist:
    
    with st.container():
        
        st.subheader('Total Distance')
        
        st.caption('Total Distance By Gear Brand')
        temp_df = df_query_builder(year_selection).groupby(['brand_name', 'name_gear']).agg({'distance_activity': 'sum'}).reset_index().rename(columns={'distance_activity': 'Distance', 'brand_name': 'Gear Brand', 'name_gear': 'Gear'})
        st.bar_chart(temp_df, x='Gear Brand', y='Distance', y_label='Distance (mi)', color='Gear', use_container_width=True)
        
        st.caption('Total Distance By Gear')
        temp_df = df_query_builder(year_selection).groupby(['brand_name', 'name_gear']).agg({'distance_activity': 'sum'}).reset_index().rename(columns={'name_gear': 'Gear', 'distance_activity': 'Distance', 'brand_name': 'Gear Brand'})
        st.bar_chart(temp_df, x='Gear', y='Distance', y_label='Distance (mi)', color='Gear', use_container_width=True)

        st.caption('Distance By Gear By Month')
        temp_df2 = df_query_builder(year_selection).sort_values(by='start_date_local').groupby(['month_year', 'name_gear'], sort=False).agg({'distance_activity': 'sum'}).reset_index().rename(columns={'month_year': 'Month', 'distance_activity': 'Distance', 'name_gear': 'Gear'})
        st.line_chart(temp_df2, x='Month', y='Distance', y_label='Distance (mi)', color='Gear', use_container_width=True)
