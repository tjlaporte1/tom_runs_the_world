import pandas as pd
import streamlit as st

import functions as fn


sidebar_logo = './images/tom_runs_the_world_sidebar.png'
title_logo = './images/tom_runs_the_world_title.png'
st.logo(sidebar_logo)   
st.image(title_logo)
st.subheader('Strava Data Analysis')

# load data
if 'strava_data' not in st.session_state:
    st.session_state.strava_data = fn.get_strava_data()

df = fn.load_data()

# max date
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
# last_refresh = pd.read_csv('data/refresh_datetime.csv').iloc[0, 0]
today = pd.to_datetime(max_date)
rolling_12_months = today - pd.DateOffset(months=12)

##### STREAMLIT DASHBOARD #####
# page header
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

# metrics header
st.header('Activity Metrics')

# metrics
with st.container(border=True):
    
    a, metrics_col1, metrics_col2= st.columns([1, 3.5, 3])
    with metrics_col1:
        st.metric('Activities', fn.df_query_builder(df, year_selection, locals())['upload_id'].nunique())
    with metrics_col2:
        st.metric('Distance', f"{round(fn.df_query_builder(df, year_selection, locals())['distance_activity'].sum(), 2):,} mi")
        
    a, metrics_col3, metrics_col4 = st.columns([1, 3.5, 3])
    with metrics_col3:
        st.metric('Elevation', f"{int(round(fn.df_query_builder(df, year_selection, locals())['total_elevation_gain'].sum(), 0)):,} ft")
    with metrics_col4:
        st.metric('Time', fn.convert_timedelta(fn.df_query_builder(df, year_selection, locals())['moving_time'].sum()))

# tabs
tab_act, tab_dist, tab_ele, tab_time = st.tabs(['Activities', 'Distance', 'Elevation', 'Time'])

# activities tab
with tab_act:
    
    with st.container():
        
        st.subheader('Total Activities By Month')
        temp_df = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby('month_year', sort=False).size().reset_index(name='Activities').rename(columns={'month_year': 'Month'})
        st.line_chart(temp_df, x='Month', y='Activities', y_label='# of Activities')
        
        st.subheader('Activities By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby(['month_year', 'type'], sort=False).size().reset_index(name='Activities').rename(columns={'month_year': 'Month', 'type': 'Activity Type'})
        st.line_chart(temp_df, x='Month', y='Activities', y_label='# of Activities', color='Activity Type')

# distance tab
with tab_dist:
    
    with st.container():
        
        st.subheader('Total Distance By Month')
        temp_df = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby('month_year', sort=False).agg(Distance=('distance_activity', 'sum')).reset_index().rename(columns={'month_year': 'Month'})
        temp_df['Distance'] = temp_df['Distance'].round(2)
        st.line_chart(temp_df, x='Month', y='Distance', y_label='Distance (mi)')
        
        st.subheader('Total Distance By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby(['month_year', 'type'], sort=False).agg(Distance=('distance_activity', 'sum')).reset_index().rename(columns={'month_year': 'Month', 'type': 'Activity Type'})
        temp_df['Distance'] = temp_df['Distance'].round(2)
        st.line_chart(temp_df, x='Month', y='Distance', y_label='Distance (mi)', color='Activity Type')
 
# elevation tab
with tab_ele:
    
    with st.container():
        
        st.subheader('Total Elevation By Month')
        temp_df = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby('month_year', sort=False).agg(Elevation=('total_elevation_gain', 'sum')).reset_index().rename(columns={'month_year': 'Month'})
        temp_df['Elevation'] = temp_df['Elevation'].round(2).astype(int)
        st.line_chart(temp_df, x='Month', y='Elevation', y_label='Elevation (ft)')
        
        st.subheader('Total Elevation By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby(['month_year', 'type'], sort=False).agg(Elevation=('total_elevation_gain', 'sum')).reset_index().rename(columns={'month_year': 'Month', 'type': 'Activity Type'})
        temp_df['Elevation'] = temp_df['Elevation'].round(2).astype(int)
        st.line_chart(temp_df, x='Month', y='Elevation', y_label='Elevation (ft)', color='Activity Type')
        
# time tab       
with tab_time:
    
    with st.container():
        
        st.subheader('Total Time By Month')
        temp_df = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby('month_year', sort=False).agg(Time=('moving_time', 'sum')).reset_index().rename(columns={'month_year': 'Month'})
        temp_df['Time'] = (temp_df['Time'].dt.total_seconds() / 3600).round(2)
        st.line_chart(temp_df, x='Month', y='Time', y_label='Time (hrs)')
        
        st.subheader('Total Time By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby(['month_year', 'type'], sort=False).agg(Time=('moving_time', 'sum')).reset_index().rename(columns={'month_year': 'Month', 'type': 'Activity Type'})
        temp_df['Time'] = (temp_df['Time'].dt.total_seconds() / 3600).round(2)
        st.line_chart(temp_df, x='Month', y='Time', y_label='Time (hrs)', color='Activity Type')