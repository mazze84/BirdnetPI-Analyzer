from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="Birdnet Analyzer",
    page_icon=':bird:'
)

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

if 'confidence' not in st.session_state:
    st.session_state['confidence'] = 70
confidence = st.sidebar.slider("Confidence in %", max_value=99, min_value=70, value=st.session_state.confidence,
                               help="Confidence for detection of birds in Percent", key='confidence')

date_detections = st.sidebar.date_input("Date of detections")

st.title(f'Birds on {date_detections}')

birds_df = get_newest_bird_detections(confidence / 100, date_detections)

st.dataframe(birds_df, column_config={
    "Date": st.column_config.DateColumn("Date", help="Date of the first detection",
                                             format="YYYY-MM-DD"),
    "Time": st.column_config.TimeColumn("Time", help="Time of the first detection"),
    "Confidence": st.column_config.NumberColumn("Confidence", format="%d", width="small"),
    "Sci_Name": "Scientific Name",
    "Com_Name": "Common Name",
    "File_Name": "File Name"
}, hide_index=True, use_container_width=True)

if birds_df.size > 0:
    filename = birds_df['File_Name'][0].replace(':', ' ')
    bird_name = birds_df['Com_Name'][0]
    path = Path(f'By_Date/{date_detections}/{bird_name}/{filename}')
    if path.is_file():
        st.image(str(path) + '.png', caption=f'{bird_name}')
        st.audio(str(path))



