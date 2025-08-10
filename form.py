import streamlit as st
import os
import json
from datetime import datetime

now = datetime.now()
today_str = now.strftime("%Y-%m-%d")  
timestamp_str = now.isoformat()  # precise record time

# Access Code
form_access_code = st.text_input("Enter Access Code:", type="password")
correct_code = st.secrets["attendance"]["access_code"]

if form_access_code != correct_code:
    st.error("Invalid access code. Please contact admin.")
    st.stop()

# Select service BEFORE submitting
service = st.radio(
    "Select Service",
    ["First Service", "Second Service"],
    horizontal=True
)

# Determine file paths
if service == "First Service":
    filename = f"data/{today_str}-first.json"
    other_service_file = f"data/{today_str}-second.json"
else:
    filename = f"data/{today_str}-second.json"
    other_service_file = f"data/{today_str}-first.json"

# Load attendance for current service
attendance_data = []
if os.path.exists(filename):
    with open(filename, "r") as file:
        attendance_data = json.load(file)

# Load attendance for other service
other_service_data = []
if os.path.exists(other_service_file):
    with open(other_service_file, "r") as f:
        other_service_data = json.load(f)

# Form
with st.form(key="inviter_info_form"):
    user_name = st.text_input("Enter your Full Name:")
    phone_number_input = st.text_input("Enter your Phone number:")
    phone_number = phone_number_input.strip()
    other_names = st.text_area("Enter full names of others you want to mark (one per line):")
    submitted = st.form_submit_button("Submit")

    if submitted:
        all_valid = True

        # Prevent marking in both services
        for record in other_service_data:
            if record["phone_number"] == phone_number:
                st.error(f"You already marked attendance in the other service: {record['service']}")
                all_valid = False

        # Validate full name
        if not user_name or len(user_name.strip().split()) < 2:
            st.warning("Please input your full name!")
            all_valid = False

        # Validate phone number
        if not phone_number:
            st.warning("Please input your phone number!")
            all_valid = False
        elif phone_number.startswith("+"):
            if len(phone_number) != 14 or not phone_number[1:].isdigit():
                st.error("Phone number starting with '+' must be 14 characters and digits after '+'.")
                all_valid = False
        else:
            if len(phone_number) != 11 or not phone_number.isdigit():
                st.error("Phone number without '+' must be 11 digits.")
                all_valid = False

        # Prevent double marking in same service
        for record in attendance_data:
            if record["phone_number"] == phone_number:
                st.error("You have already marked attendance today in this service.")
                all_valid = False
                break

        # Validate others' names
        clean_names = [name.strip() for name in other_names.split("\n") if name.strip()]
        invalid_names = [name for name in clean_names if len(name.split()) < 2]
        if invalid_names:
            st.error(f"Please enter full names for: {', '.join(invalid_names)}")
            all_valid = False

        if all_valid:
            # Add main person
            new_record = {
                "name": user_name,
                "phone_number": phone_number,
                "service": service,
                "marked_by": None,  # self
                "timestamp": timestamp_str,
            }
            attendance_data.append(new_record)

            # Add others marked
            for name in clean_names:
                attendance_data.append({
                    "name": name,
                    "phone_number": None,
                    "service": service,
                    "marked_by": user_name,
                    "timestamp": timestamp_str,
                })

            # Save file
            with open(filename, "w") as file:
                json.dump(attendance_data, file, indent=4)

            st.success("Attendance marked successfully!")
