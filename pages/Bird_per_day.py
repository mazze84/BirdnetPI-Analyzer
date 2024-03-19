import streamlit as st
from datetime import date
import pandas as pd

st.set_page_config(
    page_title="Birdnet Analyzer",
    page_icon=':bird:'
)

def get_different_birds(confidence, ttl=3600):
    conn = st.connection('birds_db', type='sql')

    different_birds = conn.query("SELECT com_name FROM detections WHERE confidence>= :confidence GROUP BY com_name",
                               ttl=ttl, params={"confidence": confidence})
    return different_birds

def get_detections_per_bird(confidence, common_name, ttl=3600):
    conn = st.connection('birds_db', type='sql')

    detections_per_bird = conn.query("SELECT COUNT(date) as count, confidence, date, com_name, sci_name"
                                     " FROM detections"
                                     " WHERE com_name= :common_name"
                                     " AND confidence>= :confidence"
                                     " GROUP BY Date"
                                     " ORDER BY Date desc",
                                     ttl=ttl, params={"confidence": confidence, "common_name": common_name})
    return detections_per_bird

def get_times_at_date(confidence, date, common_name, ttl=3600):
    conn = st.connection('birds_db', type='sql')

    detections_date = conn.query("SELECT time, com_name, sci_name"
                                     " FROM detections"
                                     " WHERE com_name= :common_name"
                                     " AND confidence>= :confidence"
                                     " AND Date= :date"
                                     " ORDER BY Date desc",
                                     ttl=ttl, params={"confidence": confidence, "common_name": common_name, "date": date})
    return detections_date

st.title("Detections of bird per day")
if 'confidence' not in st.session_state:
    st.session_state['confidence'] = 70
confidence = st.sidebar.slider("Confidence in %", max_value=99, min_value=70, value=st.session_state.confidence,
                               help="Confidence for detection of birds in Percent", key='confidence')
bird = st.selectbox("Select a Bird", get_different_birds(confidence/100))

if bird is not None:
    detections_24h = get_times_at_date(confidence/100, date.today(), bird)
    detections_24h['Time'] = pd.to_datetime(detections_24h['Time'])
    detections_24h['hour_stamp'] = detections_24h['Time'].dt.hour

    st.write(detections_24h.groupby('hour_stamp').count())
    st.line_chart(detections_24h, x='hour_stamp', y='Com_Name')

    detections_per_bird = get_detections_per_bird(confidence/100, bird)

    st.bar_chart(detections_per_bird, x='Date', y='count')

    st.dataframe(detections_per_bird, column_config={
        "count": st.column_config.NumberColumn("Detection Count", help="Detection of birds", width="small"),
        "date": st.column_config.DateColumn("First Detection", help="Date of the detection", format="YYYY-MM-DD"),
        "Com_Name": st.column_config.TextColumn("Common Name", help="common name of the bird", width="medium"),
        "Sci_Name": st.column_config.TextColumn("Scientific Name", help="scientific name of the bird", width="medium"),
    }, hide_index=True, use_container_width=True)

