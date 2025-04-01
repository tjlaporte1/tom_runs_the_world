import pandas as pd
import streamlit as st

import Overview as o

# distinct gear type list
gear_brand_list = o.df['brand_name'].value_counts().index.tolist()

# header
with st.container():
    st.title('Tom Runs The World')
    st.subheader('Strava Data Analysis')
    st.caption('Data as of: ' + o.max_date)
    st.divider()

# filters
filter_col1, filter_col2 = st.columns([3, 1])
with filter_col1:
    act_type_selection = st.segmented_control('Activity Type', o.act_type_filter, default=o.highlighted_activities, selection_mode='multi')
with filter_col2:
    year_selection = st.selectbox('Years', o.year_filter, index=1)
    
gear_brand_selection = st.segmented_control('Gear Brand', gear_brand_list, default=gear_brand_list, selection_mode='multi')
