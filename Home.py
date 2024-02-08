import streamlit as st
from datetime import date, timedelta


st.title("Birdnet Analyzer")
# Create the SQL connection to pets_db as specified in your secrets file.
conn = st.connection('birds_db', type='sql')

confidence = st.sidebar.slider("Confidence", max_value=1.0, min_value=.7, help="Confidence for detection of birds")

days = st.sidebar.slider("Days", max_value=365, min_value=1, value=365, help="Days for detection")
date_from = date.today() - timedelta(days=days)


# Query and display the data you inserted
birds_df = conn.query("select count(*) as count, min(date), sci_name, com_name, min(file_name) from detections"
                      " where confidence>= :confidence"
                      " group by sci_name"
                      " order by min(date) desc, time desc",
                      ttl=3600, params={"confidence": confidence})
number_new_birds_today = len(birds_df[birds_df['min(date)'] == date.today()].index)
st.metric("Different Birds", len(birds_df.index), f'{number_new_birds_today} new today')

st.subheader("Newest Birds")
st.dataframe(birds_df, column_config={
    "count": st.column_config.NumberColumn("Detection Count"),
    "min(date)": st.column_config.DateColumn("First Detection", help="Date of the first detection"),
    "Sci_Name": "Scientific Name",
    "Com_Name": "Common Name",
    "min(file_name)": "File Name"
    },hide_index=True, use_container_width=True)

most_detections_df = conn.query("SELECT COUNT(DISTINCT sci_name) as count, date, "
                                " GROUP_CONCAT(DISTINCT com_name) AS name_list "
                                " FROM detections"
                                " WHERE confidence>= :confidence"
                                " AND date>:date_from"
                                " GROUP BY Date"
                                " ORDER BY COUNT(DISTINCT sci_name) desc", ttl=3600,
                                params={"confidence": confidence, "date_from": date_from})
st.subheader("Detected Birds per Day")
st.dataframe(most_detections_df, column_config={
    "count": st.column_config.NumberColumn("Detection Count", help="Unique detection of birds"),
    "date": st.column_config.DateColumn("First Detection", help="Date of the first detection")
    }, hide_index=True, use_container_width=True)


