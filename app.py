import streamlit as st
import pandas as pd
import openai
import os
import tiktoken
import html

# Initialize OpenAI client
client = openai.OpenAI()

def get_translations(language):
    translations = {
        "English": {
            "title": "Rian SuperAI PDG",
            "prompt_label": "Enter your prompt",
            "upload_label": "Upload a file (CSV or Excel)",
            "generate_button": "Generate Descriptions",
            "download_button": "Download results",
            "language_label": "Choose output language",
            "style_label": "Choose a style",
            "file_option": "Upload file",
            "input_option": "Manual input",
            "progress_message": "Generating descriptions... Please wait...",
            "result_label": "Generated description",
            "token_usage": "Tokens Used",
            "model_label": "Choose AI Model",
            "temperature_label": "Set AI Creativity (Temperature)",
            "output_label": "Generated Descriptions Preview",
            "upload_prompt_label": "Upload a prompt file (TXT)",
            "load_last_prompt": "Load last used prompt",
            "manual_input_label": "Enter your data manually",
            "manual_input_placeholder": "Enter your data here, one item per line"
        },
        "Nederlands": {
            "title": "Rian SuperAI PDG",
            "prompt_label": "Voer hier je prompt in",
            "upload_label": "Upload een bestand (CSV of Excel)",
            "generate_button": "Genereer Beschrijvingen",
            "download_button": "Download resultaten",
            "language_label": "Kies uitvoertaal",
            "style_label": "Kies een stijl",
            "file_option": "Bestand uploaden",
            "input_option": "Handmatige invoer",
            "progress_message": "Beschrijvingen worden gegenereerd... Even geduld...",
            "result_label": "Gegenereerde beschrijving",
            "token_usage": "Gebruikte tokens",
            "model_label": "Kies AI-model",
            "temperature_label": "Stel AI Creativiteit in (Temperature)",
            "output_label": "Gegenereerde Beschrijvingen Voorbeeld",
            "upload_prompt_label": "Upload een promptbestand (TXT)",
            "load_last_prompt": "Laad laatst gebruikte prompt",
            "manual_input_label": "Voer uw gegevens handmatig in",
            "manual_input_placeholder": "Voer hier uw gegevens in, één item per regel"
        }
    }
    return translations[language]

# Functie om tokens te tellen
def count_tokens(text, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def clean_text(text):
    return text.encode('utf-8', 'ignore').decode('utf-8')

def convert_html_to_markdown(html_text):
    return html.unescape(html_text).replace("\n", "\n\n")

def generate_description(item, prompt, output_language, style, model, temperature):
    """
    Genereer een beschrijving voor een item met behulp van OpenAI's GPT-model.
    
    Args:
        item (dict): Een dictionary met de gegevens van het item.
        prompt (str): De prompt die wordt gebruikt om de beschrijving te genereren.
        output_language (str): De taal waarin de beschrijving moet worden gegenereerd.
        style (str): De stijl van de beschrijving.
        model (str): Het GPT-model dat moet worden gebruikt.
        temperature (float): De creativiteit van het model (0.0 tot 1.2).
    
    Returns:
        tuple: Een tuple met de gegenereerde beschrijving en het aantal gebruikte tokens.
    """
    try:
        # Bouw de prompt op basis van de invoer
        full_prompt = f"{prompt}\n\nItem: {item['Item']}\nTaal: {output_language}\nStijl: {style}\nGenereer een beschrijving."
        
        # Roep het OpenAI-model aan
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=temperature,
            max_tokens=150
        )
        
        # Haal de gegenereerde tekst op
        description = response.choices[0].message.content.strip()
        
        # Tel het aantal gebruikte tokens
        tokens_used = count_tokens(full_prompt + description, model)
        
        return description, tokens_used
    
    except Exception as e:
        st.error(f"Fout bij het genereren van de beschrijving: {e}")
        return f"Fout: {e}", 0

# Load last used prompt
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# Interface language selection
language = st.sidebar.selectbox("Select Language / Kies Taal", ["English", "Nederlands"])
text = get_translations(language)

st.title(text["title"])

# AI Model selection
model_choice = st.sidebar.selectbox(text["model_label"], ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo-16k"])

# Temperature selection
temperature = st.sidebar.slider(text["temperature_label"], 0.0, 1.2, 0.7, 0.1)

# Choose input method
input_method = st.radio("", [text["file_option"], text["input_option"]])

# API-key ophalen uit Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Prompt upload
uploaded_prompt = st.file_uploader(text["upload_prompt_label"], type=["txt"])
if uploaded_prompt is not None:
    st.session_state.last_prompt = uploaded_prompt.read().decode("utf-8")

# Prompt invoeren
user_prompt = st.text_area(text["prompt_label"], value=st.session_state.last_prompt)

# Load last used prompt
if st.button(text["load_last_prompt"]):
    st.session_state.last_prompt = user_prompt

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

if input_method == text["file_option"]:
    # File upload
    uploaded_file = st.file_uploader(text["upload_label"], type=["xlsx", "xls", "csv"])

    # Handle CSV and Excel file parsing
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
            else:
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Fout bij het inlezen van het bestand: {e}")
            df = None

        if df is not None and st.button(text["generate_button"]):
            with st.spinner(text["progress_message"]):
                results = df.apply(lambda row: generate_description({"Item": row["Item"]}, user_prompt, output_language, style_choice, model_choice, temperature), axis=1)
                df["Productbeschrijving"], df["Tokens Gebruikt"] = zip(*results)

            # Toon tokengebruik
            total_tokens = df["Tokens Gebruikt"].sum()
            st.sidebar.markdown(f"**{text['token_usage']}:** {total_tokens}")
            
            # Toon gegenereerde beschrijvingen met markdown-opmaak
            st.subheader(text["output_label"])
            for desc in df["Productbeschrijving"].head():
                st.markdown(convert_html_to_markdown(desc), unsafe_allow_html=True)
                st.markdown("---")
            
            # Excel met nieuwe kolom downloaden
            st.download_button(
                label=text["download_button"],
                data=df.to_csv(index=False, encoding="utf-8").encode("utf-8"),
                file_name="producten_met_beschrijving.csv",
                mime="text/csv"
            )
else:
    # Manual input section
    manual_input = st.text_area(text["manual_input_label"], placeholder=text["manual_input_placeholder"], height=150)
    
    if manual_input and st.button(text["generate_button"]):
        # Split manual input into lines
        items = manual_input.split("\n")
        
        # Create a DataFrame from the manual input
        df = pd.DataFrame(items, columns=["Item"])
        
        with st.spinner(text["progress_message"]):
            results = df.apply(lambda row: generate_description({"Item": row["Item"]}, user_prompt, output_language, style_choice, model_choice, temperature), axis=1)
            df["Productbeschrijving"], df["Tokens Gebruikt"] = zip(*results)

        # Toon tokengebruik
        total_tokens = df["Tokens Gebruikt"].sum()
        st.sidebar.markdown(f"**{text['token_usage']}:** {total_tokens}")
        
        # Toon gegenereerde beschrijvingen met markdown-opmaak
        st.subheader(text["output_label"])
        for desc in df["Productbeschrijving"].head():
            st.markdown(convert_html_to_markdown(desc), unsafe_allow_html=True)
            st.markdown("---")
        
        # Excel met nieuwe kolom downloaden
        st.download_button(
            label=text["download_button"],
            data=df.to_csv(index=False, encoding="utf-8").encode("utf-8"),
            file_name="producten_met_beschrijving.csv",
            mime="text/csv"
        )
