import streamlit as st
import os
import json
from datetime import datetime
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

# --- Time access control ---
if now.hour < 7 or (now.hour == 7 and now.minute < 20):
    st.warning("Attendance opens at 7:20 AM.")
    st.stop()

if now.hour >= 12:
    st.warning("Attendance is now closed.")
    st.stop()

# --- Form ---
with st.form(key="inviter_info_form"):
    user_name = st.text_input("Enter your Full Name:")
    phone_number_input = st.text_input("Enter your Phone number:")
    phone_number = phone_number_input.strip()
    other_names = st.text_area("Enter the full names of others you want to mark (one name per line):")

    # Service selection logic
    if now.hour < 10 or (now.hour == 10 and now.minute <= 9):
        service = st.radio(
            "Select Service",
            ["First Service", "Second Service", "Both"],
            horizontal=True
        )
    else:
        service = "Second Service"  # Automatically assign

    submitted = st.form_submit_button("Submit")

    if submitted:
        all_valid = True

        # Determine files based on service
        if service == "First Service":
            filename = f"data/{today_str}-first.json"
            other_service_file = f"data/{today_str}-second.json"
        elif service == "Second Service":
            filename = f"data/{today_str}-second.json"
            other_service_file = f"data/{today_str}-first.json"
        else:  # Both
            filename_first = f"data/{today_str}-first.json"
            filename_second = f"data/{today_str}-second.json"
            other_service_file = None

        # Load current data
        if service in ["First Service", "Second Service"]:
            attendance_data = []
            if os.path.exists(filename):
                with open(filename, "r") as file:
                    attendance_data = json.load(file)

            # Check if already marked in other service
            if os.path.exists(other_service_file):
                with open(other_service_file, "r") as f:
                    other_service_data = json.load(f)
                    for record in other_service_data:
                        if record["phone_number"] == phone_number and phone_number != "":
                            st.error(f"You already marked attendance in the other service: {record['service']}")
                            all_valid = False

        # --- Validation ---
        if not user_name or len(user_name.strip().split()) < 2:
            st.warning("Please input your Full name!")
            all_valid = False

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

        # Prevent duplicates in same service
        if service in ["First Service", "Second Service"]:
            for record in attendance_data:
                if phone_number != "" and record["phone_number"] == phone_number:
                    st.error("You have already marked attendance today.")
                    all_valid = False
                    break

        # Validate others' names
        lines = other_names.split("\n")
        clean_names = [line.strip() for line in lines if line.strip()]
        invalid_names = [name for name in clean_names if len(name.split()) < 2]
        if invalid_names:
            st.error(f"Please enter full names (at least two words) for: {', '.join(invalid_names)}")
            all_valid = False

        # --- Save Data ---
        if all_valid:
            if service == "Both":
                for file_name, svc in [(filename_first, "First Service"), (filename_second, "Second Service")]:
                    data = []
                    if os.path.exists(file_name):
                        with open(file_name, "r") as f:
                            data = json.load(f)

                    # Save main user
                    data.append({
                        "name": user_name,
                        "phone_number": phone_number,
                        "service": svc,
                        "marked_by": "self",
                        "timestamp": timestamp_str,
                    })

                    # Save "others marked" as separate entries
                    for other_name in clean_names:
                        data.append({
                            "name": other_name,
                            "phone_number": "",
                            "service": svc,
                            "marked_by": "others_marked",
                            "timestamp": timestamp_str,
                        })

                    with open(file_name, "w") as f:
                        json.dump(data, f, indent=4)

                st.success("Marked for both services successfully!")

            else:
                # Single service
                if os.path.exists(filename):
                    with open(filename, "r") as f:
                        attendance_data = json.load(f)
                else:
                    attendance_data = []

                # Save main user
                attendance_data.append({
                    "name": user_name,
                    "phone_number": phone_number,
                    "service": service,
                    "marked_by": "self",
                    "timestamp": timestamp_str,
                })

                # Save "others marked" separately
                for other_name in clean_names:
                    attendance_data.append({
                        "name": other_name,
                        "phone_number": "",
                        "service": service,
                        "marked_by": "others_marked",
                        "timestamp": timestamp_str,
                    })

                with open(filename, "w") as f:
                    json.dump(attendance_data, f, indent=4)

                st.success(f"Marked for {service} successfully!")
