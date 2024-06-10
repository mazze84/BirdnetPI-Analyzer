import streamlit as st
from datetime import date
import altair as alt

st.set_page_config(
    page_title="Birdnet Analyzer",
    page_icon=':bird:'
)


@st.cache_data
def get_most_active_bird(confidence, order_by, ttl=60):
    conn = st.connection('birds_db', type='sql')

    birds_df = conn.query(
        "select count(*) as Count, avg(confidence) as Confidence, com_name, sci_name"
        " from detections"
        " where confidence >= :confidence"
        " group by sci_name, com_name"
        " order by count(*) " + order_by +
        " limit " + str(limit),
        ttl=ttl, params={"confidence": confidence})
    birds_df["Confidence"] = birds_df["Confidence"] * 100

    return birds_df


if "confidence" not in st.session_state:
    st.session_state.confidence = 70
confidence = st.sidebar.slider("Confidence in %", max_value=99, min_value=70, value=st.session_state.confidence,
                               help="Confidence for detection of birds in Percent")
limit = st.sidebar.slider("How many birds will be shown", max_value=30, min_value=1, value=15,
                          key='limit')

st.subheader("Most active birds")

most_active = get_most_active_bird(confidence / 100, "desc", limit)
st.altair_chart(alt.Chart(most_active).mark_bar().encode(
    x=alt.X('Com_Name', sort=None),
    y='Count',
), use_container_width=True)

st.dataframe(most_active, column_config={
    "Date": st.column_config.DateColumn("Date", help="Date of the first detection",
                                        format="YYYY-MM-DD"),
    "Time": st.column_config.TimeColumn("Time", help="Time of the first detection"),
    "Confidence": st.column_config.NumberColumn("Confidence", format="%d", width="small"),
    "Com_Name": "Common Name",
    "Sci_Name": "Scientific Name",

    "File_Name": "File Name"
}, hide_index=True, use_container_width=True)

st.subheader("Least active birds")

least_active = get_most_active_bird(confidence / 100, "asc", limit)
st.altair_chart(alt.Chart(least_active).mark_bar().encode(
    x=alt.X('Com_Name', sort=None),
    y='Count',
), use_container_width=True)
st.dataframe(least_active, column_config={
    "Date": st.column_config.DateColumn("Date", help="Date of the first detection",
                                        format="YYYY-MM-DD"),
    "Time": st.column_config.TimeColumn("Time", help="Time of the first detection"),
    "Confidence": st.column_config.NumberColumn("Confidence", format="%d", width="small"),
    "Com_Name": "Common Name",
    "Sci_Name": "Scientific Name",

    "File_Name": "File Name"
}, hide_index=True, use_container_width=True)
