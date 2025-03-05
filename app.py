import streamlit as st
import pandas as pd
import openai
import os

# API-key ophalen uit Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Taalkeuze dropdown
taal_opties = {"Nederlands": "nl", "English": "en"}
geselecteerde_taal = st.selectbox("Kies je taal / Choose your language", list(taal_opties.keys()))

# Stijlkeuze dropdown
stijl_opties = {
    "Persoonlijk en vriendelijk": "friendly",
    "Urgent en dringend": "urgent",
    "Eigenzinnig en gedurfd": "bold",
    "Informatief en servicegericht": "informative",
    "Humoristisch": "humorous",
    "Overtuigend": "persuasive"
}
geselecteerde_stijl = st.selectbox("Kies een stijl / Choose a style", list(stijl_opties.keys()))

# Formele of informele tekst keuze
col1, col2 = st.columns(2)
with col1:
    formeel = st.button("Formeel (U)")
with col2:
    informeel = st.button("Informeel (Je)")

st.title("Agung Super AI - Product Description Generator")

# Prompt invoeren
user_prompt = st.text_area("Voer hier je prompt in")

# Keuze tussen bestandsupload of handmatige invoer
keuze = st.radio("Hoe wil je data invoeren?", ("Bestand uploaden", "Handmatig invoeren"))

if keuze == "Bestand uploaden":
    uploaded_file = st.file_uploader("Upload een bestand", type=["xlsx", "xls", "csv"])
else:
    handmatige_invoer = st.text_area("Voer je productgegevens in")

# Functie om productbeschrijving te genereren
def generate_description(product_info, prompt, taal, stijl, tone):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Je bent een behulpzame AI die productbeschrijvingen genereert in {taal}. Gebruik de stijl {stijl} en de aanspreekvorm {tone}."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": str(product_info)}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

if (uploaded_file or handmatige_invoer) and openai.api_key and user_prompt:
    df = None
    if uploaded_file:
        if uploaded_file.name.endswith("csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    else:
        df = pd.DataFrame([{"Handmatige invoer": handmatige_invoer}])
    
    if st.button("Genereer Beschrijvingen"):
        with st.spinner("Genereren..."):
            tone = "formeel" if formeel else "informeel"
            df["Productbeschrijving"] = df.apply(lambda row: generate_description(row.to_dict(), user_prompt, taal_opties[geselecteerde_taal], stijl_opties[geselecteerde_stijl], tone), axis=1)
        
        # Output box
        st.text_area("Gegenereerde beschrijvingen", "\n".join(df["Productbeschrijving"].tolist()), height=300)
        
        # Download knop
        st.download_button(
            label="Download resultaten",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="producten_met_beschrijving.csv",
            mime="text/csv"
        )
