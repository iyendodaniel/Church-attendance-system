import streamlit as st
import os
import json
from datetime import datetime

# Current time
now = datetime.now()
hour = now.hour
minute = now.minute
today_str = now.strftime("%Y-%m-%d")
timestamp_str = now.isoformat()

# Access code
form_access_code = st.text_input("Enter Access Code:", type="password")
correct_code = st.secrets["attendance"]["access_code"]

if form_access_code != correct_code:
    st.error("Invalid access code. Please contact admin.")
    st.stop()

with st.form(key="inviter_info_form"):
    user_name = st.text_input("Enter your Full Name:")
    phone_number_input = st.text_input("Enter your Phone number:")
    phone_number = phone_number_input.strip()
    other_names = st.text_area("Enter the full names of others you want to mark (one name per line):")

    # Time-based service logic
    if (hour == 7 and minute >= 20) or (8 <= hour < 10) or (hour == 10 and minute <= 9):
        # Between 07:20 and 10:09 → show all options
        service = st.radio(
            "Select Service",
            ["First Service", "Second Service", "Both Services"],
            horizontal=True
        )
    else:
        # From 10:10 onward → auto select Second Service
        service = "Second Service"
        st.info("⏰ It's after 10:10 AM — automatically marking for Second Service.")

    submitted = st.form_submit_button("Submit")

    if submitted:
        all_valid = True

        # Determine files
        if service == "First Service":
            filename = f"data/{today_str}-first.json"
        elif service == "Second Service":
            filename = f"data/{today_str}-second.json"
        else:  # Both Services
            filename_first = f"data/{today_str}-first.json"
            filename_second = f"data/{today_str}-second.json"

        # Validation
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

        # Process other names
        lines = other_names.split("\n")
        clean_names = [line.strip() for line in lines if line.strip()]
        invalid_names = [name for name in clean_names if len(name.split()) < 2]
        if invalid_names:
            st.error(f"Please enter full names (at least two words) for: {', '.join(invalid_names)}")
            all_valid = False

        if all_valid:
            new_record = {
                "name": user_name,
                "phone_number": phone_number,
                "service": service,
                "others_marked": clean_names,
                "timestamp": timestamp_str,
            }

            if service == "Both Services":
                # Save to first
                data_first = []
                if os.path.exists(filename_first):
                    with open(filename_first, "r") as f:
                        data_first = json.load(f)
                data_first.append(new_record)
                with open(filename_first, "w") as f:
                    json.dump(data_first, f, indent=4)

                # Save to second
                data_second = []
                if os.path.exists(filename_second):
                    with open(filename_second, "r") as f:
                        data_second = json.load(f)
                data_second.append(new_record)
                with open(filename_second, "w") as f:
                    json.dump(data_second, f, indent=4)

            else:
                # Save to single service file
                data = []
                if os.path.exists(filename):
                    with open(filename, "r") as f:
                        data = json.load(f)
                data.append(new_record)
                with open(filename, "w") as f:
                    json.dump(data, f, indent=4)

            st.success("Attendance marked successfully!")
