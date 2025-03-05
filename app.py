import streamlit as st
import pandas as pd
import openai
import os

# API-key ophalen uit Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Agung Super AI - Product Description Generator")

# Prompt invoeren
user_prompt = st.text_area("Voer hier je prompt in")

# Dropdown om taal te selecteren
language = st.selectbox("Kies de uitvoertaal:", ["Nederlands", "English"])

# Bestand uploaden (Excel of CSV)
uploaded_file = st.file_uploader("Upload een Excel- of CSV-bestand", type=["xlsx", "xls", "csv"])

# Functie om productbeschrijving te genereren
def generate_description(product_info, prompt, lang):
    lang_instruction = "Genereer de productbeschrijving in het Nederlands." if lang == "Nederlands" else "Generate the product description in English."
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Je bent een behulpzame AI die productbeschrijvingen genereert."},
            {"role": "user", "content": lang_instruction},
            {"role": "user", "content": prompt},
            {"role": "user", "content": str(product_info)}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

if uploaded_file and openai.api_key and user_prompt:
    # Bepaal bestandstype en lees het in als DataFrame
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    if st.button("Genereer Beschrijvingen"):
        df["Productbeschrijving"] = df.apply(lambda row: generate_description(row.to_dict(), user_prompt, language), axis=1)
        
        # Download de resultaten als CSV
        st.download_button(
            label="Download resultaten",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="producten_met_beschrijving.csv",
            mime="text/csv"
        )
