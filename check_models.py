import google.generativeai as genai
import toml

secrets = toml.load(".streamlit/secrets.toml")
genai.configure(api_key=secrets["GEMINI_API_KEY"])

print("Listing models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
