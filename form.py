import streamlit as st
import os
import json
from datetime import datetime

now = datetime.now()
hour = now.hour
today_str = now.strftime("%Y-%m-%d")  
timestamp_str = now.isoformat()         # for record timestamp


st.set_page_config(page_title="Attendance", layout="centered")
st.title("Mark attendance")
ACCESS_CODE = "ATTEND2025"
access_code = st.text_input("Enter access code to proceed:")

if access_code != ACCESS_CODE:
    st.warning("Please enter a valid access code to mark attendance.")
    st.stop()


with st.form(key="inviter_info_form"):
    user_name = st.text_input("Enter your Full Name:")
    phone_number_input = st.text_input("Enter your Phone number:")
    phone_number = phone_number_input.strip()
    other_names = st.text_area("Enter the full names of others you want to mark (one name per line):")
    submitted = st.form_submit_button("Submit")

    if submitted:
        all_valid = True
        # Detect service type
        if hour < 8:
            st.error("Attendance hasn't started yet.")
            st.stop()
        elif hour < 10:
            service = "First Service"
            other_service_file = f"data/{today_str}-second.json"
        elif hour < 13:
            service = "Second Service"
            other_service_file = f"data/{today_str}-first.json"
        else:
            st.error("Attendance marking is closed.")
            st.stop()

        # Load current service file
        filename = f"data/{today_str}-first.json" if service == "First Service" else f"data/{today_str}-second.json"
        attendance_data = []
        if os.path.exists(filename):
            with open(filename, "r") as file:
                attendance_data = json.load(file)

        # 🔒 Load and check the other service file
        if os.path.exists(other_service_file):
            with open(other_service_file, "r") as f:
                other_service_data = json.load(f)
                for record in other_service_data:
                    if record["phone_number"] == phone_number:
                        st.error(f"You already marked attendance in the other service: {record['service']}")
                        all_valid = False


        if user_name:
            if len(user_name.strip().split()) < 2:
                st.warning("Plese input your Full name!")
                all_valid = False
            else:
                pass
        else:
            st.warning("Plese input your Full name!")
            all_valid = False
        if not phone_number:
            st.warning("Plese input your phone number!")
            valid_phone = False
            all_valid = False
        elif phone_number.startswith("+"):
            if len(phone_number) == 14 and phone_number[1:].isdigit():
                valid_phone = True
            else:
                st.error("Phone number starting with '+' must be 14 characters and digits after '+'.")
                valid_phone = False
                all_valid = False
        else:
            if len(phone_number) == 11 and phone_number.isdigit():
                valid_phone = True
            else:
                st.error("Phone number without '+' must be 11 digits.")
                valid_phone = False
                all_valid = False
        for record in attendance_data:
            if record["phone_number"] == phone_number:
                st.error("You have already marked attendance today.")
                all_valid = False
                break
        lines = other_names.split("\n")
        clean_names = [line.strip() for line in lines if line.strip()]
        invalid_names = [name for name in clean_names if len(name.split()) < 2]
        if invalid_names:
            st.error(f"Please enter full names (at least two words) for: {', '.join(invalid_names)}")
            all_valid = False
        else:
            st.success("All names look good!")

        if all_valid == True:
            new_record = {
                "name": user_name,
                "phone_number": phone_number,
                "service": service,
                "others_marked": clean_names,
                "timestamp": timestamp_str,
            }
            attendance_data.append(new_record)
            with open(filename, "w") as file:
                json.dump(attendance_data, file, indent=4)
            st.success("Done successfully!")