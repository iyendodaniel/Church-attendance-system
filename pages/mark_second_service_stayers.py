import streamlit as st
import json
import os
from datetime import datetime

# 📅 Today's date
today_str = datetime.now().strftime("%Y-%m-%d")
DATA_DIR = "./data"
FIRST_SERVICE_FILE = os.path.join(DATA_DIR, f"{today_str}-first.json")
SECOND_SERVICE_FILE = os.path.join(DATA_DIR, f"{today_str}-second.json")

st.title("🔄 Mark 2nd Service Stayers (Others Marked)")

# --- Step 1: Ask for Access Code ---
correct_code = st.secrets["attendance"]["second_mark_code"]
code = st.text_input("Enter access code to continue", type="password")

if code != correct_code:
    st.warning("Access code required.")
    st.stop()

# --- Step 2: Check time is after 11:10 AM ---
now = datetime.now()
if now.hour < 11 or (now.hour == 11 and now.minute < 10):
    st.warning("You can only mark 2nd service stayers after 11:10 AM.")
    st.stop()

# --- Step 3: Load First Service JSON ---
if not os.path.exists(FIRST_SERVICE_FILE):
    st.error("First service data not found.")
    st.stop()

with open(FIRST_SERVICE_FILE, "r") as f:
    first_data = json.load(f)

# --- Step 4: Collect only "others_marked" entries ---
others = []
for entry in first_data:
    if "others_marked" in entry and entry["others_marked"]:
        for other_name in entry["others_marked"]:
            others.append({"name": other_name})

if not others:
    st.info("No 'others marked' attendees found in first service.")
    st.stop()

# --- Step 5: Remove duplicates ---
unique_names = sorted(set(o["name"] for o in others))

# --- Step 6: Multiselect list ---
selected_names = st.multiselect(
    "Select those who stayed for 2nd service",
    unique_names
)

# --- Step 7: Load or create second service file ---
if os.path.exists(SECOND_SERVICE_FILE):
    with open(SECOND_SERVICE_FILE, "r") as f:
        second_data = json.load(f)
else:
    second_data = []

# --- Step 8: Save selections ---
if st.button("✅ Mark Selected as 2nd Service Attendees"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entries = []

    for name in selected_names:
        new_entry = {
            "name": name,
            "phone_number": "N/A",
            "marked_by": "Daniel",
            "timestamp": timestamp
        }
        if not any(d["name"] == new_entry["name"] for d in second_data):
            second_data.append(new_entry)
            new_entries.append(new_entry)

    with open(SECOND_SERVICE_FILE, "w") as f:
        json.dump(second_data, f, indent=4)

    st.success(f"{len(new_entries)} person(s) added to Second Service!")
