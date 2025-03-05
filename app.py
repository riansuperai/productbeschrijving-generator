import streamlit as st
import pandas as pd
import openai
import os

# API-key ophalen uit Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Agung Super AI - Product Description Generator")

# Prompt invoeren
user_prompt = st.text_area("Voer hier je prompt in")

# Keuze tussen uploaden of handmatige invoer
input_option = st.radio("Kies een invoermethode:", ("Upload een bestand", "Handmatige invoer"))

# Taalkeuze
language = st.selectbox("Kies de uitvoertaal:", ["Nederlands", "Engels"])

# Functie om productbeschrijving te genereren
def generate_description(product_info, prompt, language):
    lang_prompt = "Schrijf dit in het Nederlands." if language == "Nederlands" else "Write this in English."
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Je bent een behulpzame AI die productbeschrijvingen genereert."},
            {"role": "user", "content": lang_prompt},
            {"role": "user", "content": prompt},
            {"role": "user", "content": str(product_info)}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

if input_option == "Upload een bestand":
    uploaded_file = st.file_uploader("Upload een Excel- of CSV-bestand", type=["xlsx", "xls", "csv"])
    
    if uploaded_file and openai.api_key and user_prompt:
        if uploaded_file.name.endswith("csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        if st.button("Genereer Beschrijvingen"):
            df["Productbeschrijving"] = df.apply(lambda row: generate_description(row.to_dict(), user_prompt, language), axis=1)
            
            # Output weergeven
            st.write("**Gegenereerde beschrijvingen:**")
            st.dataframe(df[["Productbeschrijving"]])
            
            # Excel met nieuwe kolom downloaden
            st.download_button(
                label="Download resultaten",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="producten_met_beschrijving.csv",
                mime="text/csv"
            )

elif input_option == "Handmatige invoer":
    manual_input = st.text_area("Voer productinformatie in")
    
    if st.button("Genereer Beschrijving") and manual_input:
        result = generate_description(manual_input, user_prompt, language)
        
        # Output weergeven
        st.write("**Gegenereerde beschrijving:**")
        st.text_area("Output", value=result, height=200)
