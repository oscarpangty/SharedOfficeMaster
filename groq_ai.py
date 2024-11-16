import requests
from groq import Groq
import streamlit as st

WEATHER_API_KEY=st.secrets["WEATHER_API_KEY"]  
def get_weather(query: str) -> list:
    """Search weatherapi to get the current weather"""
    endpoint = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={query}"
    response = requests.get(endpoint)
    data = response.json()

    if data.get("location"):
        return data
    else:
        return "Weather Data Not Found"


def get_llm_decision(start_time,end_time,ac_preference):
  weather=get_weather("London weather now")
  return "Yes. Fine "+ weather
