import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Set up the floorplan
st.title("Shared Office Booking System")
st.image("floorplan.jpeg", caption="Office Floorplan", use_column_width=True)

# Placeholder for availability data
if "bookings" not in st.session_state:
    st.session_state["bookings"] = pd.DataFrame(columns=["Room", "Start Time", "End Time", "Name", "Email"])

# Room Selection
st.header("Book a Room")
room = st.selectbox("Choose a room to book:", ["Meeting Room", "Office 31a", "Office 31b", "Office 30", "Office 32"])

# Time Slot Selection
st.subheader("Choose a Time Slot")
start_time = st.datetime_input("Start Time", datetime.now() + timedelta(hours=1))
end_time = st.datetime_input("End Time", start_time + timedelta(hours=1))

# User Info
st.subheader("Enter Your Details")
name = st.text_input("Your Name")
email = st.text_input("Your Email")

# Check for Conflicts
if st.button("Check Availability"):
    conflicts = st.session_state["bookings"][
        (st.session_state["bookings"]["Room"] == room) &
        (st.session_state["bookings"]["Start Time"] < end_time) &
        (st.session_state["bookings"]["End Time"] > start_time)
    ]

    if not conflicts.empty:
        st.error("The selected room is not available for the chosen time slot.")
    else:
        st.success("The room is available!")

# Confirm Booking
if st.button("Confirm Booking"):
    if name and email:
        new_booking = {
            "Room": room,
            "Start Time": start_time,
            "End Time": end_time,
            "Name": name,
            "Email": email
        }
        st.session_state["bookings"] = st.session_state["bookings"].append(new_booking, ignore_index=True)
        st.success("Booking Confirmed!")
    else:
        st.error("Please fill in all required fields.")

# Display All Bookings
st.header("Current Bookings")
st.write(st.session_state["bookings"])
