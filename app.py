import streamlit as st
import requests
import re
import google.generativeai as genai

# ---------------- CONFIG ----------------
# Using st.secrets.get needed to avoid immediate crash if secrets aren't set yet during first run/setup
OPENWEATHER_KEY = st.secrets.get("957b3f2f18bc0bec42969af03f87fd1d")
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY")

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

st.set_page_config(page_title="Weather Chatbot", page_icon="🌦️")
st.title("🌦️ Smart Weather Chatbot")

# Check for secrets before proceeding
if not OPENWEATHER_KEY or not GEMINI_KEY:
    st.error("🚨 API Keys missing! Please set `OPENWEATHER_API_KEY` and `GEMINI_API_KEY` in `.streamlit/secrets.toml`.")
    st.stop()

genai.configure(api_key=GEMINI_KEY)
# Initialize model with safety settings if needed, for now using default
model = genai.GenerativeModel("gemini-2.0-flash")

# ---------------- FUNCTIONS ----------------
def extract_city(text):
    match = re.search(r"in ([a-zA-Z ]+)", text.lower())
    return match.group(1).title() if match else None

def get_weather(city):
    params = {
        "q": city,
        "appid": OPENWEATHER_KEY,
        "units": "metric"
    }
    try:
        r = requests.get(WEATHER_URL, params=params)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        st.error(f"Error fetching weather: {e}")
        return None

def format_with_gemini(weather_json):
    prompt = f"""
You are a helpful weather assistant.
Use ONLY the data below. Do not add new facts.

City: {weather_json['name']}
Temperature: {weather_json['main']['temp']}°C
Feels Like: {weather_json['main']['feels_like']}°C
Humidity: {weather_json['main']['humidity']}%
Condition: {weather_json['weather'][0]['description']}

Respond naturally and briefly like a human assistant.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error communicating with AI: {e}"

def chatbot(user_input):
    city = extract_city(user_input)
    if not city:
        return "Ask like: **What's the weather in Karachi?**"

    weather = get_weather(city)
    if not weather:
        return f"I couldn't find weather data for **{city}**."

    return format_with_gemini(weather)

# ---------------- UI ----------------
user_input = st.text_input("Ask about the weather")

if user_input:
    with st.spinner("Fetching weather..."):
        reply = chatbot(user_input)
        st.markdown(reply)
