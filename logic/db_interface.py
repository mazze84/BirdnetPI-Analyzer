import datetime
import streamlit as st
import pandas as pd

def get_most_recent_bird_detections(confidence, date_detections, ttl=60):
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

@st.cache_data
def get_rarity(sci_name, ttl=3600):
    conn = st.connection('birds_db', type='sql')

    rarity_df = conn.query(
        "select count(*) as count"
        " from detections"
        " where date> :date and sci_name= :sci_name"
        " group by sci_name",
        ttl=ttl, params={"sci_name": sci_name, "date": (datetime.datetime.now() - datetime.timedelta(30)).isoformat()})

    # might be that no bird was detected in the last month
    if len(rarity_df) <= 0:
        return 'rare', 0, "orange"
    elif rarity_df['count'][0] >= 30:
        return 'common', rarity_df['count'][0], "green"
    else:
        return 'rare', rarity_df['count'][0], "orange"

@st.cache_data
def get_rare_bird(confidence, date, ttl=3600):
    conn = st.connection('birds_db', type='sql')

    different_birds = conn.query("SELECT d1.sci_name,"
                                " d1.com_name," 
                                " MAX(d1.confidence) AS max_confidence"
                                " FROM detections d1"
                                " WHERE d1.confidence >= :confidence"
                                " AND d1.date = :date"
                                " AND EXISTS ("
                                    "SELECT 1 FROM detections d2"
                                    " WHERE d2.sci_name = d1.sci_name"
                                    " AND d2.date > :rarity_date"
                                    " GROUP BY d2.sci_name"
                                    " HAVING COUNT(*) > 300"
                                ")"
                                " GROUP BY d1.sci_name, d1.com_name;",
                                 ttl=ttl, params={"confidence": confidence, "date": date, "rarity_date": (date-datetime.timedelta(30)).isoformat()})
    return different_birds

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

@st.cache_data
def get_newest_bird_detections(confidence, date=None, ttl=3600):
    conn = st.connection('birds_db', type='sql')
    where = ""
    if date is not None:
        today = datetime.date.today().isoformat()
        where = f' where date=\'{today}\''
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

@st.cache_data
def get_most_active_bird(confidence, order_by, limit,  ttl=3600):
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
