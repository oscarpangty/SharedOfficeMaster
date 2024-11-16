import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from groq_ai import get_llm_decision
import matplotlib.pyplot as plt

# Initialize session state
if "start_time" not in st.session_state:
    st.session_state["start_time"] = (datetime.now() + timedelta(hours=1)).time()
if "end_time" not in st.session_state:
    st.session_state["end_time"] = (datetime.now() + timedelta(hours=2)).time()
if "llm_feedback" not in st.session_state:
    st.session_state["llm_feedback"] = "System is operating normally. All rooms are adequately managed."
if "bookings" not in st.session_state:
    st.session_state["bookings"] = pd.DataFrame(columns=["Room", "Start Time", "End Time", "Name", "Email", "AC On"])
if "energy_data" not in st.session_state:
    st.session_state["energy_data"] = {"Meeting Room": 0, "Office 31a": 0, "Office 31b": 0, "Office 30": 0, "Office 32": 0}

# Room sizes (preset)
room_sizes = {
    "Meeting Room": 50,  # in square meters
    "Office 31a": 30,
    "Office 31b": 25,
    "Office 30": 20,
    "Office 32": 35,
}

# Page Navigation
page = st.sidebar.radio("Navigate", ["Booking System", "Room Analysis"])

if page == "Booking System":
    # Booking System Page
    st.title("Shared Office Booking System")
    st.image("floorplan.jpeg", caption="Office Floorplan", use_column_width=True)

    # Room Selection
    st.header("Book a Room")
    room = st.selectbox("Choose a room to book:", list(room_sizes.keys()))

    # Date and Time Slot Selection
    st.subheader("Choose a Date and Time Slot")
    booking_date = st.date_input("Select a Date", datetime.now().date())
    start_time = st.time_input("Start Time", st.session_state["start_time"], key="start_time_input")
    end_time = st.time_input("End Time", st.session_state["end_time"], key="end_time_input")
    st.session_state["start_time"] = start_time
    st.session_state["end_time"] = end_time

    # Combine date and time into datetime objects
    start_datetime = datetime.combine(booking_date, start_time)
    end_datetime = datetime.combine(booking_date, end_time)

    # User Info
    st.subheader("Enter Your Details")
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")

    # Air Conditioner Preference
    st.subheader("Air Conditioner Preference")
    ac_preference = st.radio(
        "Select your preference:",
        ["I want air conditioner", "No air conditioner"]
    )

    # Check Availability
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
                "AC On": ac_on
            }])
            st.session_state["bookings"] = pd.concat([st.session_state["bookings"], new_booking], ignore_index=True)
            st.success("Booking Confirmed!")
        else:
            st.error("Please fill in all required fields.")

    # Display Bookings
    st.header("Current Bookings")
    if not st.session_state["bookings"].empty:
        st.dataframe(st.session_state["bookings"], use_container_width=True)
    else:
        st.write("No bookings yet.")

    # Feedback Textbox
    st.subheader("AI Management Feedback")
    st.text_area("Feedback from AI Management System", value=st.session_state["llm_feedback"], height=100, disabled=True)

elif page == "Room Analysis":
    # Room Analysis Page
    st.title("Room Analysis")

    # Input energy consumption manually
    st.subheader("Input Energy Consumption (kWh)")
    for room in room_sizes.keys():
        current_energy = float(st.session_state["energy_data"][room])
        energy = st.number_input(f"{room}", value=current_energy, step=1.0)
        st.session_state["energy_data"][room] = energy

    # Calculate total booked time per room
    usage_times = {room: 0 for room in room_sizes.keys()}
    for _, booking in st.session_state["bookings"].iterrows():
        room = booking["Room"]
        if pd.notna(booking["Start Time"]) and pd.notna(booking["End Time"]):
            usage_times[room] += (booking["End Time"] - booking["Start Time"]).seconds / 3600  # convert to hours

    # Analysis Data
    analysis_data = pd.DataFrame({
        "Room": list(room_sizes.keys()),
        "Size (m²)": list(room_sizes.values()),
        "Usage Time (hours)": [usage_times[room] for room in room_sizes.keys()],
        "Energy Consumption (kWh)": [st.session_state["energy_data"][room] for room in room_sizes.keys()]
    })

    # Display Analysis Data
    st.subheader("Analysis Data")
    st.dataframe(analysis_data)

    # Charts
    st.subheader("Charts")

    # Room Size vs Energy Consumption
    fig1, ax1 = plt.subplots()
    ax1.bar(analysis_data["Room"], analysis_data["Size (m²)"])
    ax1.set_xlabel("Room")
    ax1.set_ylabel("Size (m²)")
    ax1.set_title("Room Sizes")
    st.pyplot(fig1)

    # Usage Time
    fig2, ax2 = plt.subplots()
    ax2.bar(analysis_data["Room"], analysis_data["Usage Time (hours)"], color="orange")
    ax2.set_xlabel("Room")
    ax2.set_ylabel("Usage Time (hours)")
    ax2.set_title("Usage Time by Room")
    st.pyplot(fig2)

    # Energy Consumption
    fig3, ax3 = plt.subplots()
    ax3.bar(analysis_data["Room"], analysis_data["Energy Consumption (kWh)"], color="green")
    ax3.set_xlabel("Room")
    ax3.set_ylabel("Energy Consumption (kWh)")
    ax3.set_title("Energy Consumption by Room")
    st.pyplot(fig3)

