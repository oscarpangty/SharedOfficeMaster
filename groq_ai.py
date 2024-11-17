import requests
from groq import Groq
import streamlit as st
import base64

WEATHER_API_KEY=st.secrets["WEATHER_API_KEY"]  
GROQ_API_KEY=st.secrets["GROQ_API_KEY"]  
MODEL_NAME="llama-3.2-3b-preview"

def get_weather(query: str) -> list:
    """Search weatherapi to get the current weather"""
    endpoint = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={query}"
    response = requests.get(endpoint)
    data = response.json()

    if data.get("location"):
        return data
    else:
        return "Weather Data Not Found"
    

def get_llm_decision(start_time,end_time,ac_preference,room_id):
    weather=get_weather("London weather now")
    client = Groq(
        api_key=GROQ_API_KEY,
    )
    
    messages = [
        {"role": "user", "content": f"What's the weather in this location {weather}"},
        {"role": "user", "content": f"Here is my preference about air conditioner: {ac_preference}, Do I need to open the air conditioner right now? Don't consider heater. It is usually accepted that people work best at a temperature between 16°C and 24°C"}
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

    messages.append({"role": "assistant", "content": chat_completion2.choices[0].message.content})
    messages.append({
    "role": "user",
    "content": f"Now start the AC. Set temperature based on previous info. "
               f"Set mode between cooling and heating. Remember when current temperature is lower than comfort temperature set heating otherwise cooling. Set fan speed among low, high and auto. If the difference between current temperature and comfort temperature is big set high otherwise low and comfort. Also sets the start time a little bit in advance to give AC enough time to make the room comfortable"
               f"Only output JSON code in this format: "
               f"{{\"device\": {{\"buildingId\": \"12345\", \"deviceId\": \"{room_id}\", "
               f"\"start_time\": \"{start_time}\", \"end_time\": \"{end_time}\", "
               f"\"mode\": \"heating\", \"targetTemp\": 22, \"fanSpeed\": \"high\"}}}} "
               f"no comments. Only change mode, fanSpeed and targetTemp."
    })
                  
    chat_completion3 = client.chat.completions.create(
        messages=messages,
        model=MODEL_NAME
    )

    return (chat_completion1.choices[0].message.content,chat_completion2.choices[0].message.content,chat_completion3.choices[0].message.content)

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
      
def analyze_graph(image_path):
    base64_image = encode_image(image_path)

    client = Groq(
        api_key=GROQ_API_KEY,
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "This is a bubble chart. x-axis is the room size. y-axis is the usage time. Bubble size represents AC energy consumption while different colors represent different rooms. Tell if any room has shown energy consumption anomaly in this bubble chart. Focus on rooms with usually higher energy consumption and give insights such as that one specific room has odd energy consumption pattern please inspect the equipment and the room insulation."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model="llama-3.2-90b-vision-preview",
    )
    response = chat_completion.choices[0].message.content
    return response
