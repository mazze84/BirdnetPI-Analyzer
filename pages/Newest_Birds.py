import streamlit as st
import datetime

from logic.bird_apis import get_pic_from_flickr
from logic.db_interface import get_newest_bird_detections

st.set_page_config(
    page_title="Birdnet Analyzer",
    page_icon=':bird:'
)



st.title("Birdnet Analyzer")
# Create the SQL connection to pets_db as specified in your secrets file.


daily = st.sidebar.checkbox("Daily")

if "confidence" not in st.session_state:
    st.session_state.confidence = 70
confidence = st.sidebar.slider("Confidence in %", max_value=99, min_value=70, value=st.session_state.confidence,
                               help="Confidence for detection of birds in Percent")

#days = st.sidebar.slider("Days", max_value=365, min_value=1, value=365, help="Days for detection")
#date_from = date.today() - timedelta(days=days)

if daily:
    birds_df = get_newest_bird_detections(confidence / 100, datetime.date.today().isoformat())
else:
    birds_df = get_newest_bird_detections(confidence / 100)

if birds_df.size >0:
    number_new_birds_today = len(birds_df[birds_df['min(date)'] == datetime.date.today().isoformat()].index)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.metric("Different Birds", len(birds_df.index), f'{number_new_birds_today} new today')
    with col2:
        pic_url = get_pic_from_flickr(birds_df['Sci_Name'][0])
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
else:
    st.write("No birds yet.")
