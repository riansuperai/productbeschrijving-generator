import streamlit as st
import pandas as pd
import openai
import os

# API-key ophalen uit Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Agung Super AI - Product Description Generator")

# Keuze tussen bestand uploaden of handmatige invoer
input_option = st.radio("Kies een invoermethode", ("Upload bestand", "Handmatige invoer"))

# Prompt invoeren
user_prompt = st.text_area("Voer hier je prompt in")

# Taalkeuze
language = st.selectbox("Kies de uitvoertaal", ("Nederlands", "Engels"))

# Functie om productbeschrijving te genereren
def generate_description(product_info, prompt, language):
    lang_instruction = "Schrijf in het Nederlands." if language == "Nederlands" else "Write in English."
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

# Layout instellen
col1, col2 = st.columns(2)

if input_option == "Upload bestand":
    with col1:
        uploaded_file = st.file_uploader("Upload een bestand", type=["xlsx", "xls", "csv"])
    
    if uploaded_file and openai.api_key and user_prompt:
        if uploaded_file.name.endswith("csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        if st.button("Genereer Beschrijvingen"):
            df["Productbeschrijving"] = df.apply(lambda row: generate_description(row.to_dict(), user_prompt, language), axis=1)
            
            with col2:
                st.write("**Gegenereerde productbeschrijvingen:**")
                st.dataframe(df)
                
            st.download_button(
                label="Download resultaten",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="producten_met_beschrijving.csv",
                mime="text/csv"
            )
else:
    with col1:
        product_input = st.text_area("Voer hier je productinformatie in")
    
    if st.button("Genereer Beschrijving") and product_input:
        result = generate_description(product_input, user_prompt, language)
        with col2:
            st.write("**Gegenereerde productbeschrijving:**")
            st.text_area("", result, height=200)
