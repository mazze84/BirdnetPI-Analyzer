import streamlit as st
from datetime import date

st.title("Recent Detections")

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


confidence = st.sidebar.slider("Confidence in %", max_value=99, min_value=70,
                               help="Confidence for detection of birds in Percent")

date_detections = st.sidebar.date_input("Date of detections")

st.write(date_detections)

birds_df = get_newest_bird_detections(confidence / 100, date_detections)

st.dataframe(birds_df, column_config={
    "date": st.column_config.DateColumn("First Detection", help="Date of the first detection",
                                             format="YYYY-MM-DD"),
    "time": st.column_config.DateColumn("First Detection", help="Time of the first detection",
                                             format="YYYY-MM-DD"),
    "confidence": st.column_config.NumberColumn("Confidence", format="%d", width="small"),
    "Sci_Name": "Scientific Name",
    "Com_Name": "Common Name",
    "file_name": "File Name"
}, hide_index=True, use_container_width=True)


