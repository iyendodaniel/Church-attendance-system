import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="View Attendance", layout="wide")
st.title("📊 Attendance Viewer")

# Select date and service
today_str = datetime.now().strftime("%Y-%m-%d")
selected_date = st.date_input("Select Date", datetime.now()).strftime("%Y-%m-%d")

service_option = st.radio("Select Service to View:", ["First Service", "Second Service"])

# Map to filename
filename = f"data/{selected_date}-first.json" if service_option == "First Service" else f"data/{selected_date}-second.json"

if not os.path.exists(filename):
    st.warning("No attendance data found for the selected service and date.")
    st.stop()

# Load attendance data
with open(filename, "r") as file:
    attendance_data = json.load(file)

# Build DataFrame
df_rows = []
for rec in attendance_data:
    df_rows.append({
        "Full Name": rec["name"],
        "Phone Number": rec["phone_number"],
        "Others Marked": ", ".join(sorted(rec["others_marked"])),  # sort within cell
        "Timestamp": rec["timestamp"]
    })

df = pd.DataFrame(df_rows)

# Sort all by Full Name (alphabetically)
df = df.sort_values(by="Full Name")

# Show table
st.subheader("📋 Attendance Table")
st.dataframe(df, use_container_width=True)

# Total count
num_main = len(df)
num_others = sum(len(rec["others_marked"]) for rec in attendance_data)
total_present = num_main + num_others

st.success(f"✅ Total People Marked Present: {total_present} ({num_main} main + {num_others} others)")

# Download Excel
excel_buffer = BytesIO()
df.to_excel(excel_buffer, index=False)
excel_buffer.seek(0)

st.download_button(
    label="📥 Download as Excel",
    data=excel_buffer,
    file_name=f"{selected_date}-{service_option.lower().replace(' ', '_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
