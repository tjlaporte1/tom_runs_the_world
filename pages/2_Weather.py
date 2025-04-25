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
    
st.header('Weather')
    
tab_act, tab_dist, tab_ele, tab_time, tab_speed, tab_heart, tab_effort = st.tabs(['Activities', 'Distance', 'Elevation', 'Time', 'Speed', 'Heart Rate', 'Relative Effort'])

with tab_act:
    
    with st.container():
        
        st.subheader('Activities By Relative Humidity vs. Temperature')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'temp': 'Temperature (°F)', 'rhum': 'Relative Humidity (%)', 'type': 'Activity Type'})
        st.scatter_chart(temp_df, x='Temperature (°F)', y='Relative Humidity (%)', color='Activity Type')
        
with tab_dist:
    
    with st.container():
        
        st.subheader('Distance By Temperature')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'temp': 'Temperature (°F)', 'rhum': 'Relative Humidity (%)', 'type': 'Activity Type', 'distance_activity': 'Distance (mi)'})
        st.scatter_chart(temp_df, x='Temperature (°F)', y='Distance (mi)', color='Activity Type')
        
        st.subheader('Distance By Relative Humidity')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'temp': 'Temperature (°F)', 'rhum': 'Relative Humidity (%)', 'type': 'Activity Type', 'distance_activity': 'Distance (mi)'})
        st.scatter_chart(temp_df, x='Relative Humidity (%)', y='Distance (mi)', color='Activity Type')
        
with tab_ele:
    
    with st.container():
        
        st.subheader('Elevation By Temperature')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'temp': 'Temperature (°F)', 'rhum': 'Relative Humidity (%)', 'type': 'Activity Type', 'total_elevation_gain': 'Elevation (ft)'})
        st.scatter_chart(temp_df, x='Temperature (°F)', y='Elevation (ft)', color='Activity Type')
        
        st.subheader('Elevation By Relative Humidity')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'temp': 'Temperature (°F)', 'rhum': 'Relative Humidity (%)', 'type': 'Activity Type', 'total_elevation_gain': 'Elevation (ft)'})
        st.scatter_chart(temp_df, x='Relative Humidity (%)', y='Elevation (ft)', color='Activity Type')
        
with tab_time:
    
    with st.container():
        
        st.subheader('Time By Temperature')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'temp': 'Temperature (°F)', 'rhum': 'Relative Humidity (%)', 'type': 'Activity Type', 'moving_time': 'Time (hrs)'})
        temp_df['Time (hrs)'] = (temp_df['Time (hrs)'].dt.total_seconds() / 3600).round(2)
        st.scatter_chart(temp_df, x='Temperature (°F)', y='Time (hrs)', color='Activity Type')
        
        st.subheader('Time By Relative Humidity')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'temp': 'Temperature (°F)', 'rhum': 'Relative Humidity (%)', 'type': 'Activity Type', 'moving_time': 'Time (hrs)'})
        temp_df['Time (hrs)'] = (temp_df['Time (hrs)'].dt.total_seconds() / 3600).round(2)
        st.scatter_chart(temp_df, x='Relative Humidity (%)', y='Time (hrs)', color='Activity Type')
        
with tab_speed:
    
    with st.container():
        
        st.subheader('Avg Speed By Temperature')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'temp': 'Temperature (°F)', 'rhum': 'Relative Humidity (%)', 'type': 'Activity Type', 'average_speed': 'Avg speed (mph)'})
        st.scatter_chart(temp_df, x='Temperature (°F)', y='Avg speed (mph)', color='Activity Type')
        
        st.subheader('Avg Speed By Relative Humidity')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'temp': 'Temperature (°F)', 'rhum': 'Relative Humidity (%)', 'type': 'Activity Type', 'average_speed': 'Avg speed (mph)'})
        st.scatter_chart(temp_df, x='Relative Humidity (%)', y='Avg speed (mph)', color='Activity Type')
        
with tab_heart:
    
    with st.container():
        
        st.subheader('Avg Heart Rate By Temperature')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'temp': 'Temperature (°F)', 'rhum': 'Relative Humidity (%)', 'type': 'Activity Type', 'average_heartrate': 'Avg Heart Rate'})
        st.scatter_chart(temp_df, x='Temperature (°F)', y='Avg Heart Rate', color='Activity Type')
        
        st.subheader('Avg Heart Rate By Relative Humidity')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'temp': 'Temperature (°F)', 'rhum': 'Relative Humidity (%)', 'type': 'Activity Type', 'average_heartrate': 'Avg Heart Rate'})
        st.scatter_chart(temp_df, x='Relative Humidity (%)', y='Avg Heart Rate', color='Activity Type')
        
with tab_effort:
    
    with st.container():
        
        st.subheader('Relative Effort By Temperature')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'temp': 'Temperature (°F)', 'rhum': 'Relative Humidity (%)', 'type': 'Activity Type', 'suffer_score': 'Relative Effort'})
        st.scatter_chart(temp_df, x='Temperature (°F)', y='Relative Effort', color='Activity Type')
        
        st.subheader('Relative Effort By Relative Humidity')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'temp': 'Temperature (°F)', 'rhum': 'Relative Humidity (%)', 'type': 'Activity Type', 'suffer_score': 'Relative Effort'})
        st.scatter_chart(temp_df, x='Relative Humidity (%)', y='Relative Effort', color='Activity Type')