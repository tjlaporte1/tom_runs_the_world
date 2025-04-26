import pandas as pd
import streamlit as st
import plotly.express as px

import functions as fn

df = fn.load_data()

sidebar_logo = './images/tom_runs_the_world_sidebar.png'
title_logo = './images/tom_runs_the_world_title.png'
st.logo(sidebar_logo)

refresh_date = df['refresh_date'].max()
max_date = pd.to_datetime(df['start_date_local']).dt.strftime('%Y-%m-%d %I:%M %p').max()

# distict activity type list
highlighted_activities = ['Run', 'Hike', 'Walk', 'Ride']
act_type_filter = df['type'].value_counts().index.tolist()
act_type_filter = list(dict.fromkeys(act_type_filter))

# distinct year list
year_filter = sorted(df['year'].unique().tolist(), reverse=True)
year_filter.insert(0, 'All')
year_filter.insert(1, 'Rolling 12 Months')

# distinct gear type list
gear_brand_list = df['brand_name'].value_counts().index.tolist()

# rolling 12 mo variable
today = pd.to_datetime(max_date)
rolling_12_months = today - pd.DateOffset(months=12)

# header
with st.container():
    st.image(title_logo)
    st.subheader('Strava Data Analysis')
    st.page_link('Overview.py', label='Refresh Data', help='Refresh data on Overview tab')
    st.caption('Last Refreshed: ' + str(refresh_date))
    st.caption('Last Activity Date: ' + max_date)
    st.divider()

# filters in sidebar
with st.sidebar:
    
    st.header('Filters')
    
    # initialize year selection
    st.session_state.year_selection = st.session_state.get('year_selection', fn.default_year_selection())
    year_selection = st.selectbox('Years', year_filter, key='year_selection')
    
    # initialize activity type selection
    st.session_state.act_type_selection = st.session_state.get('act_type_selection', fn.default_activity_selection(highlighted_activities))
    act_type_selection = st.multiselect('Activity Type', act_type_filter, placeholder='Select Activity Type', key='act_type_selection')
    
    # initialize gear brand selection
    st.session_state.gear_brand_selection = st.session_state.get('gear_brand_selection', fn.default_gear_brand_selection(gear_brand_list))
    gear_brand_selection = st.multiselect('Gear Brand', gear_brand_list, placeholder='Select Gear Brand', key='gear_brand_selection')
    
st.header('Activity Data')

# created gear dataframe
selected_columns = [
    'start_date_local',
    'start_time_local_12h',
    'type',
    'name_activity',
    'brand_name',
    'name_gear',
    'distance_activity',
    'total_elevation_gain',
    'elev_high',
    'elev_low',
    'moving_time',
    'average_speed',
    'max_speed',
    'average_heartrate',
    'max_heartrate',
    'suffer_score',
    'temp',
    'rhum',
    'start_time_local_24h_hour',
    'weekday'
]

temp_df = df[selected_columns].copy()

# format date and time
temp_df['moving_time'] = (temp_df['moving_time'].dt.total_seconds() / 3600).round(2)
temp_df['start_date_local'] = pd.to_datetime(temp_df['start_date_local']).dt.strftime('%Y-%m-%d')

# rename coulns and add helpers
column_config = {
    
    'start_date_local': st.column_config.DateColumn('Date'),
    'start_time_local_12h': st.column_config.TextColumn('Start Time'),
    'type': st.column_config.TextColumn('Activity Type'),
    'name_activity': st.column_config.TextColumn('Activity Name'),
    'brand_name': st.column_config.TextColumn('Brand Name'),
    'name_gear': st.column_config.TextColumn('Gear'),
    'distance_activity': st.column_config.NumberColumn('Distance (mi)'),
    'total_elevation_gain': st.column_config.NumberColumn('Total Elevation (ft)'),
    'elev_high': st.column_config.NumberColumn('Max Elevation (ft)'),
    'elev_low': st.column_config.NumberColumn('Min Elevation (ft)'),
    'moving_time': st.column_config.NumberColumn('Moving Time (hrs)'),
    'average_speed': st.column_config.NumberColumn('Avg Speed (mph)'),
    'max_speed': st.column_config.NumberColumn('Max Speed (mph)'),
    'average_heartrate': st.column_config.NumberColumn('Avg Heart Rate'),
    'max_heartrate': st.column_config.NumberColumn('Max Heart Rate'),
    'suffer_score': st.column_config.NumberColumn('Relative Effort', help='Metric that quantifies the cardiovascular work done during an activity'),
    'temp': st.column_config.NumberColumn('Temperature (°F)'),
    'rhum': st.column_config.NumberColumn('Relative Humidity (%)', format="%.0f%%"),
    'start_time_local_24h_hour': st.column_config.NumberColumn('Start Hour (24h)'),
    'weekday': st.column_config.TextColumn('Weekday')
    
}

st.dataframe(temp_df, column_config=column_config, hide_index=True)