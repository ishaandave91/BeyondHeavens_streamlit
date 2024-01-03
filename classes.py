import os
from datetime import datetime
from pathlib import Path
import streamlit as st
import mysql.connector
from mysql.connector import Error
from io import BytesIO
import base64
import css_strings as cs


# Create MySQL database connection
class EstablishConnection:
    def __init__(self, host="localhost", user="root", password="justdo!t",
                 database="local_data"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def database_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if connection.is_connected():
                return connection
        except Error as e:
            st.error(f"Error: {e}")
        return None

