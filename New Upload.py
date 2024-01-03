import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path
from mysql.connector import Error
import base64
import classes as cl
import css_strings as cs
from email_validator import validate_email, EmailNotValidError

st.set_page_config(layout='wide', page_title='Beyond Heavens',
                   initial_sidebar_state='expanded')

est_connection = cl.EstablishConnection()
connection = est_connection.database_connection()


def validate_current_name(filename):
    existing_records = fetch_existing_files()
    existing_filenames = [Path(record_file_name[0]).stem for
                          record_file_name in existing_records]
    return filename in existing_filenames


def fetch_existing_files():
    try:
        cursor = connection.cursor()
        records_query = "SELECT filename, content FROM videos"
        cursor.execute(records_query)
        records = cursor.fetchall()
        cursor.close()
        return records
    except Error as e:
        st.error(f"Error: {e}")
    return []


def edit_file_name(filename):
    # Create new file name with current date
    now = datetime.now()
    new_file_name = (filename + ' (' + str(now.month) +
                     '-' + str(now.day) + '-' + str(now.hour)
                     + str(now.minute) + ')')
    return new_file_name


# Create table to store video files
def create_video_table():
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS videos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255),
            content LONGBLOB,
            receiveremailid VARCHAR(255),
            senddate VARCHAR(255),
            status VARCHAR(255)
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
    except Error as e:
        st.error(f"Error: {e}")


# Insert uploaded video file into database
def insert_video(file_name, encoded_content_str, vid_receiver_email, vid_send_date, vid_send_time):
    try:
        send_date_time = str(vid_send_date) + " " + str(vid_send_time)
        cursor = connection.cursor()
        insert_query = ("INSERT INTO videos (filename, content, receiveremailid, senddate) "
                        "VALUES (%s, %s, %s, %s)")
        cursor.execute(insert_query, (file_name, encoded_content_str,
                                      vid_receiver_email, send_date_time))
        connection.commit()
        cursor.close()
        st.success(f"Video '{file_name}' inserted successfully")
    except Error as e:
        st.error(f"Error: {e}")


# Get recording send date, time, video name & receiver email address
def get_send_datetime():
    st.header("Enter recording details")

    with (st.form("recording_details")):
        col1, col2 = st.columns(2)
        tomorrow = datetime.today()
                # + timedelta(days=1)
        # Request recording details
        with col1:
            name_input = st.text_input(label='Recording Name',
                                       placeholder='Add recording name here...', label_visibility='hidden')
            email_input = st.text_input(label='Receiver email',
                                        placeholder='Enter receiver email id...',
                                        label_visibility='hidden')

        with col2:
            date_input = st.date_input(label='Select a send date', value=tomorrow,
                                       min_value=tomorrow, format="DD/MM/YYYY")
            time_input = st.time_input(label="Select a time", value=None)
            # for time input in hours only, use below:
            # time_input = st.time_input(label="Select hour of the day", value=None,
            #                            step=timedelta(hours=1))
        # Form submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            if (name_input.strip() == '' or date_input == '' or email_input.strip() == ''
                    or time_input is None):
                st.write("All the fields are required, please provide relevant data!")
            else:
                if email_input != '':
                    email_address_status = validate_email_address(email_input)
                    return name_input, email_input, date_input, time_input, email_address_status
                else:
                    return name_input, email_input, date_input, time_input, "INVALID"
        else:
            return name_input, email_input, date_input, time_input, ""


def validate_email_address(email_address_input):
    try:
        v = validate_email(email_address_input)
        return "VALID"
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        return str(e)


def main():
    if 'recording_name' not in st.session_state:
        st.session_state.recording_name = ""
    if 'recording_date' not in st.session_state:
        st.session_state.recording_date = ""
    if 'recording_time' not in st.session_state:
        st.session_state.recording_time = ""
    if 'receiver_email' not in st.session_state:
        st.session_state.receiver_email = ""

    st.title('Upload a recorded video!')

    st.markdown(f'<style>{cs.hide_fileuploader_extended}</style>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Browse files", type='mp4',
                                     key='file_picker', label_visibility='hidden')

    css = cs.browse_files_btn_css

    st.markdown(css, unsafe_allow_html=True)

    # Create videos table
    create_video_table()

    if uploaded_file is not None:
        st.text(uploaded_file.name)
        rec_name, receiver_email, rec_date, rec_time, email_validity = get_send_datetime()
        if (rec_name != '' and receiver_email != "" and email_validity == 'VALID'
                and rec_date != '' and rec_time is not None):
            # Extract file name and content
            file_content = uploaded_file.read()

            # Validate if filename exists or not
            name_exists = validate_current_name(rec_name)
            if name_exists:
                rec_name = edit_file_name(rec_name)

            encoded_content = base64.b64encode(file_content)
            encoded_content_str = encoded_content.decode('utf-8')

            insert_video(rec_name, encoded_content_str, receiver_email, rec_date, rec_time)

            # send_email(receiver_email)

            # Clear the input elements
            if ('recording_name' in st.session_state or 'recording_date' in st.session_state
                    or 'recording_time' in st.session_state or 'file_picker' in st.session_state
                    or 'receiver_email' in st.session_state):
                del st.session_state['recording_name']
                del st.session_state['receiver_email']
                del st.session_state['recording_date']
                del st.session_state['recording_time']
                del st.session_state['file_picker']
                st.rerun()
        elif email_validity != '' and email_validity != 'VALID' and email_validity != 'INVALID':
            st.write(email_validity)
            st.write("Example: name@example.com")


# Run application
main()
