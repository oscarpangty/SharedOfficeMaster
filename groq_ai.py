import requests
from groq import Groq
import streamlit as st
import base64

WEATHER_API_KEY=st.secrets["WEATHER_API_KEY"]  
GROQ_API_KEY=st.secrets["GROQ_API_KEY"]  
MODEL_NAME="llama-3.2-11b-vision-preview"

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
    client = Groq(
        api_key=GROQ_API_KEY,
    )
    
    messages = [
        {"role": "user", "content": f"What's the weather in this location {weather}"},
        {"role": "user", "content": f"Here is my preference about air conditioner: {ac_preference}, Do I need to open the air conditioner right now?"}
    ]

    chat_completion1 = client.chat.completions.create(
        messages=messages,
        model=MODEL_NAME
    )

    messages.append({"role": "assistant", "content": chat_completion1.choices[0].message.content})
    messages.append({"role": "user", "content": "Based on the previous response, do I need to turn on the air conditioner? Just answer Yes or No."})

    chat_completion2 = client.chat.completions.create(
        messages=messages,
        model=MODEL_NAME
    )

    return chat_completion1.choices[0].message.content

def analyze_graph(image_data):
    response = "This is a sample response from the LLM analyzing the bubble chart."
    return response
