import streamlit as st
import pandas as pd
import openai
import time

# API-key ophalen uit Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Agung Super AI - Product Description Generator")

# Prompt invoeren
user_prompt = st.text_area("Voer hier je prompt in")

# Keuze tussen bestand uploaden of handmatig invoeren
input_option = st.radio("Kies invoermethode", ("Upload bestand", "Handmatige invoer"))

# Dropdown voor taalkeuze
language = st.selectbox("Kies output taal", ["Nederlands", "English"])

# Dropdown voor schrijfstijl
style_tone = st.selectbox("Kies een stijl", [
    "Persoonlijk en vriendelijk",
    "Urgent en dringend",
    "Eigenzinnig en gedurfd",
    "Informatief en servicegericht",
    "Humoristisch",
    "Overtuigend"
])

if input_option == "Upload bestand":
    uploaded_file = st.file_uploader("Upload een CSV- of Excel-bestand", type=["xlsx", "xls", "csv"])
    
    if uploaded_file:
        if uploaded_file.name.endswith("csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
else:
    manual_input = st.text_area("Voer je productinformatie in")

def generate_description(product_info, prompt, language, style_tone):
    messages = [
        {"role": "system", "content": "Je bent een behulpzame AI die productbeschrijvingen genereert."},
        {"role": "user", "content": f"Taal: {language}. Stijl: {style_tone}. {prompt}"},
        {"role": "user", "content": str(product_info)}
    ]
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()

if st.button("Genereer Beschrijvingen"):
    with st.spinner("AI is bezig met genereren..."):
        if input_option == "Upload bestand" and uploaded_file:
            df["Productbeschrijving"] = df.apply(lambda row: generate_description(row.to_dict(), user_prompt, language, style_tone), axis=1)
            
            st.download_button(
                label="Download resultaten",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="producten_met_beschrijving.csv",
                mime="text/csv"
            )
        elif input_option == "Handmatige invoer" and manual_input:
            result = generate_description(manual_input, user_prompt, language, style_tone)
            st.text_area("Gegenereerde beschrijving", result, height=200)
