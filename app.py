import streamlit as st
import pandas as pd
import openai
import os
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
        "plagiarism_tool": "Plagiaatchecker"
    },
    "en": {
        "title": "Agung Super AI - Product Description Generator",
        "prompt_label": "Enter your prompt here",
        "upload_label": "Upload a file",
        "generate_button": "Generate Descriptions",
        "download_button": "Download Results",
        "language_label": "Choose Language",
        "plagiarism_tool": "Plagiarism Checker"
    }
}

# Keuze voor taal
selected_lang = st.sidebar.selectbox("Language / Taal", ["nl", "en"])
lang = LANGUAGES[selected_lang]

st.title(lang["title"])

# Navigatie tussen tools
selected_tool = st.sidebar.radio("Selecteer een tool", ["Productbeschrijving", "Plagiaatchecker"])

if selected_tool == "Productbeschrijving":
    product_description.show_tool(lang)
elif selected_tool == "Plagiaatchecker":
    plagiarism_checker.show_tool(lang)

# product_description.py
import streamlit as st
import pandas as pd
import openai

def show_tool(lang):
    user_prompt = st.text_area(lang["prompt_label"])
    uploaded_file = st.file_uploader(lang["upload_label"], type=["xlsx", "xls", "csv"])
    
    def generate_description(product_info, prompt):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Je bent een behulpzame AI die productbeschrijvingen genereert."},
                {"role": "user", "content": prompt},
                {"role": "user", "content": str(product_info)}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    
    if uploaded_file and user_prompt:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

        if st.button(lang["generate_button"]):
            df["Productbeschrijving"] = df.apply(lambda row: generate_description(row.to_dict(), user_prompt), axis=1)
            st.download_button(
                label=lang["download_button"],
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="producten_met_beschrijving.csv",
                mime="text/csv"
            )

# plagiarism_checker.py
import streamlit as st
import requests

def check_plagiarism(text):
    # Dit is een placeholder-implementatie, je moet een echte API gebruiken
    API_URL = "https://api.plagiarismchecker.com/check"  # Voorbeeld API-url
    API_KEY = "jouw_api_sleutel"  # Vervang dit door je echte API sleutel
    
    response = requests.post(API_URL, json={"text": text}, headers={"Authorization": f"Bearer {API_KEY}"})
    
    if response.status_code == 200:
        return response.json().get("result", "Geen resultaat ontvangen")
    else:
        return "Fout bij het ophalen van plagiaatresultaten"

def show_tool(lang):
    st.header(lang["plagiarism_tool"])
    user_text = st.text_area("Voer de tekst in om te controleren op plagiaat")
    
    if st.button("Controleer op Plagiaat"):
        st.info("Plagiaatcontrole wordt uitgevoerd...")
        result = check_plagiarism(user_text)
        st.success(result)
