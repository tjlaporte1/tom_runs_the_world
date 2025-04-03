import pandas as pd
import streamlit as st

import Overview as o

# header
with st.container():
    st.title('Tom Runs The World')
    st.subheader('Strava Data Analysis')
    st.caption('Data as of: ' + o.max_date)
    st.divider()

# filters in sidebar
with st.sidebar:
    
    st.subheader('Filters')
    
    year_selection = st.selectbox('Years', o.year_filter, index=1)
    act_type_selection = st.multiselect('Activity Type', o.act_type_filter, default=o.highlighted_activities, placeholder='Select Activity Type')
    gear_brand_selection = st.multiselect('Gear Brand', o.gear_brand_list, default=o.gear_brand_list, placeholder='Select Gear Brand')
