import streamlit as st
import pandas as pd
import openai
import os

def get_translations(language):
    translations = {
        "English": {
            "title": "Agung Super AI - Product Description Generator",
            "prompt_label": "Enter your prompt",
            "upload_label": "Upload a file (CSV or Excel)",
            "generate_button": "Generate Descriptions",
            "download_button": "Download results",
            "language_label": "Choose output language",
            "style_label": "Choose a style",
            "file_option": "Upload file",
            "input_option": "Manual input",
            "progress_message": "Generating descriptions... Please wait...",
            "result_label": "Generated description"
        },
        "Nederlands": {
            "title": "Agung Super AI - Productbeschrijving Generator",
            "prompt_label": "Voer hier je prompt in",
            "upload_label": "Upload een bestand (CSV of Excel)",
            "generate_button": "Genereer Beschrijvingen",
            "download_button": "Download resultaten",
            "language_label": "Kies uitvoertaal",
            "style_label": "Kies een stijl",
            "file_option": "Bestand uploaden",
            "input_option": "Handmatige invoer",
            "progress_message": "Beschrijvingen worden gegenereerd... Even geduld...",
            "result_label": "Gegenereerde beschrijving"
        }
    }
    return translations[language]

# Interface language selection
language = st.sidebar.selectbox("Select Language / Kies Taal", ["English", "Nederlands"])
text = get_translations(language)

st.title(text["title"])

# Choose input method
input_method = st.radio("", [text["file_option"], text["input_option"]])

# API-key ophalen uit Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Prompt invoeren
user_prompt = st.text_area(text["prompt_label"])

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

# Functie om productbeschrijving te genereren
def generate_description(product_info, prompt, language, style):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Je bent een behulpzame AI die productbeschrijvingen genereert."},
            {"role": "user", "content": f"Taal: {language}, Stijl: {style}"},
            {"role": "user", "content": prompt},
            {"role": "user", "content": str(product_info)}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

if input_method == text["file_option"]:
    uploaded_file = st.file_uploader(text["upload_label"], type=["xlsx", "xls", "csv"])

    if uploaded_file and openai.api_key and user_prompt:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

        if st.button(text["generate_button"]):
            with st.spinner(text["progress_message"]):
                df["Productbeschrijving"] = df.apply(lambda row: generate_description(row.to_dict(), user_prompt, output_language, style_choice), axis=1)
            
            # Excel met nieuwe kolom downloaden
            st.download_button(
                label=text["download_button"],
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="producten_met_beschrijving.csv",
                mime="text/csv"
            )
else:
    user_input = st.text_area("Voer productdetails in")
    if st.button(text["generate_button"]):
        with st.spinner(text["progress_message"]):
            generated_description = generate_description(user_input, user_prompt, output_language, style_choice)
        st.text_area(text["result_label"], generated_description, height=200)
