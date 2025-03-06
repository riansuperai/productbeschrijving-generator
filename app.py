import streamlit as st
import pandas as pd
import openai
import os
import tiktoken
import requests
from app_modules import product_description, plagiarism_checker

# Meertalige ondersteuning
LANGUAGES = {
    "nl": {
        "title": "Agung Super AI - Productbeschrijving Generator",
        "prompt_label": "Voer hier je prompt in",
        "upload_label": "Upload een bestand",
        "generate_button": "Genereer Beschrijvingen",
        "download_button": "Download resultaten",
        "language_label": "Kies taal",
        "plagiarism_tool": "Plagiaatchecker",
        "select_tool": "Selecteer een tool",
        "token_usage": "Gebruikte tokens",
        "api_credit": "Beschikbare API-credits"
    },
    "en": {
        "title": "Agung Super AI - Product Description Generator",
        "prompt_label": "Enter your prompt here",
        "upload_label": "Upload a file",
        "generate_button": "Generate Descriptions",
        "download_button": "Download Results",
        "language_label": "Choose Language",
        "plagiarism_tool": "Plagiarism Checker",
        "select_tool": "Select a tool",
        "token_usage": "Tokens Used",
        "api_credit": "Available API Credits"
    }
}

# Keuze voor taal
selected_lang = st.sidebar.selectbox("Language / Taal", ["nl", "en"])
lang = LANGUAGES[selected_lang]

st.title(lang["title"])

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Functie om OpenAI API-tegoed op te vragen
def get_api_credits():
    try:
        response = requests.get("https://api.openai.com/v1/dashboard/billing/subscription",
                                headers={"Authorization": f"Bearer {openai.api_key}"})
        if response.status_code == 200:
            credits = response.json().get("hard_limit_usd", "Onbekend")
            return f"{credits} USD"
        return "Fout bij ophalen van API-tegoed"
    except Exception as e:
        return "Kon API-tegoed niet ophalen"

# Functie om tokens te tellen
def count_tokens(text, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Toon API-credit overzicht
st.sidebar.markdown(f"**{lang['api_credit']}:** {get_api_credits()}")

# Navigatie tussen tools
selected_tool = st.sidebar.radio(lang["select_tool"], ["Productbeschrijving", "Plagiaatchecker"])

if selected_tool == "Productbeschrijving":
    product_description.show_tool(lang, count_tokens)
elif selected_tool == "Plagiaatchecker":
    plagiarism_checker.show_tool(lang, count_tokens)
