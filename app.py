import streamlit as st
import pandas as pd
import openai
import tiktoken
import html
import google.generativeai as genai

# Initialize OpenAI client
client = openai.OpenAI()

# Initialize Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def get_translations(language):
    # ... (jouw bestaande vertalingen code)

# Functie om tokens te tellen
def count_tokens(text, model="gpt-3.5-turbo"):
    # ... (jouw bestaande token tellen code)

def clean_text(text):
    # ... (jouw bestaande clean text code)

def convert_html_to_markdown(html_text):
    # ... (jouw bestaande convert html to markdown code)

# Load last used prompt
if "last_prompt" not in st.session_state:
    # ... (jouw bestaande load last prompt code)

# Interface language selection
language = st.sidebar.selectbox("Select Language / Kies Taal", ["English", "Nederlands"])
text = get_translations(language)

st.title(text["title"])

# AI Model selection
ai_platform = st.sidebar.selectbox("Choose AI Platform", ["OpenAI", "Gemini"])

if ai_platform == "OpenAI":
    model_choice = st.sidebar.selectbox(text["model_label"], ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo-16k"])
    temperature = st.sidebar.slider(text["temperature_label"], 0.0, 1.2, 0.7, 0.1)
else:
    model_choice = "gemini-pro"
    temperature = 1.0 # Gemini heeft geen temperature parameter op dezelfde manier als openai

# Choose input method
input_method = st.radio("", [text["file_option"], text["input_option"]])

# API-key ophalen uit Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Prompt upload
uploaded_prompt = st.file_uploader(text["upload_prompt_label"], type=["txt"])
if uploaded_prompt is not None:
    # ... (jouw bestaande prompt upload code)

# Prompt invoeren
user_prompt = st.text_area(text["prompt_label"], value=st.session_state.last_prompt)

# Load last used prompt
if st.button(text["load_last_prompt"]):
    # ... (jouw bestaande load last prompt code)

# Output language selection
output_language = st.selectbox(text["language_label"], ["Nederlands", "English"])

# Style selection
style_options = [
    "Persoonlijk en vriendelijk",
    "Urgent en dringend",
    "Eigenzinnig en gedurfd",
    "Informatief en servicegericht",
    "Humoristisch",
    "Overtuigend"
]
style_choice = st.selectbox(text["style_label"], style_options)

# Define generate_description function
def generate_description(product_details, user_prompt, output_language, style_choice, model_choice, temperature, ai_platform):
    prompt = f"{user_prompt}\n\nProductdetails: {product_details}\n\nOutput language: {output_language}\nStyle: {style_choice}"
    if ai_platform == "OpenAI":
        response = client.chat.completions.create(
            model=model_choice,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        description = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        return description, tokens_used
    elif ai_platform == "Gemini":
        try:
            model = genai.GenerativeModel(model_choice)
            response = model.generate_content(prompt)
            description = response.text
            tokens_used = count_tokens(prompt + description)
            return description, tokens_used
        except Exception as e:
            st.error(f"Gemini API error: {e}. Falling back to OpenAI.")
            ai_platform = "OpenAI" #Forceert de functie om open ai te gebruiken.
            return generate_description(product_details, user_prompt, output_language, style_choice, "gpt-3.5-turbo", 0.7, ai_platform)

# Manual input section
if input_method == text["input_option"]:
    # ... (jouw bestaande manual input code)

# File upload
if input_method == text["file_option"]:
    # ... (jouw bestaande file upload code)
