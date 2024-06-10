import streamlit as st
import altair as alt

st.set_page_config(
    page_title="Birdnet Analyzer",
    page_icon=':bird:'
)


@st.cache_data
def get_most_detections_per_day(confidence, ttl=3600):
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


@st.cache_data
def get_least_detections_per_day(confidence, ttl=3600):
    conn = st.connection('birds_db', type='sql')

    detections_per_day_df = conn.query("SELECT COUNT(DISTINCT sci_name) as count, date, "
                                       " GROUP_CONCAT(DISTINCT com_name) AS name_list "
                                       " FROM detections"
                                       " WHERE confidence>= :confidence"
                                       " GROUP BY Date"
                                       " ORDER BY COUNT(DISTINCT sci_name) asc"
                                       " LIMIT 15",
                                       ttl=ttl, params={"confidence": confidence})
    return detections_per_day_df


if "confidence" not in st.session_state:
    st.session_state.confidence = 70

confidence = st.sidebar.slider("Confidence in %", max_value=99, min_value=70, value=st.session_state.confidence,
                               help="Confidence for detection of birds in Percent")

most_per_day_df = get_most_detections_per_day(confidence / 100)
least_per_day_df = get_least_detections_per_day(confidence / 100)

st.subheader("Most detected Birds per Day")

col1, col2 = st.columns([2, 5])
with col1:
    st.metric(f'Most Birds on {most_per_day_df["Date"][0]}', most_per_day_df['count'][0])
with col2:
    st.write(most_per_day_df["name_list"][0])

st.altair_chart(alt.Chart(most_per_day_df).mark_bar().encode(
    x=alt.X('Date', sort=None),
    y='count',
), use_container_width=True)
st.dataframe(most_per_day_df, column_config={
    "count": st.column_config.NumberColumn("Different birds", help="Unique detection of birds", width="small"),
    "date": st.column_config.DateColumn("First Detection", help="Date of the first detection", format="YYYY-MM-DD"),
    "name_list": st.column_config.ListColumn("Birds detected", help="The birds detected that day", width="large"),
}, hide_index=True, use_container_width=True)

st.subheader("Least detected Birds per Day")

col1, col2 = st.columns([2, 5])
with col1:
    st.metric(f'Least Birds on {least_per_day_df["Date"][0]}', least_per_day_df['count'][0])
with col2:
    st.write(least_per_day_df["name_list"][0])
st.altair_chart(alt.Chart(least_per_day_df).mark_bar().encode(
    x=alt.X('Date', sort=None),
    y='count',
), use_container_width=True)
st.dataframe(least_per_day_df, column_config={
    "count": st.column_config.NumberColumn("Different birds", help="Unique detection of birds", width="small"),
    "date": st.column_config.DateColumn("First Detection", help="Date of the first detection", format="YYYY-MM-DD"),
    "name_list": st.column_config.ListColumn("Birds detected", help="The birds detected that day", width="large"),
}, hide_index=True, use_container_width=True)
