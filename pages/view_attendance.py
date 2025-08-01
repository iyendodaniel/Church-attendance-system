import streamlit as st
import os
import json
from datetime import datetime
import pandas as pd

today_str = datetime.now().strftime("%Y-%m-%d")

first_file = f"data/{today_str}-first.json"
second_file = f"data/{today_str}-second.json"


st.set_page_config(page_title="Admin", layout="centered")
st.title("Admin View")

ADMIN_PASSWORD = "pass123"
user_password = st.text_input("Enter password:", type="password")

if user_password != ADMIN_PASSWORD:
    st.warning("WRONG PASSWORD!")
    st.stop()
else:
    st.success("Correct password")
    service_option = st.radio("Select Service to View:", ["First service", "Second service", "All services"])
    attendance_data = []

    if service_option in ["First service", "All services"] and os.path.exists(first_file):
        with open (first_file, "r") as f:
            attendance_data += json.load(f)

    if service_option in ["Second service", "All services"] and os.path.exists(second_file):
        with open (second_file, "r") as f:
            attendance_data += json.load(f)


    if attendance_data:
        df = pd.DataFrame(attendance_data)
        df["Others Count"] = df["others_marked"].apply(len)

        st.write("### Attendance Records")
        st.dataframe(df[["name", "phone_number", "service", "others_marked", "timestamp"]])

        num_main = len(attendance_data)
        num_others = sum(len(rec["others_marked"]) for rec in attendance_data)
        grand_total = num_main + num_others

        st.success(f"Main Attendances: {num_main}")
        st.success(f"Others marked: {num_others}")
        st.info(f"**Total Attendance:**: {grand_total}")