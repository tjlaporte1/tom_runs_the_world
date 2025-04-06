import pandas as pd
import streamlit as st

df = st.session_state.strava_data

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
#act_type_filter = [activity if activity in highlighted_activities else 'Other' for activity in act_type_filter]
act_type_filter = list(dict.fromkeys(act_type_filter))
#act_type_filter.insert(0, 'All')

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
    st.caption('Data as of: ' + max_date)
    st.divider()

# filters in sidebar
with st.sidebar:
    
    st.subheader('Filters')
    
    year_selection = st.selectbox('Years', year_filter, index=1)
    act_type_selection = st.multiselect('Activity Type', act_type_filter, default=highlighted_activities, placeholder='Select Activity Type')
    gear_brand_selection = st.multiselect('Gear Brand', gear_brand_list, default=gear_brand_list, placeholder='Select Gear Brand')

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
