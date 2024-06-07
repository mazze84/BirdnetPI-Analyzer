import streamlit as st
from datetime import date, timedelta
import pandas as pd

from logic.bird_apis import get_pic_from_flickr

st.set_page_config(
    page_title="Birdnet Analyzer",
    page_icon=':bird:'
)


def get_newest_bird_detections(confidence, daily=False, ttl=3600):
    conn = st.connection('birds_db', type='sql')
    where = ""
    if daily:
        today = date.today().isoformat()
        where = f' and date=\'{today}\''
    birds_df = conn.query(
        "select count(*) as count, max(confidence), min(date), sci_name, com_name, min(file_name), min(Cutoff)"
        " from detections"
        " where confidence>= :confidence"
        + where +
        " group by sci_name"
        " order by min(date) desc, time desc",
        ttl=ttl, params={"confidence": confidence})
    birds_df["max(confidence)"] = birds_df["max(confidence)"] * 100
    # birds_df['min(date)'] = pd.to_date(birds_df['min(date)'])
    return birds_df

st.title("Birdnet Analyzer")
# Create the SQL connection to pets_db as specified in your secrets file.


daily = st.sidebar.checkbox("Daily")
if st.session_state.confidence is None:
    st.session_state.confidence = 70
confidence = st.sidebar.slider("Confidence in %", max_value=99, min_value=70, value=st.session_state.confidence,
                               help="Confidence for detection of birds in Percent")

#days = st.sidebar.slider("Days", max_value=365, min_value=1, value=365, help="Days for detection")
#date_from = date.today() - timedelta(days=days)


birds_df = get_newest_bird_detections(confidence / 100, daily=daily)
number_new_birds_today = len(birds_df[birds_df['min(date)'] == date.today().isoformat()].index)

col1, col2 = st.columns([1, 1])
with col1:
    st.metric("Different Birds", len(birds_df.index), f'{number_new_birds_today} new today')
with col2:
    pic_url = get_pic_from_flickr(birds_df['Com_Name'][0])
    if pic_url is not None:
        st.write("Newest:")
        st.image(pic_url, caption=birds_df["Com_Name"][0])

st.subheader("Newest Birds")
st.dataframe(birds_df, column_config={
    "count": st.column_config.NumberColumn("Detection Count", width="small"),
    "min(date)": st.column_config.DateColumn("First Detection", help="Date of the first detection",
                                             format="YYYY-MM-DD"),
    "max(confidence)": st.column_config.NumberColumn("Confidence", format="%d", width="small"),
    "Sci_Name": "Scientific Name",
    "Com_Name": "Common Name",
    "min(file_name)": "File Name"
}, hide_index=True, use_container_width=True)
