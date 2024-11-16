import requests
from groq import Groq
import streamlit as st

WEATHER_API_KEY=st.secrets["WEATHER_API_KEY"]  
GROQ_API_KEY=st.secrets["GROQ_API_KEY"]  

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

    chat_completion1 = client.chat.completions.create(
        messages=[
        {
            "role": "user",
            "content": f"what's the weather in London {weather}",
        },{
            "role": "user",
            "content": "Do I need to open the air conditioner right now?",
            }
        ],
        model="llama-3.2-11b-vision-preview",
    )

    chat_completion2 = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": f"what's the weather in London {weather}",
        },{
            "role": "assistant",
            "content": f"{chat_completion1.choices[0].message.content}",
        },
         {
            "role": "user",
            "content": "Based on previously response, Do I need to turn on the air conditioner? Just answer yes or no.",
        }
    ],
    model="llama-3.2-11b-vision-preview",
)
    return chat_completion2.choices[0].message.content
