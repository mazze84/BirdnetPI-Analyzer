import streamlit as st
from datetime import date, time
import pandas as pd

from logic.bird_apis import get_desc_from_wiki, get_pic_from_flickr
from logic.db_interface import get_rarity, get_different_birds, get_times_at_date, get_detections_per_bird

st.set_page_config(
    page_title="Birdnet Analyzer",
    page_icon=':bird:'
)


st.title("Detected birds")

if "confidence" not in st.session_state:
    st.session_state.confidence = 70
confidence = st.sidebar.slider("Confidence in %", max_value=99, min_value=70, value=st.session_state.confidence,
                               help="Confidence for detection of birds in Percent")
bird = st.selectbox("Select a Bird", get_different_birds(confidence / 100))

if bird is not None:

    detections_24h = get_times_at_date(confidence / 100, date.today(), bird)

    timestamp = []
    for i in range(24):
        timestamp.append(time(i, 0))
        timestamp.append(time(i, 30))
        # s_row = pd.Series([time(i, 0), 0, 0, 0, 0], index=detection_count.columns)
    # st.write(timestamp)
    # timeline_df['timestamp24h'] = timestamp
    #st.write(detections_24h)
    detection_count = detections_24h.groupby(['datetime_rounded']).count()

    # date = detections_24h['datetime_rounded'][0]

    for time in timestamp:
        # s_row = pd.Series([time, 0,0,0,0], index=detection_count.columns
        # st.write(date.set_time(time))
        detection_count.loc[len(detection_count.index)] = [time, 0,0,0,0]
    #st.write(detection_count)

    #st.line_chart(detections_24h, x='datetime_rounded', y='Com_Name')

    detections_per_bird = get_detections_per_bird(confidence / 100, bird)
    sci_bird = detections_per_bird["Sci_Name"][0]
    if "language" in st.secrets:
        lang = st.secrets["language"]
        desc = get_desc_from_wiki(sci_bird, lang)
    else:
        desc = get_desc_from_wiki(sci_bird)

    pic_url = get_pic_from_flickr(sci_bird)
    if pic_url is not None or desc is not None:
        st.subheader("Description")

    col1, col2 = st.columns([1, 2])
    with col1:
        if pic_url is not None:
            st.image(pic_url, caption=detections_per_bird["Com_Name"][0])


    with col2:
        rarity = get_rarity(sci_bird)
        st.badge(rarity[0], color=rarity[2])
        st.write(f"Seen {rarity[1]} times in the last 30 Days")
        if desc is not None:
            st.write(desc)


    st.bar_chart(detections_per_bird, x='Date', y='count')

    st.dataframe(detections_per_bird, column_config={
        "count": st.column_config.NumberColumn("Detection Count", help="Detection of birds", width="small"),
        "Confidence": st.column_config.NumberColumn("Confidence", format="%d", width="small"),
        "date": st.column_config.DateColumn("First Detection", help="Date of the detection", format="YYYY-MM-DD"),
        "Com_Name": st.column_config.TextColumn("Common Name", help="common name of the bird", width="medium"),
        "Sci_Name": st.column_config.TextColumn("Scientific Name", help="scientific name of the bird", width="medium"),
    }, hide_index=True, use_container_width=True)
