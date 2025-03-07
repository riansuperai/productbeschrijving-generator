import streamlit as st
import pandas as pd
import openai
import os
import tiktoken
import html

# Initialize OpenAI client
client = openai.OpenAI()

def get_translations(language):
    translations = {
        "English": {
            "title": "Rian SuperAI PDG",
            "prompt_label": "Enter your prompt",
            "upload_label": "Upload a file (CSV or Excel)",
            "generate_button": "Generate Descriptions",
            "download_button": "Download results",
            "language_label": "Choose output language",
            "style_label": "Choose a style",
            "file_option": "Upload file",
            "input_option": "Manual input",
            "progress_message": "Generating descriptions... Please wait...",
            "result_label": "Generated description",
            "token_usage": "Tokens Used",
            "model_label": "Choose AI Model",
            "temperature_label": "Set AI Creativity (Temperature)",
            "output_label": "Generated Descriptions Preview",
            "upload_prompt_label": "Upload a prompt file (TXT)",
            "load_last_prompt": "Load last used prompt",
            "style_options": [
                "Personal and friendly",
                "Urgent and important",
                "Quirky and bold",
                "Informative and service-oriented",
                "Humorous",
                "Persuasive"
            ]
        },
        "Nederlands": {
            "title": "Rian SuperAI PDG",
            "prompt_label": "Voer hier je prompt in",
            "upload_label": "Upload een bestand (CSV of Excel)",
            "generate_button": "Genereer Beschrijvingen",
            "download_button": "Download resultaten",
            "language_label": "Kies uitvoertaal",
            "style_label": "Kies een stijl",
            "file_option": "Bestand uploaden",
            "input_option": "Handmatige invoer",
            "progress_message": "Beschrijvingen worden gegenereerd... Even geduld...",
            "result_label": "Gegenereerde beschrijving",
            "token_usage": "Gebruikte tokens",
            "model_label": "Kies AI-model",
            "temperature_label": "Stel AI Creativiteit in (Temperature)",
            "output_label": "Gegenereerde Beschrijvingen Voorbeeld",
            "upload_prompt_label": "Upload een promptbestand (TXT)",
            "load_last_prompt": "Laad laatst gebruikte prompt",
            "style_options": [
                "Persoonlijk en vriendelijk",
                "Urgent en belangrijk",
                "Eigenzinnig en gedurfd",
                "Informatief en servicegericht",
                "Humoristisch",
                "Overtuigend"
            ]
        },
        "Deutsch": {
            "title": "Rian SuperAI PDG",
            "prompt_label": "Geben Sie Ihren Prompt ein",
            "upload_label": "Laden Sie eine Datei hoch (CSV oder Excel)",
            "generate_button": "Beschreibungen generieren",
            "download_button": "Ergebnisse herunterladen",
            "language_label": "Wählen Sie die Ausgabesprache",
            "style_label": "Wählen Sie einen Stil",
            "file_option": "Datei hochladen",
            "input_option": "Manuelle Eingabe",
            "progress_message": "Beschreibungen werden generiert... Bitte warten...",
            "result_label": "Generierte Beschreibung",
            "token_usage": "Verwendete Tokens",
            "model_label": "Wählen Sie ein KI-Modell",
            "temperature_label": "KI-Kreativität einstellen (Temperature)",
            "output_label": "Vorschau der generierten Beschreibungen",
            "upload_prompt_label": "Laden Sie eine Prompt-Datei hoch (TXT)",
            "load_last_prompt": "Letzten verwendeten Prompt laden",
            "style_options": [
                "Persönlich und freundlich",
                "Dringend und wichtig",
                "Eigenwillig und kühn",
                "Informativ und dienstleistungsorientiert",
                "Humorvoll",
                "Überzeugend"
            ]
        }
    }
    return translations[language]

# Functie om tokens te tellen
def count_tokens(text, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def clean_text(text):
    return text.encode('utf-8', 'ignore').decode('utf-8')

def convert_html_to_markdown(html_text):
    return html.unescape(html_text).replace("\n", "\n\n")

# Load last used prompt
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# Interface language selection
language = st.sidebar.selectbox("Select Language / Kies Taal / Sprache wählen", ["English", "Nederlands", "Deutsch"])
text = get_translations(language)

st.title(text["title"])

# AI Model selection
model_choice = st.sidebar.selectbox(text["model_label"], ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo-16k"])

# Temperature selection
temperature = st.sidebar.slider(text["temperature_label"], 0.0, 1.2, 0.7, 0.1)

# Choose input method
input_method = st.radio("", [text["file_option"], text["input_option"]])

# API-key ophalen uit Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Prompt upload
uploaded_prompt = st.file_uploader(text["upload_prompt_label"], type=["txt"])
if uploaded_prompt is not None:
    st.session_state.last_prompt = uploaded_prompt.read().decode("utf-8")

# Prompt invoeren
user_prompt = st.text_area(text["prompt_label"], value=st.session_state.last_prompt)

# Load last used prompt
if st.button(text["load_last_prompt"]):
    st.session_state.last_prompt = user_prompt

# Output language selection
output_language = st.selectbox(text["language_label"], ["Nederlands", "English", "Deutsch"])

# Style selection
style_choice = st.selectbox(text["style_label"], text["style_options"])

# File upload
uploaded_file = st.file_uploader(text["upload_label"], type=["xlsx", "xls", "csv"])

# Generate button for uploaded file
if input_method == text["file_option"] and uploaded_file:
    if st.button(text["generate_button"]):
        st.write("Processing uploaded file...")  # Placeholder for actual processing logic
