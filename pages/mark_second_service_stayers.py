import streamlit as st
import json
import os
from datetime import datetime

# 📁 Paths
DATA_DIR = "./data"
FIRST_SERVICE_FILE = os.path.join(DATA_DIR, "first_service.json")
SECOND_SERVICE_FILE = os.path.join(DATA_DIR, "second_service.json")

# 🔐 Access Code
second_service_access_code = "mark"  # Change this to something secure

st.title("🔄 Mark 2nd Service Stayers (Non-Phone Users)")

# --- Step 1: Ask for Access Code ---
code = st.text_input("Enter access code to continue", type="password")

if code != second_service_access_code:
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

# --- Step 4: Get "others_marked" entries only ---
others = [entry for entry in first_data if entry.get("marked_by") == "others_marked"]

if not others:
    st.info("No non-phone users found in first service data.")
    st.stop()

# --- Step 5: Let Daniel select who stayed ---
names = [f"{entry['name']} ({entry['phone']})" for entry in others]
selected = st.multiselect("Select those who stayed for 2nd service", names)

# --- Step 6: Load or create 2nd service data ---
if os.path.exists(SECOND_SERVICE_FILE):
    with open(SECOND_SERVICE_FILE, "r") as f:
        second_data = json.load(f)
else:
    second_data = []

# --- Step 7: Add selected names to 2nd service JSON under Daniel ---
if st.button("✅ Mark Selected as 2nd Service Attendees"):
    new_entries = []
    for entry in others:
        full = f"{entry['name']} ({entry['phone']})"
        if full in selected:
            new_entry = {
                "name": entry["name"],
                "phone": entry["phone"],
                "marked_by": "Daniel",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            second_data.append(new_entry)
            new_entries.append(new_entry)

    # Save updated second service JSON
    with open(SECOND_SERVICE_FILE, "w") as f:
        json.dump(second_data, f, indent=4)

    st.success(f"{len(new_entries)} person(s) added to Second Service!")
