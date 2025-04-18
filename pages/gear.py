import pandas as pd
import streamlit as st
import plotly.express as px

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
tab_act, tab_dist, tab_ele, tab_time, tab_speed, tab_heart, tab_effort = st.tabs(['Activities', 'Distance', 'Elevation', 'Time', 'Speed', 'Heart Rate', 'Relative Effort'])

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
        
        st.caption('Distance By Gear (Box Plot)')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'name_gear': 'Gear', 'brand_name': 'Gear Brand'})
        fig = px.box(temp_df, x='Gear', y='distance_activity', labels={'distance_activity': 'Distance (mi)'}, points='all')
        st.plotly_chart(fig)

with tab_ele:
    
    with st.container():
        
        st.subheader('Total Elevation')
        
        st.caption('Total Elevation By Gear Brand')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['brand_name', 'name_gear']).agg(Elevation=('total_elevation_gain', 'sum')).reset_index().rename(columns={'brand_name': 'Gear Brand', 'name_gear': 'Gear'})
        st.bar_chart(temp_df, x='Gear Brand', y='Elevation', y_label='Elevation (ft)', color='Gear', use_container_width=True)
        
        st.caption('Total Elevation By Gear')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['brand_name', 'name_gear']).agg(Elevation=('total_elevation_gain', 'sum')).reset_index().rename(columns={'name_gear': 'Gear', 'brand_name': 'Gear Brand'})
        st.bar_chart(temp_df, x='Gear', y='Elevation', y_label='Elevation (ft)', color='Gear', use_container_width=True)

        st.caption('Elevation By Gear By Month')
        temp_df2 = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby(['month_year', 'name_gear'], sort=False).agg(Elevation=('total_elevation_gain', 'sum')).reset_index().rename(columns={'month_year': 'Month', 'name_gear': 'Gear'})
        st.line_chart(temp_df2, x='Month', y='Elevation', y_label='Elevation (ft)', color='Gear', use_container_width=True)
        
        st.caption('Elevation By Gear (Box Plot)')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'name_gear': 'Gear', 'brand_name': 'Gear Brand'})
        fig = px.box(temp_df, x='Gear', y='total_elevation_gain', labels={'total_elevation_gain': 'Elevation (ft)'}, points='all')
        st.plotly_chart(fig)
        
with tab_time:
    
    with st.container():
        
        st.subheader('Total Time')
        
        st.caption('Total Time By Gear Brand')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['brand_name', 'name_gear']).agg(Time=('moving_time', 'sum')).reset_index().rename(columns={'brand_name': 'Gear Brand', 'name_gear': 'Gear'})
        temp_df['Time'] = (temp_df['Time'].dt.total_seconds() / 3600).round(2)
        st.bar_chart(temp_df, x='Gear Brand', y='Time', y_label='Time (hrs)', color='Gear', use_container_width=True)
        
        st.caption('Total Time By Gear')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['brand_name', 'name_gear']).agg(Time=('moving_time', 'sum')).reset_index().rename(columns={'name_gear': 'Gear', 'brand_name': 'Gear Brand'})
        temp_df['Time'] = (temp_df['Time'].dt.total_seconds() / 3600).round(2)
        st.bar_chart(temp_df, x='Gear', y='Time', y_label='Time (hrs)', color='Gear', use_container_width=True)

        st.caption('Time By Gear By Month')
        temp_df2 = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby(['month_year', 'name_gear'], sort=False).agg(Time=('moving_time', 'sum')).reset_index().rename(columns={'month_year': 'Month', 'name_gear': 'Gear'})
        temp_df2['Time'] = (temp_df2['Time'].dt.total_seconds() / 3600).round(2)
        st.line_chart(temp_df2, x='Month', y='Time', y_label='Time (hrs)', color='Gear', use_container_width=True)
        
        st.caption('Time By Gear (Box Plot)')
        temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'name_gear': 'Gear', 'brand_name': 'Gear Brand'})
        temp_df['moving_time'] = (temp_df['moving_time'].dt.total_seconds() / 3600).round(2)
        fig = px.box(temp_df, x='Gear', y='moving_time', labels={'moving_time': 'Time (hrs)'}, points='all')
        st.plotly_chart(fig)
        
with tab_speed:
    
    with st.container():
        
        st.subheader('Gear Performance')
        
        st.caption('Avg Speed By Gear')
        temp_df = fn.df_query_builder(df, year_selection, locals()).groupby(['brand_name', 'name_gear']).agg(avg_speed=('average_speed', 'mean')).reset_index().rename(columns={'name_gear': 'Gear', 'brand_name': 'Gear Brand', 'avg_speed': 'Avg Speed'})
        temp_df['Avg Speed'] = temp_df['Avg Speed'].round(2)
        st.bar_chart(temp_df, x='Gear', y='Avg Speed', y_label='Avg Speed (mph)', color='Gear', use_container_width=True)

        st.caption('Avg Speed By Gear By Month')
        temp_df = fn.df_query_builder(df, year_selection, locals()).sort_values(by='start_date_local').groupby(['month_year', 'name_gear'], sort=False).agg(avg_speed=('average_speed', 'mean')).reset_index().rename(columns={'month_year': 'Month', 'name_gear': 'Gear', 'avg_speed': 'Avg Speed'})
        temp_df['Avg Speed'] = temp_df['Avg Speed'].round(2)
        st.line_chart(temp_df, x='Month', y='Avg Speed', y_label='Avg Speed (mph)', color='Gear', use_container_width=True)
        
        # st.caption('Time By Gear (Box Plot)')
        # temp_df = fn.df_query_builder(df, year_selection, locals()).rename(columns={'name_gear': 'Gear', 'brand_name': 'Gear Brand'})
        # temp_df['moving_time'] = (temp_df['moving_time'].dt.total_seconds() / 3600).round(2)
        # fig = px.box(temp_df, x='Gear', y='moving_time', labels={'moving_time': 'Time (hrs)'}, points='all')
        # st.plotly_chart(fig)
        
st.divider()
# created gear dataframe
temp_df = df.groupby(['brand_name', 'name_gear', 'retired']).agg(
    Total_Activities=('upload_id', 'count'),
    Total_Distance=('distance_activity', 'sum'),
    Max_Distance=('distance_activity', 'max'),
    Total_Elevation=('total_elevation_gain', 'sum'),
    Max_Elevation=('total_elevation_gain', 'max'),
    Total_Time=('moving_time', 'sum'),
    Max_Time=('moving_time', 'max'),
    Avg_Speed=('average_speed', 'mean'),
    Max_Speed=('max_speed', 'max'),
    Avg_Heart_Rate=('average_heartrate', 'mean'),
    Max_Heart_Rate=('max_heartrate', 'max'),
    Avg_Relative_Effort=('suffer_score', 'mean'),
    Max_Relative_Effort=('suffer_score', 'max'),
    First_Activity_Date=('start_date_local', 'min'),
    Last_Activity_Date=('start_date_local', 'max')).reset_index().sort_values(by=['retired', 'Last_Activity_Date'],
                                                                              ascending=[True, False]).round(2)

# format date and time
temp_df['First_Activity_Date'] = temp_df['First_Activity_Date'].dt.strftime('%Y-%m-%d')
temp_df['Last_Activity_Date'] = temp_df['Last_Activity_Date'].dt.strftime('%Y-%m-%d')
temp_df['Total_Time'] = (temp_df['Total_Time'].dt.total_seconds() / 3600).round(2)
temp_df['Max_Time'] = (temp_df['Max_Time'].dt.total_seconds() / 3600).round(2)

temp_df.rename(columns={'name_gear': 'Gear'}, inplace=True)
temp_df.columns = temp_df.columns.str.replace('_', ' ').str.title()
temp_df.set_index(['Gear'], inplace=True)

# rename coulns and add helpers
column_config = {
    'Total Distance': st.column_config.NumberColumn('Total Distnace (mi)'),
    'Max Distance': st.column_config.NumberColumn('Max Distance (mi)'),
    'Total Elevation': st.column_config.NumberColumn('Total Elevation (ft)'),
    'Max Elevation': st.column_config.NumberColumn('Max Elevation (ft)'),
    'Total Time': st.column_config.NumberColumn('Total Time (hrs)'),
    'Max Time': st.column_config.NumberColumn('Max Time (hrs)'),
    'Avg Speed': st.column_config.NumberColumn('Avg Speed (mph)'),
    'Max Speed': st.column_config.NumberColumn('Max Speed (mph)'),
    'Avg Heart Rate': st.column_config.NumberColumn('Avg Heart Rate'),
    'Max Heart Rate': st.column_config.NumberColumn('Max Heart Rate'),
    'Avg Relative Effort': st.column_config.NumberColumn('Avg Relative Effort', help='Metric that quantifies the cardiovascular work done during an activity'),
    'Max Relative Effort': st.column_config.NumberColumn('Max Relative Effort', help='Metric that quantifies the cardiovascular work done during an activity')
}

st.subheader('Gear Data')
st.dataframe(temp_df, column_config=column_config)