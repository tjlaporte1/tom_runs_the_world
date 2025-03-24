import pandas as pd
import streamlit as st

import main as m

# distinct gear type list
gear_list = m.df['name_gear'].value_counts().index.tolist()
gear_list.insert(0, 'All')

with st.container():
    st.title('Tom Runs The World')
    st.subheader('Strava Data Analysis')
    st.caption('Data as of: ' + m.max_date)
    st.divider()

filter_col1, filter_col2 = st.columns([2, 1])
with filter_col1:
    act_type_selection = st.segmented_control('Activity Type', m.act_type_filter, default='All')
with filter_col2:
    year_selection = st.selectbox('Years', m.year_filter, index=1)
