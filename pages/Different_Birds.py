import streamlit as st
from datetime import date, time
import pandas as pd

from logic.bird_apis import get_desc_from_wiki, get_pic_from_flickr

st.set_page_config(
    page_title="Birdnet Analyzer",
    page_icon=':bird:'
)

@st.cache_data
def get_different_birds(confidence, ttl=3600):
    conn = st.connection('birds_db', type='sql')

    different_birds = conn.query("SELECT com_name FROM detections WHERE confidence>= :confidence GROUP BY com_name",
                                 ttl=ttl, params={"confidence": confidence})
    return different_birds


@st.cache_data
def get_detections_per_bird(confidence, common_name, ttl=3600):
    conn = st.connection('birds_db', type='sql')

    detections_per_bird = conn.query("SELECT COUNT(date) as count, confidence, date, com_name, sci_name"
                                     " FROM detections"
                                     " WHERE com_name= :common_name"
                                     " AND confidence>= :confidence"
                                     " GROUP BY Date"
                                     " ORDER BY Date desc",
                                     ttl=ttl, params={"confidence": confidence, "common_name": common_name})
    detections_per_bird["Confidence"] = detections_per_bird["Confidence"] * 100

    return detections_per_bird

@st.cache_data
def get_times_at_date(confidence, date, common_name, ttl=3600):
    conn = st.connection('birds_db', type='sql')

    detections_date = conn.query("SELECT time, com_name, sci_name"
                                 " FROM detections"
                                 " WHERE com_name= :common_name"
                                 " AND confidence>= :confidence"
                                 " AND Date= :date"
                                 " ORDER BY Time asc",
                                 ttl=ttl, params={"confidence": confidence, "common_name": common_name, "date": date})
    detections_date['Time'] = pd.to_datetime(detections_date['Time'], format='%H:%M:%S')
    detections_date['hour_stamp'] = detections_date['Time'].dt.hour
    detections_date['minute_stamp'] = detections_date['Time'].dt.minute

    time_rounded = []
    for time_detection in detections_date['Time']:
        if time_detection.minute > 45:
            time_rounded.append(time_detection.replace(hour=time_detection.hour+1 ,minute=0, second=0))
        elif time_detection.minute > 30:
            time_rounded.append(time_detection.replace(minute=30, second=0))
        elif time_detection.minute > 15:
            time_rounded.append(time_detection.replace(minute=30, second=0))
        else:
            time_rounded.append(time_detection.replace(minute=0, second=0))
    detections_date['datetime_rounded'] = time_rounded
    return detections_date


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

    if "language" in st.secrets:
        lang = st.secrets["language"]
        desc = get_desc_from_wiki(detections_per_bird["Sci_Name"][0], lang)
    else:
        desc = get_desc_from_wiki(detections_per_bird["Sci_Name"][0])

    pic_url = get_pic_from_flickr(detections_per_bird["Sci_Name"][0])
    if pic_url is not None or desc is not None:
        st.subheader("Description")

    col1, col2 = st.columns([1, 2])
    with col1:
        if pic_url is not None:
            st.image(pic_url, caption=detections_per_bird["Com_Name"][0])
    with col2:
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
