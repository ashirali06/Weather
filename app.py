import streamlit as st
import requests
import re
import google.generativeai as genai

# ---------------- CONFIG ----------------
OPENWEATHER_KEY = st.secrets.get("OPENWEATHER_API_KEY")
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY")

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

st.set_page_config(page_title="Weather Chatbot", page_icon="🌦️")
st.title("🌦️ Smart Weather Chatbot")

if not OPENWEATHER_KEY or not GEMINI_KEY:
    st.error("API keys missing. Add them to .streamlit/secrets.toml")
    st.stop()

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("models/gemini-pro")

# ---------------- FUNCTIONS ----------------
def extract_city(text: str):
    match = re.search(r"(?:in|at)\s+([a-zA-Z ]+)", text.lower())
    return match.group(1).strip().title() if match else None


def get_weather(city: str):
    params = {
        "q": city,
        "appid": OPENWEATHER_KEY,
        "units": "metric"
    }
    try:
        response = requests.get(WEATHER_URL, params=params, timeout=10)
        if response.status_code != 200:
            return None
        return response.json()
    except requests.RequestException:
        return None


def format_with_gemini(weather):
    prompt = f"""
You are a helpful weather assistant.

Use ONLY the data below.
You may give light advice (clothing, umbrella).
Do NOT invent numbers.

City: {weather['name']}
Temperature: {weather['main']['temp']} °C
Feels Like: {weather['main']['feels_like']} °C
Humidity: {weather['main']['humidity']} %
Condition: {weather['weather'][0]['description']}

Reply in 2–3 natural sentences.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "Sorry, I couldn't generate a response."


def chatbot(user_input: str):
    city = extract_city(user_input)
    if not city:
        return "Please ask like: **What’s the weather in Karachi?**"

    weather = get_weather(city)
    if not weather:
        return f"Could not find weather data for **{city}**."

    return format_with_gemini(weather)

# ---------------- UI ----------------
user_input = st.text_input("Ask about the weather")

if user_input:
    with st.spinner("Checking weather..."):
        reply = chatbot(user_input)
        st.markdown(reply)


