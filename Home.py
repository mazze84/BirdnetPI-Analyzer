import streamlit as st
from datetime import date, timedelta

# Create the SQL connection to pets_db as specified in your secrets file.
conn = st.connection('birds_db', type='sql')

date_from = date.today() - timedelta(days=5)
confidence = 0.7
# Query and display the data you inserted
birds_df = conn.query("select count(*) as count, min(date), sci_name, com_name, min(file_name) from detections"
                      " where date>:date_from"
                      " and confidence>= :confidence"
                      " group by sci_name"
                      " order by min(date) desc, time desc",
                      ttl=5, params={"date_from": date_from, "confidence": confidence})

st.dataframe(birds_df, column_config={
    "count": st.column_config.NumberColumn("Detection Count"),
    "min(date)": st.column_config.DateColumn(
        "First Detection",
        help="Date of the first detection"
    ),
    "Sci_Name": "Scientific Name",
    "Com_Name": "Common Name",
    "min(file_name)": "File Name"
},
             hide_index=True, use_container_width=True)

most_detections_df = conn.query("SELECT count(DISTINCT sci_name) as count, date, "
                                " GROUP_CONCAT(DISTINCT com_name) AS name_list "
                                " FROM detections"
                                " where confidence>= :confidence"
                                " group by Date"
                                " ORDER BY count(DISTINCT sci_name) desc", ttl=5, params={"confidence": confidence})
st.dataframe(most_detections_df, column_config={
    "count": st.column_config.NumberColumn("Detection Count", help="Unique detection of birds"),
    "date": st.column_config.DateColumn("First Detection", help="Date of the first detection")
},
             hide_index=True, use_container_width=True)

conn.close()
