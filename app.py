import streamlit as st
import pandas as pd
import openai
import time

# API-key ophalen uit Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Language selection
language = st.selectbox("Select Language / Kies een taal", ["English", "Nederlands"])

# Translation dictionary
translations = {
    "English": {
        "title": "Agung Super AI - Product Description Generator",
        "prompt_label": "Enter your prompt here",
        "upload_label": "Upload a file (CSV or Excel)",
        "generate_button": "Generate Descriptions",
        "download_button": "Download Results",
        "input_option": "Choose Input Method",
        "upload_file": "Upload File",
        "manual_input": "Manual Input",
        "output_label": "Generated Description",
        "language_output": "Choose output language",
        "tone_style": "Choose a style or personal tone"
    },
    "Nederlands": {
        "title": "Agung Super AI - Productbeschrijving Generator",
        "prompt_label": "Voer hier je prompt in",
        "upload_label": "Upload een bestand (CSV of Excel)",
        "generate_button": "Genereer Beschrijvingen",
        "download_button": "Download resultaten",
        "input_option": "Kies invoermethode",
        "upload_file": "Bestand uploaden",
        "manual_input": "Handmatige invoer",
        "output_label": "Gegenereerde Beschrijving",
        "language_output": "Kies uitvoertaal",
        "tone_style": "Kies een stijl of persoonlijke toon"
    }
}

# Apply translations
tr = translations[language]

st.title(tr["title"])

# Prompt invoeren
user_prompt = st.text_area(tr["prompt_label"])

# Input selection method
input_method = st.radio(tr["input_option"], [tr["upload_file"], tr["manual_input"]])

# File upload option
uploaded_file = None
manual_text = ""
if input_method == tr["upload_file"]:
    uploaded_file = st.file_uploader(tr["upload_label"], type=["xlsx", "xls", "csv"])
else:
    manual_text = st.text_area("Enter your product details manually")

# Output language selection
output_language = st.selectbox(tr["language_output"], ["Nederlands", "English"])

# Tone style selection
tone_style = st.selectbox(tr["tone_style"], [
    "Persoonlijk en vriendelijk", "Urgent en dringend", "Eigenzinnig en gedurfd",
    "Informatief en servicegericht", "Humoristisch", "Overtuigend"
])

# Functie om productbeschrijving te genereren
def generate_description(product_info, prompt, lang, tone):
    full_prompt = f"{prompt}\nTone: {tone}\nLanguage: {lang}\nProduct Info: {product_info}"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful AI that generates product descriptions."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

if st.button(tr["generate_button"]):
    with st.spinner("Generating descriptions..."):
        time.sleep(1)
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            df["Productbeschrijving"] = df.apply(lambda row: generate_description(row.to_dict(), user_prompt, output_language, tone_style), axis=1)
            
            # Show output preview
            st.text_area(tr["output_label"], df["Productbeschrijving"].iloc[0])
            
            # Excel met nieuwe kolom downloaden
            st.download_button(
                label=tr["download_button"],
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="producten_met_beschrijving.csv",
                mime="text/csv"
            )
        elif manual_text:
            generated_text = generate_description(manual_text, user_prompt, output_language, tone_style)
            st.text_area(tr["output_label"], generated_text)
