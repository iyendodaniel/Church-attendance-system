import streamlit as st
import os
import json
from datetime import datetime, time
import pytz

# 📅 Local timezone
lagos_tz = pytz.timezone("Africa/Lagos")
now = datetime.now(lagos_tz)

today_str = now.strftime("%Y-%m-%d")
timestamp_str = now.isoformat()

# 🔐 Access Code
form_access_code = st.text_input("Enter Access Code:", type="password")
correct_code = st.secrets["attendance"]["access_code"]

if form_access_code != correct_code:
    st.error("Invalid access code. Please contact admin.")
    st.stop()

# --- Time boundaries ---
start_choice = time(7, 20)       # 7:20 AM
end_choice = time(10, 9)         # 10:09 AM
start_auto_second = time(10, 10) # 10:10 AM
end_auto_second = time(12, 59)   # 12:59 PM
close_attendance = time(14, 0)   # 2:00 PM

current_time = now.time()

# Service selection logic based on time
if current_time < start_choice:
    st.warning("Attendance opens at 7:20 AM.")
    st.stop()
elif current_time <= end_choice:
    # Show radio for choice
    service_selection = st.radio(
        "Select Service",
        ["First Service", "Second Service", "Both"],
        horizontal=True
    )
elif current_time <= end_auto_second:
    st.info("Automatically marking for Second Service.")
    service_selection = "Second Service"
elif current_time < close_attendance:
    st.info("Automatically marking for Second Service (only service open now).")
    service_selection = "Second Service"
else:
    st.warning("Attendance is now closed.")
    st.stop()

# Form
with st.form(key="inviter_info_form"):
    user_name = st.text_input("Enter your Full Name:")
    phone_number_input = st.text_input("Enter your Phone number:")
    phone_number = phone_number_input.strip()
    other_names = st.text_area("Enter the full names of others you want to mark (one name per line):")

    submitted = st.form_submit_button("Submit")

    if submitted:
        all_valid = True

        # Determine files based on choice
        if service_selection == "First Service":
            filename = f"data/{today_str}-first.json"
            other_service_file = f"data/{today_str}-second.json"
        elif service_selection == "Second Service":
            filename = f"data/{today_str}-second.json"
            other_service_file = f"data/{today_str}-first.json"
        else:  # Both services
            filename_first = f"data/{today_str}-first.json"
            filename_second = f"data/{today_str}-second.json"
            other_service_file = None

        # Load data for single service
        if service_selection in ["First Service", "Second Service"]:
            attendance_data = []
            if os.path.exists(filename):
                with open(filename, "r") as file:
                    attendance_data = json.load(file)

            # Check if already in other service
            if os.path.exists(other_service_file):
                with open(other_service_file, "r") as f:
                    other_service_data = json.load(f)
                    for record in other_service_data:
                        if record["phone_number"] == phone_number:
                            st.error(f"You already marked attendance in the other service: {record['service']}")
                            all_valid = False

        # Validate name
        if not user_name or len(user_name.strip().split()) < 2:
            st.warning("Please input your Full name!")
            all_valid = False

        # Validate phone number
        if not phone_number:
            st.warning("Please input your phone number!")
            all_valid = False
        elif phone_number.startswith("+"):
            if not (len(phone_number) == 14 and phone_number[1:].isdigit()):
                st.error("Phone number starting with '+' must be 14 characters and digits after '+'.")
                all_valid = False
        else:
            if not (len(phone_number) == 11 and phone_number.isdigit()):
                st.error("Phone number without '+' must be 11 digits.")
                all_valid = False

        # Check duplicates in current service
        if service_selection in ["First Service", "Second Service"]:
            for record in attendance_data:
                if record["phone_number"] == phone_number:
                    st.error("You have already marked attendance today.")
                    all_valid = False
                    break

        # Validate "others marked"
        lines = other_names.split("\n")
        clean_names = [line.strip() for line in lines if line.strip()]
        invalid_names = [name for name in clean_names if len(name.split()) < 2]
        if invalid_names:
            st.error(f"Please enter full names (at least two words) for: {', '.join(invalid_names)}")
            all_valid = False

        # Save attendance
        if all_valid:
            if service_selection == "Both":
                for file_name, svc in [(filename_first, "First Service"), (filename_second, "Second Service")]:
                    data = []
                    if os.path.exists(file_name):
                        with open(file_name, "r") as f:
                            data = json.load(f)
                    new_record = {
                        "name": user_name,
                        "phone_number": phone_number,
                        "service": svc,
                        "others_marked": clean_names,
                        "timestamp": timestamp_str,
                    }
                    data.append(new_record)
                    with open(file_name, "w") as f:
                        json.dump(data, f, indent=4)
                st.success("Marked for both services successfully!")
            else:
                new_record = {
                    "name": user_name,
                    "phone_number": phone_number,
                    "service": service_selection,
                    "others_marked": clean_names,
                    "timestamp": timestamp_str,
                }
                attendance_data.append(new_record)
                with open(filename, "w") as f:
                    json.dump(attendance_data, f, indent=4)
                st.success(f"Marked for {service_selection} successfully!")
