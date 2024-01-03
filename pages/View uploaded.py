import streamlit as st
from mysql.connector import Error
import base64
import classes as cl

st.set_page_config(layout='wide', page_title='Beyond Heavens',
                   initial_sidebar_state='expanded')

est_connection = cl.EstablishConnection()
connection = est_connection.database_connection()


def count_existing_files():
    try:
        cursor = connection.cursor()
        count_query = "SELECT count(*) FROM videos"
        cursor.execute(count_query)
        row_count = cursor.fetchall()[0][0]
        cursor.close()
        return row_count
    except Error as e:
        st.error(f"Error: {e}")
    return 0


def extract_records():
    try:
        cursor = connection.cursor()
        records_query = "SELECT filename, content, receiveremailid, senddate FROM videos"
        cursor.execute(records_query)
        records = cursor.fetchall()
        cursor.close()
        return records
    except Error as e:
        st.error(f"Error: {e}")
    return []


def render_video(fetched_records):
    for filename, content, receiveremailid, senddate in fetched_records:
        try:
            button_name = filename
            col3, col4 = st.columns(2)
            with col3:
                watch_btn_key = f'watch_btn_{filename}'
                watch_button_clicked = st.button(f"Watch: {button_name}", use_container_width=True,
                                                 key=watch_btn_key)
            with col4:
                st.write("**Recipient:** ", receiveremailid)
                st.write("**Scheduled send date & time:** ", senddate)

            st.write("<hr>", unsafe_allow_html=True)
            
            if watch_button_clicked:
                decoded_content = base64.b64decode(content)
                video_frame = st.video(decoded_content, format="video/mp4", start_time=0)
                close_btn_key = f'close_vid_{filename}'
                close_button_clicked = st.button("Close", use_container_width=True,
                                                 key=close_btn_key)
                if close_button_clicked:
                    del close_button_clicked
                    del video_frame
        except Exception as e:
            st.error(f"Error encoding video content: {e}")
            return None


total_videos = count_existing_files()
if total_videos > 0:
    st.title("Your uploaded files:")
    existing_records = extract_records()
    render_video(existing_records)
else:
    st.title("No uploaded files!")
