import pandas as pd
import streamlit as st

import functions as fn

df = fn.load_data()

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
    st.title('Tom Runs The World')
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
    
st.header('Gear Analysis')

# tabs
tab_act, tab_dist, tab_ele, tab_time = st.tabs(['Activities', 'Distance', 'Elevation', 'Time'])

with tab_act:
    
    with st.container():
        
        st.subheader('Total Activities')
        
        st.caption('Total Activities By Gear Brand')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['brand_name', 'name_gear']).agg(Activities=('upload_id', 'count')).reset_index().rename(columns={'brand_name': 'Gear Brand', 'name_gear': 'Gear'})
        st.bar_chart(temp_df, x='Gear Brand', y='Activities', y_label='# of Activities', color='Gear', use_container_width=True)
        
        st.caption('Total Activities By Gear')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['brand_name', 'name_gear']).agg(Activities=('upload_id', 'count')).reset_index().rename(columns={'name_gear': 'Gear', 'brand_name': 'Gear Brand'})
        st.bar_chart(temp_df, x='Gear', y='Activities', y_label='# of Activities', color='Gear', use_container_width=True)

        st.caption('Activities By Gear By Month')
        temp_df2 = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby(['month_year', 'name_gear'], sort=False).size().reset_index(name='Activities').rename(columns={'month_year': 'Month', 'name_gear': 'Gear'})
        st.line_chart(temp_df2, x='Month', y='Activities', y_label='# of Activities', color='Gear', use_container_width=True)
        
with tab_dist:
    
    with st.container():
        
        st.subheader('Total Distance')
        
        st.caption('Total Distance By Gear Brand')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['brand_name', 'name_gear']).agg(Distance=('distance_activity', 'sum')).reset_index().rename(columns={'brand_name': 'Gear Brand', 'name_gear': 'Gear'})
        st.bar_chart(temp_df, x='Gear Brand', y='Distance', y_label='Distance (mi)', color='Gear', use_container_width=True)
        
        st.caption('Total Distance By Gear')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['brand_name', 'name_gear']).agg(Distance=('distance_activity', 'sum')).reset_index().rename(columns={'name_gear': 'Gear', 'brand_name': 'Gear Brand'})
        st.bar_chart(temp_df, x='Gear', y='Distance', y_label='Distance (mi)', color='Gear', use_container_width=True)

        st.caption('Distance By Gear By Month')
        temp_df2 = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby(['month_year', 'name_gear'], sort=False).agg(Distance=('distance_activity', 'sum')).reset_index().rename(columns={'month_year': 'Month', 'name_gear': 'Gear'})
        st.line_chart(temp_df2, x='Month', y='Distance', y_label='Distance (mi)', color='Gear', use_container_width=True)
