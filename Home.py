import streamlit as st
from datetime import date, timedelta
import pandas as pd

st.set_page_config(
    page_title="Birdnet Analyzer",
    page_icon=':bird:'
)

def get_newest_bird_detections(confidence, ttl=3600):
    birds_df = conn.query(
        "select count(*) as count, max(confidence), min(date), sci_name, com_name, min(file_name), min(Cutoff) from detections"
        " where confidence>= :confidence"
        " group by sci_name"
        " order by min(date) desc, time desc",
        ttl=ttl, params={"confidence": confidence})
    birds_df["max(confidence)"] = birds_df["max(confidence)"] * 100
    #birds_df['min(date)'] = pd.to_date(birds_df['min(date)'])
    return birds_df

def get_detections_per_day(confidence, date_from, ttl=3600):
    detections_per_day_df = conn.query("SELECT COUNT(DISTINCT sci_name) as count, date, "
                                    " GROUP_CONCAT(DISTINCT com_name) AS name_list "
                                    " FROM detections"
                                    " WHERE confidence>= :confidence"
                                    " AND date>:date_from"
                                    " GROUP BY Date"
                                    " ORDER BY COUNT(DISTINCT sci_name) desc", ttl=ttl,
                                    params={"confidence": confidence, "date_from": date_from})
    return detections_per_day_df

st.title("Birdnet Analyzer")
# Create the SQL connection to pets_db as specified in your secrets file.
conn = st.connection('birds_db', type='sql')

confidence = st.sidebar.slider("Confidence in %", max_value=99, min_value=70, help="Confidence for detection of birds in Percent")

days = st.sidebar.slider("Days", max_value=365, min_value=1, value=365, help="Days for detection")
date_from = date.today() - timedelta(days=days)

birds_df = get_newest_bird_detections(confidence / 100)
number_new_birds_today = len(birds_df[birds_df['min(date)'] == date.today().isoformat()].index)
st.metric("Different Birds", len(birds_df.index), f'{number_new_birds_today} new today')

st.subheader("Newest Birds")
st.dataframe(birds_df, column_config={
    "count": st.column_config.NumberColumn("Detection Count", width="small"),
    "min(date)": st.column_config.DateColumn("First Detection", help="Date of the first detection", format="YYYY-MM-DD"),
    "max(confidence)" : st.column_config.NumberColumn("Confidence", format="%d", width="small"),
    "Sci_Name": "Scientific Name",
    "Com_Name": "Common Name",
    "min(file_name)": "File Name"
    },hide_index=True, use_container_width=True)

detections_per_day_df = get_detections_per_day(confidence / 100, date_from)
st.subheader("Detected Birds per Day")
st.dataframe(detections_per_day_df, column_config={
    "count": st.column_config.NumberColumn("Detection Count", help="Unique detection of birds", width="small"),
    "date": st.column_config.DateColumn("First Detection", help="Date of the first detection", format="YYYY-MM-DD"),
    "name_list": st.column_config.ListColumn("Birds detected", help="The birds detected that day", width="large"),
    }, hide_index=True, use_container_width=True)


