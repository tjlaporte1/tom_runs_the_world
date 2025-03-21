import pandas as pd
import streamlit as st

from main import df, max_date

# distinct gear type list
gear_list = df['name_gear'].value_counts().index.tolist()
gear_list = gear_list[~pd.isnull(gear_list)]
gear_list.insert(0, 'All')

page_head = st.container()
page_head.title('Tom Runs The World')
page_head.subheader('Strava Data Analysis')
page_head.caption('Data as of: ' + max_date)
page_head.button('Refresh Data')
page_head.divider()

filter_col1, filter_col2 = st.columns([7,1])
with filter_col1:
    st.subheader('Activity Type')
    act_type_selection = st.segmented_control('Activity Type', ['All', 'distinct activity types'])
with filter_col2:
    st.subheader('Year')
    year_selection = st.selectbox('Years', [2025, 2024, 'All', 'Rolling 12 mo'])
