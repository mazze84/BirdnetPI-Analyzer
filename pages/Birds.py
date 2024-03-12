import streamlit as st

def get_diffent_birds(ttl=3600):
    conn = st.connection('birds_db', type='sql')

    different_birds = conn.query("SELECT com_name FROM detections GROUP BY com_name",
                               ttl=ttl)
    return different_birds

def get_detections_per_bird(common_name, ttl=3600):
    conn = st.connection('birds_db', type='sql')

    detections_per_bird = conn.query("SELECT COUNT(date) as count, date, com_name, sci_name"
                               " FROM detections"
                               " WHERE com_name= :common_name"
                               " GROUP BY Date"
                               " ORDER BY Date desc",
                                ttl=ttl, params={"common_name": common_name})
    return detections_per_bird

st.title("Birds")

option = st.selectbox("Select a Bird", get_diffent_birds())

if option is not None:
    detections_per_bird = get_detections_per_bird(option)
    st.dataframe(detections_per_bird, column_config={
        "count": st.column_config.NumberColumn("Detection Count", help="Detection of birds", width="small"),
        "date": st.column_config.DateColumn("First Detection", help="Date of the detection", format="YYYY-MM-DD"),
        "Com_name": st.column_config.TextColumn("Common Name", help="common name of the bird", width="large"),
        "Sci_name": st.column_config.TextColumn("Scientific Name", help="scientific name of the bird", width="large"),
    }, hide_index=True, use_container_width=True)