import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from groq_ai import get_llm_decision

# Initialize session state for time inputs
if "start_time" not in st.session_state:
    st.session_state["start_time"] = (datetime.now() + timedelta(hours=1)).time()
if "end_time" not in st.session_state:
    st.session_state["end_time"] = (datetime.now() + timedelta(hours=2)).time()

# Set up the floorplan
st.title("Shared Office Booking System")
st.image("floorplan.jpeg", caption="Office Floorplan", use_column_width=True)

# Placeholder for availability data
if "bookings" not in st.session_state:
    st.session_state["bookings"] = pd.DataFrame(columns=["Room", "Start Time", "End Time", "Name", "Email", "AC On"])

# Room Selection
st.header("Book a Room")
room = st.selectbox("Choose a room to book:", ["Meeting Room", "Office 31a", "Office 31b", "Office 30", "Office 32"])

# Date and Time Slot Selection
st.subheader("Choose a Date and Time Slot")
booking_date = st.date_input("Select a Date", datetime.now().date())

# Persist time inputs using session state
start_time = st.time_input("Start Time", st.session_state["start_time"], key="start_time_input")
end_time = st.time_input("End Time", st.session_state["end_time"], key="end_time_input")

# Update session state whenever time inputs change
st.session_state["start_time"] = start_time
st.session_state["end_time"] = end_time
st.session_state["llm_feedback"]="System is operating normally. All rooms are adequately managed."
# Combine date and time into datetime objects
start_datetime = datetime.combine(booking_date, start_time)
end_datetime = datetime.combine(booking_date, end_time)

# User Info
st.subheader("Enter Your Details")
name = st.text_input("Your Name")
email = st.text_input("Your Email")

# Air Conditioner Toggle
st.subheader("Air Conditioner Preference")
ac_preference = st.radio(
    "Select your preference:",
    ["I want air conditioner", "No air conditioner"]
)
print(ac_preference)
# Check for Conflicts
if st.button("Check Availability"):
    conflicts = st.session_state["bookings"][
        (st.session_state["bookings"]["Room"] == room) &
        (st.session_state["bookings"]["Start Time"] < end_datetime) &
        (st.session_state["bookings"]["End Time"] > start_datetime)
    ]

    if not conflicts.empty:
        st.error("The selected room is not available for the chosen time slot.")
    else:
        st.success("The room is available!")

# Confirm Booking
if st.button("Confirm Booking"):
    if name and email:
        llm_decision = get_llm_decision(start_time, end_time, ac_preference)
        st.session_state["llm_feedback"] = llm_decision
        ac_on = "Yes" if "Yes" in llm_decision else "No"
        new_booking = pd.DataFrame([{
            "Room": room,
            "Start Time": start_datetime,
            "End Time": end_datetime,
            "Name": name,
            "Email": email,
            "AC On": "Yes" if ac_on=="Yes" else "No"
        }])
        st.session_state["bookings"] = pd.concat([st.session_state["bookings"], new_booking], ignore_index=True)
        st.success("Booking Confirmed!")
    else:
        st.error("Please fill in all required fields.")

# Display All Bookings
st.header("Current Bookings")
if not st.session_state["bookings"].empty:
    st.dataframe(
        st.session_state["bookings"],
        use_container_width=True,
    )
else:
    st.write("No bookings yet.")

# Feedback Textbox for AI Management System
st.subheader("AI Management Feedback")
st.text_area("Feedback from AI Management System", value=st.session_state["llm_feedback"], height=100, disabled=True)

st.write(f"You selected: {ac_preference}")


