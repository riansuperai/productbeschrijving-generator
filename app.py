import streamlit as st
import pandas as pd
import openai

# Set your OpenAI API key here
openai.api_key = "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"

# Streamlit UI
st.title("Agung Super AI - Product Description Generator")

# Prompt invoeren
user_prompt = st.text_area("Voer hier je prompt in")

# Excel-bestand uploaden
uploaded_file = st.file_uploader("Upload een Excel-bestand", type=["xlsx", "xls"])

# Functie om productbeschrijving te genereren
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
    # Dataframe inlezen
    df = pd.read_excel(uploaded_file)
    
    if st.button("Genereer Beschrijvingen"):
        df["Productbeschrijving"] = df.apply(lambda row: generate_description(row.to_dict(), user_prompt), axis=1)
        
        # Excel met nieuwe kolom downloaden
        st.download_button(
            label="Download resultaten",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="producten_met_beschrijving.csv",
            mime="text/csv"
        )
