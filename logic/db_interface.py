import datetime
import streamlit as st

@st.cache_data
def get_newest_bird_detections(confidence, date_detections, ttl=60):
    conn = st.connection('birds_db', type='sql')

    birds_df = conn.query(
        "select confidence, date, time, sci_name, com_name, file_name"
        " from detections"
        " where confidence>= :confidence"
        " and date= :date"
        " order by date desc, time desc",
        ttl=ttl, params={"confidence": confidence, "date": date_detections.isoformat()})
    birds_df["Confidence"] = birds_df["Confidence"] * 100

    return birds_df

@st.cache_data
def get_rarity(sci_name, ttl=60):
    conn = st.connection('birds_db', type='sql')

    rarity_df = conn.query(
        "select count(*) as count"
        " from detections"
        " where date> :date and sci_name= :sci_name",
        ttl=ttl, params={"sci_name": sci_name, "date": (datetime.datetime.now() - datetime.timedelta(30)).isoformat()})

    if rarity_df['count'][0] >= 30:
        return 'common', rarity_df['count'][0], "green"
    else:
        return 'rare', rarity_df['count'][0], "orange"
