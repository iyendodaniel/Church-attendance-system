import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="View Attendance", layout="wide")
st.title("📋 Attendance Records (Admin View)")

# --- Admin Password ---
correct_code = st.secrets["attendance"]["admin_view_code"]
admin_pass = st.text_input("Enter Admin Passcode", type="password")
if admin_pass != correct_code:
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
        others_count = len(record.get("others_marked", []))
        
        # Main person
        rows.append({
            "#": None,  # Will fill later
            "Name": record["name"],
            "Phone Number": record.get("phone_number", "N/A"),
            "Service": record["service"],
            "Marked For": f"{others_count} people" if others_count > 0 else "-",
            "Timestamp": record["timestamp"]
        })
        
        # People they marked for
        for name in record.get("others_marked", []):
            rows.append({
                "#": None,
                "Name": name,
                "Phone Number": "N/A",
                "Service": record["service"],
                "Marked For": record["name"],
                "Timestamp": record["timestamp"]
            })

    # Create DataFrame
    df = pd.DataFrame(rows)

    # Sort alphabetically & add numbering
    df = df.sort_values(by="Name").reset_index(drop=True)
    df.index += 1
    df.insert(0, "#", df.index)


    st.dataframe(df, use_container_width=True)

    st.markdown(f"**👥 Total Attendance:** {len(df)} people")

    # --- Download as Excel ---
    excel_filename = f"{date_str}-{service_option.replace(' ', '_').lower()}-attendance.xlsx"
    from io import BytesIO
    output = BytesIO()
    df.to_excel(output, index=True, engine="openpyxl")  # Keep numbering
    st.download_button(
        label="📥 Download Attendance (Excel)",
        data=output.getvalue(),
        file_name=excel_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("No attendance records found for this selection.")

