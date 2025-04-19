import pandas as pd
import streamlit as st
import plotly.express as px

import functions as fn

df = fn.load_data()

sidebar_logo = './images/tom_runs_the_world_sidebar.png'
title_logo = './images/tom_runs_the_world_title.png'
st.logo(sidebar_logo)

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
    
st.header('Under Construction')
#TODO analysis on # of activities on the day of the week, by month. Distance by day of the week, by month, time of day, etc.