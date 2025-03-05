import streamlit as st
import pandas as pd
import openai
import os

# API-key ophalen uit Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Agung Super AI - Product Description Generator")

# Keuze tussen uploaden of handmatige invoer
option = st.radio("Kies invoermethode:", ("Upload bestand", "Handmatige invoer"))

# Prompt invoeren
user_prompt = st.text_area("Voer hier je prompt in")

# Taalkeuze dropdown
language = st.selectbox("Kies uitvoertaal:", ["Nederlands", "Engels"])

# Functie om productbeschrijving te genereren
def generate_description(product_info, prompt, language):
    lang_instruction = "Schrijf de beschrijving in het Nederlands." if language == "Nederlands" else "Write the description in English."
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Je bent een behulpzame AI die productbeschrijvingen genereert."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": lang_instruction},
            {"role": "user", "content": str(product_info)}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

if option == "Upload bestand":
    uploaded_file = st.file_uploader("Upload een bestand", type=["xlsx", "xls", "csv"])
    
    if uploaded_file and openai.api_key and user_prompt:
        if uploaded_file.name.endswith("csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if st.button("Genereer Beschrijvingen"):
            df["Productbeschrijving"] = df.apply(lambda row: generate_description(row.to_dict(), user_prompt, language), axis=1)
            
            # Downloadknop
            st.download_button(
                label="Download resultaten",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="producten_met_beschrijving.csv",
                mime="text/csv"
            )

elif option == "Handmatige invoer":
    product_input = st.text_area("Voer productinformatie in")
    
    if st.button("Genereer Beschrijving") and product_input and user_prompt:
        description = generate_description(product_input, user_prompt, language)
        st.text_area("Gegenereerde beschrijving:", description, height=150)
