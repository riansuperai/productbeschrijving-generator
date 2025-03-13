import streamlit as st
import pandas as pd
import openai
import os
import tiktoken
import html

# Controleer of de API-sleutel beschikbaar is
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("OpenAI API-sleutel ontbreekt! Voeg deze toe aan Streamlit secrets.")

def count_tokens(text, model="gpt-3.5-turbo"):
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        st.error(f"Fout bij het tellen van tokens: {e}")
        return 0

def convert_html_to_markdown(html_text):
    return html.unescape(html_text).replace("\n", "\n\n")

def generate_description(item, prompt, output_language, style, model, temperature):
    try:
        full_prompt = f"{prompt}\n\nItem: {item['Item']}\nTaal: {output_language}\nStijl: {style}\nGenereer een beschrijving."
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=temperature,
            max_tokens=150
        )
        
        description = response["choices"][0]["message"]["content"].strip()
        tokens_used = count_tokens(full_prompt + description, model)
        
        return description, tokens_used
    except Exception as e:
        st.error(f"Fout bij het genereren van de beschrijving: {e}")
        return f"Fout: {e}", 0

st.title("Productbeschrijving Generator")

model_choice = st.sidebar.selectbox("Kies AI-model", ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo-16k"])
temperature = st.sidebar.slider("Creativiteit (Temperature)", 0.0, 1.2, 0.7, 0.1)
input_method = st.radio("", ["Bestand uploaden", "Handmatige invoer"])

user_prompt = st.text_area("Voer hier je prompt in")
output_language = st.selectbox("Kies uitvoertaal", ["Nederlands", "English"])
style_options = ["Persoonlijk en vriendelijk", "Urgent en dringend", "Informatief", "Humoristisch", "Overtuigend"]
style_choice = st.selectbox("Kies een stijl", style_options)

if input_method == "Bestand uploaden":
    uploaded_file = st.file_uploader("Upload een bestand (CSV of Excel)", type=["xlsx", "xls", "csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip') if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            if st.button("Genereer Beschrijvingen"):
                with st.spinner("Beschrijvingen worden gegenereerd..."):
                    results = df.apply(lambda row: generate_description({"Item": row["Item"]}, user_prompt, output_language, style_choice, model_choice, temperature), axis=1)
                    df["Productbeschrijving"], df["Tokens Gebruikt"] = zip(*results)
                    st.download_button("Download resultaten", data=df.to_csv(index=False, encoding="utf-8").encode("utf-8"), file_name="producten_met_beschrijving.csv", mime="text/csv")
        except Exception as e:
            st.error(f"Fout bij het inlezen van het bestand: {e}")
else:
    manual_input = st.text_area("Voer uw gegevens handmatig in", placeholder="Één item per regel")
    if manual_input and st.button("Genereer Beschrijvingen"):
        items = manual_input.split("\n")
        df = pd.DataFrame(items, columns=["Item"])
        with st.spinner("Beschrijvingen worden gegenereerd..."):
            results = df.apply(lambda row: generate_description({"Item": row["Item"]}, user_prompt, output_language, style_choice, model_choice, temperature), axis=1)
            df["Productbeschrijving"], df["Tokens Gebruikt"] = zip(*results)
            st.download_button("Download resultaten", data=df.to_csv(index=False, encoding="utf-8").encode("utf-8"), file_name="producten_met_beschrijving.csv", mime="text/csv")
