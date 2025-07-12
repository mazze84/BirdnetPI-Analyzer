from pathlib import Path
import streamlit as st
import altair as alt

from logic.bird_apis import get_pic_from_flickr, get_short_desc_wiki
from logic.db_interface import get_rarity, get_most_recent_bird_detections, get_rare_bird
from logic.formatting import format_date

st.set_page_config(
    page_title="Birdnet Analyzer",
    page_icon=':bird:'
)


if "confidence" not in st.session_state:
    st.session_state.confidence = 70
confidence = st.sidebar.slider("Confidence in %", max_value=99, min_value=70, value=st.session_state.confidence,
                               help="Confidence for detection of birds in Percent")

date_detections = st.sidebar.date_input("Date of detections")

st.title(f'Birds on {format_date(date_detections)}')
birds_df = get_most_recent_bird_detections(confidence / 100, date_detections)
if len(birds_df) > 0:
    df_rarity = get_rare_bird(confidence / 100, date_detections)
    if len(df_rarity) > 0:
        st.write(df_rarity['Com_Name'][0])
    else:
        st.write("no rare birds")
    number_detections = birds_df.groupby('Com_Name', as_index=False, sort=True)['Confidence'].count().rename(
        columns={"Com_Name": "Common Name", "Confidence": "Count"}).sort_values(by='Count', ascending=False)
    # st.write(number_detections)
    st.altair_chart(alt.Chart(number_detections).mark_bar().encode(
        x=alt.X('Common Name', sort=None),
        y='Count',
    ), use_container_width=True)

    st.subheader("Last detected bird:")
    col1, col2 = st.columns([1, 1])
    with col1:
        pic_url = get_pic_from_flickr(birds_df['Sci_Name'][0])
        if pic_url is not None:
            st.image(pic_url, caption=birds_df["Com_Name"][0])

    with col2:
        rarity = get_rarity(birds_df['Sci_Name'][0])
        st.badge(rarity[0], color=rarity[2])
        st.write(f"Seen {rarity[1]} times in the last 30 Days")
        if "language" in st.secrets:
            lang = st.secrets["language"]
            desc = get_short_desc_wiki(birds_df["Sci_Name"][0], lang)
        else:
            desc = get_short_desc_wiki(birds_df["Sci_Name"][0])

        if desc is not None:
            st.write(desc)

st.dataframe(birds_df, column_config={
    "Date": st.column_config.DateColumn("Date", help="Date of the first detection",
                                        format="YYYY-MM-DD"),
    "Time": st.column_config.TimeColumn("Time", help="Time of the first detection"),
    "Confidence": st.column_config.NumberColumn("Confidence", format="%d", width="small"),
    "Sci_Name": "Scientific Name",
    "Com_Name": "Common Name",
    "File_Name": "File Name"
}, hide_index=True, use_container_width=True)

if birds_df.size >= 10:
    for i in range(10):
        filename = birds_df['File_Name'][i].replace(':', ' ')
        bird_name = birds_df['Com_Name'][i]
        path = Path(f'By_Date/{date_detections}/{bird_name}/{filename}')
        if path.is_file():
            st.image(str(path) + '.png', caption=f'{bird_name}')
            st.audio(str(path))
