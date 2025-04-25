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
    
st.header('Timing')

tab_month, tab_day, tab_time = st.tabs(['Month', 'Day', 'Time of Day'])

with tab_month:
    
    with st.container():
        
        st.subheader('Total Activities By Month By Activity Type')
        st.caption('Best results when using all years available in filter')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['monthly_date', 'type']).agg(Activities=('upload_id', 'count')).reset_index().rename(columns={'monthly_date': 'Month', 'type': 'Activity Type'})
        st.bar_chart(temp_df, x='Month', y='Activities', color='Activity Type')
        
        st.subheader('Total Distance By Month By Activity Type')
        st.caption('Best results when using all years available in filter')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['monthly_date', 'type']).agg(Distance=('distance_activity', 'sum')).reset_index().rename(columns={'monthly_date': 'Month', 'type': 'Activity Type'})
        st.bar_chart(temp_df, x='Month', y='Distance', y_label='Distance (mi)', color='Activity Type')
        
        st.subheader('Total Elevation By Month By Activity Type')
        st.caption('Best results when using all years available in filter')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['monthly_date', 'type']).agg(Elevation=('total_elevation_gain', 'sum')).reset_index().rename(columns={'monthly_date': 'Month', 'type': 'Activity Type'})
        st.bar_chart(temp_df, x='Month', y='Elevation', y_label='Elevation (ft)', color='Activity Type')
        
        st.subheader('Total Time By Month By Activity Type')
        st.caption('Best results when using all years available in filter')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['monthly_date', 'type']).agg(Time=('moving_time', 'sum')).reset_index().rename(columns={'monthly_date': 'Month', 'type': 'Activity Type'})
        temp_df['Time'] = (temp_df['Time'].dt.total_seconds() / 3600).round(2)
        st.bar_chart(temp_df, x='Month', y='Time', y_label='Time (hrs)', color='Activity Type')
        
with tab_day:
    
    with st.container():
        
        st.subheader('Total Activities By Weekday By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['weekday_num', 'weekday', 'type']).agg(Activities=('upload_id', 'count')).reset_index().rename(columns={'weekday': 'Weekday', 'type': 'Activity Type'})
        temp_df['Weekday'] = (temp_df['weekday_num'] + 1).astype(str) + '-' + temp_df['Weekday']
        st.bar_chart(temp_df, x='Weekday', y='Activities', color='Activity Type')
        
        st.subheader('Total Distance By Weekday By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['weekday_num', 'weekday', 'type']).agg(Distance=('distance_activity', 'sum')).reset_index().rename(columns={'weekday': 'Weekday', 'type': 'Activity Type'})
        temp_df['Weekday'] = (temp_df['weekday_num'] + 1).astype(str) + '-' + temp_df['Weekday']
        st.bar_chart(temp_df, x='Weekday', y='Distance', y_label='Distance (mi)', color='Activity Type')
        
        st.subheader('Total Elevation By Weekday By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['weekday_num', 'weekday', 'type']).agg(Elevation=('total_elevation_gain', 'sum')).reset_index().rename(columns={'weekday': 'Weekday', 'type': 'Activity Type'})
        temp_df['Weekday'] = (temp_df['weekday_num'] + 1).astype(str) + '-' + temp_df['Weekday']
        st.bar_chart(temp_df, x='Weekday', y='Elevation', y_label='Elevation (ft)', color='Activity Type')
        
        st.subheader('Total Time By Weekday By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['weekday_num', 'weekday', 'type']).agg(Time=('moving_time', 'sum')).reset_index().rename(columns={'weekday': 'Weekday', 'type': 'Activity Type'})
        temp_df['Time'] = (temp_df['Time'].dt.total_seconds() / 3600).round(2)
        temp_df['Weekday'] = (temp_df['weekday_num'] + 1).astype(str) + '-' + temp_df['Weekday']
        st.bar_chart(temp_df, x='Weekday', y='Time', y_label='Time (hrs)', color='Activity Type')
        
with tab_time:
    
    with st.container():
        
        st.subheader('Total Activities By Hour By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['start_time_local_24h_hour', 'type']).agg(Activities=('upload_id', 'count')).reset_index().rename(columns={'start_time_local_24h_hour': 'Hour', 'type': 'Activity Type'})
        st.bar_chart(temp_df, x='Hour', y='Activities', color='Activity Type')
        
        st.subheader('Total Distance By Hour By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['start_time_local_24h_hour', 'type']).agg(Distance=('distance_activity', 'sum')).reset_index().rename(columns={'start_time_local_24h_hour': 'Hour', 'type': 'Activity Type'})
        st.bar_chart(temp_df, x='Hour', y='Distance', y_label='Distance (mi)', color='Activity Type')
        
        st.subheader('Total Elevation By Hour By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['start_time_local_24h_hour', 'type']).agg(Elevation=('total_elevation_gain', 'sum')).reset_index().rename(columns={'start_time_local_24h_hour': 'Hour', 'type': 'Activity Type'})
        st.bar_chart(temp_df, x='Hour', y='Elevation', y_label='Elevation (ft)', color='Activity Type')
        
        st.subheader('Total Time By Hour By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['start_time_local_24h_hour', 'type']).agg(Time=('moving_time', 'sum')).reset_index().rename(columns={'start_time_local_24h_hour': 'Hour', 'type': 'Activity Type'})
        temp_df['Time'] = (temp_df['Time'].dt.total_seconds() / 3600).round(2)
        st.bar_chart(temp_df, x='Hour', y='Time', y_label='Time (hrs)', color='Activity Type')