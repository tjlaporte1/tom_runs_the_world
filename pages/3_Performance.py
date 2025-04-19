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
    
st.header('Performance')

# tabs
tab_speed, tab_heart, tab_effort = st.tabs(['Speed', 'Heart Rate', 'Relative Effort'])
        
with tab_speed:
    
    with st.container(border=True):
        
        st.header('Avg Speed')
        
        st.divider()
        
        st.subheader('Avg Speed By Month By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby(['month_year', 'type']).agg(Avg_Speed=('average_speed', 'mean')).reset_index().rename(columns={'month_year': 'Month', 'type': 'Activity Type', 'Avg_Speed': 'Avg Speed (mph)'})
        temp_df['Avg Speed (mph)'] = temp_df['Avg Speed (mph)'].round(2)
        st.line_chart(temp_df, x='Month', y='Avg Speed (mph)', color='Activity Type')
        
        st.subheader('Avg Speed By Month (Boxplot)')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'name_gear': 'Gear', 'brand_name': 'Gear Brand'})
        fig = px.box(temp_df, x='month_year', y='average_speed', labels={'month_year': 'Month', 'average_speed': 'Average Speed (mph)'}, points='all')
        st.plotly_chart(fig)
        
    with st.container(border=True):
        
        st.header('Max Speed')
        
        st.divider()
        
        st.subheader('Max Speed By Month By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby(['month_year', 'type']).agg(Max_Speed=('max_speed', 'mean')).reset_index().rename(columns={'month_year': 'Month', 'type': 'Activity Type', 'Max_Speed': 'Max Speed (mph)'})
        temp_df['Max Speed (mph)'] = temp_df['Max Speed (mph)'].round(2)
        st.line_chart(temp_df, x='Month', y='Max Speed (mph)', color='Activity Type')
        
        st.subheader('Max Speed By Month (Boxplot)')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'name_gear': 'Gear', 'brand_name': 'Gear Brand'})
        fig = px.box(temp_df, x='month_year', y='max_speed', labels={'month_year': 'Month', 'max_speed': 'Max Speed (mph)'}, points='all')
        st.plotly_chart(fig)
        
with tab_heart:
    
    with st.container(border=True):
        
        st.header('Avg Heart Rate')
        
        st.divider()
        
        st.subheader('Avg Heart Rate By Month By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby(['month_year', 'type']).agg(Avg_Heartrate=('average_heartrate', 'mean')).reset_index().rename(columns={'month_year': 'Month', 'type': 'Activity Type', 'Avg_Heartrate': 'Avg Heart Rate'})
        temp_df['Avg Heart Rate'] = temp_df['Avg Heart Rate'].round(2)
        st.line_chart(temp_df, x='Month', y='Avg Heart Rate', color='Activity Type')
        
        st.subheader('Avg Heart Rate By Month (Boxplot)')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'name_gear': 'Gear', 'brand_name': 'Gear Brand'})
        fig = px.box(temp_df, x='month_year', y='average_heartrate', labels={'month_year': 'Month', 'average_heartrate': 'Avg Heart Rate'}, points='all')
        st.plotly_chart(fig)
        
    with st.container(border=True):

        st.header('Max Heart Rate')
        
        st.divider()
        
        st.subheader('Max Heart Rate By Month By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby(['month_year', 'type']).agg(Max_Heartrate=('max_heartrate', 'mean')).reset_index().rename(columns={'month_year': 'Month', 'type': 'Activity Type', 'Max_Heartrate': 'Max Heart Rate'})
        temp_df['Max Heart Rate'] = temp_df['Max Heart Rate'].round(2)
        st.line_chart(temp_df, x='Month', y='Max Heart Rate', color='Activity Type')
        
        st.subheader('Max Heart Rate By Month (Boxplot)')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'name_gear': 'Gear', 'brand_name': 'Gear Brand'})
        fig = px.box(temp_df, x='month_year', y='max_heartrate', labels={'month_year': 'Month', 'max_heartrate': 'Max Heart Rate'}, points='all')
        st.plotly_chart(fig)
        
with tab_effort:
    
    with st.container(border=True):
        
        st.header('Avg Relative Effort')
        
        st.divider()
        
        st.subheader('Avg Relative Effort By Month By Activity Type')
        temp_df = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby(['month_year', 'type']).agg(Avg_Relative_Effort=('suffer_score', 'mean')).reset_index().rename(columns={'month_year': 'Month', 'type': 'Activity Type', 'Avg_Relative_Effort': 'Avg Relative Effort'})
        temp_df['Avg Relative Effort'] = temp_df['Avg Relative Effort'].round(2)
        st.line_chart(temp_df, x='Month', y='Avg Relative Effort', color='Activity Type')
        
        st.subheader('Avg Relative Effort By Month (Boxplot)')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'name_gear': 'Gear', 'brand_name': 'Gear Brand'})
        fig = px.box(temp_df, x='month_year', y='suffer_score', labels={'month_year': 'Month', 'suffer_score': 'Avg Relative Effort'}, points='all')
        st.plotly_chart(fig)