import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="View Attendance", layout="wide")
st.title("📋 Attendance Records (Admin View)")

# --- Admin Password ---
admin_pass = st.text_input("Enter Admin Passcode", type="password")
if admin_pass != "teens":
    st.warning("Enter the correct admin passcode to view attendance.")
    st.stop()

# --- Service selection ---
service_option = st.radio("Select Service to View:", ["First Service", "Second Service", "All Services"])

# --- Select Date ---
date_option = st.date_input("Pick a Date", datetime.today())
date_str = date_option.strftime("%Y-%m-%d")

# --- Load data files ---
def load_data(date_str, service):
    filename = f"data/{date_str}-{'first' if service == 'First Service' else 'second'}.json"
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file), filename
    else:
        return [], filename

if service_option in ["First Service", "Second Service"]:
    data, file_path = load_data(date_str, service_option)
else:
    first_data, first_file = load_data(date_str, "First Service")
    second_data, second_file = load_data(date_str, "Second Service")
    data = first_data + second_data
    file_path = None  # not relevant here

# --- Process and Display Data ---
if data:
    rows = []
    for record in data:
        rows.append({
            "Name": record["name"],
            "Phone Number": record["phone_number"],
            "Service": record["service"],
            "Marked For": ", ".join(record["others_marked"]),
            "Timestamp": record["timestamp"]
        })
        for name in record["others_marked"]:
            rows.append({
                "Name": name,
                "Phone Number": "N/A",
                "Service": record["service"],
                "Marked For": "—",
                "Timestamp": record["timestamp"]
            })

    df = pd.DataFrame(rows)
    df = df.sort_values(by="Name")  # Sort alphabetically

    st.dataframe(df, use_container_width=True)

    st.markdown(f"**👥 Total Attendance:** {len(df)} people")

    # --- Download as Excel ---
    excel_filename = f"{date_str}-{service_option.replace(' ', '_').lower()}-attendance.xlsx"
    excel_bytes = df.to_excel(index=False, engine="openpyxl")

    st.download_button(
        label="📥 Download Attendance (Excel)",
        data=excel_bytes,
        file_name=excel_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("No attendance records found for this selection.")
