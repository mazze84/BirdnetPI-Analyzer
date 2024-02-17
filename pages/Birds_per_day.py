import streamlit as st

def get_detections_per_day(confidence, ttl=3600):
    conn = st.connection('birds_db', type='sql')

    detections_per_day_df = conn.query("SELECT COUNT(DISTINCT sci_name) as count, date, "
                                       " GROUP_CONCAT(DISTINCT com_name) AS name_list "
                                       " FROM detections"
                                       " WHERE confidence>= :confidence"
                                       " GROUP BY Date"
                                       " ORDER BY COUNT(DISTINCT sci_name) desc"
                                       " LIMIT 15",
                                       ttl=ttl, params={"confidence": confidence})
    return detections_per_day_df

confidence = st.sidebar.slider("Confidence in %", max_value=99, min_value=70,
                               help="Confidence for detection of birds in Percent")

detections_per_day_df = get_detections_per_day(confidence / 100)

col1, col2 = st.columns([2,5])
with col1:
    st.metric(f'Most Birds on {detections_per_day_df["Date"][0]}', detections_per_day_df['count'][0])
with col2:
    st.write(detections_per_day_df["name_list"][0])


st.subheader("Detected Birds per Day")
st.dataframe(detections_per_day_df, column_config={
    "count": st.column_config.NumberColumn("Detection Count", help="Unique detection of birds", width="small"),
    "date": st.column_config.DateColumn("First Detection", help="Date of the first detection", format="YYYY-MM-DD"),
    "name_list": st.column_config.ListColumn("Birds detected", help="The birds detected that day", width="large"),
}, hide_index=True, use_container_width=True)
