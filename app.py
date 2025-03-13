import streamlit as st
import pandas as pd
import openai
import tiktoken
import html
import google.generativeai as genai

# Initialize OpenAI client
client = openai.OpenAI()

# Initialize Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"]) # API key uit secrets

def get_translations(language):
    translations = {
        "English": {
            "title": "Ami Super-Ai",
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
            "manual_input_label": "Enter product details (comma-separated)"
        },
        "Nederlands": {
            "title": "Ami Super-Ai",
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
            "manual_input_label": "Voer productdetails in (komma-gescheiden)"
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

# Load last used prompt
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# Interface language selection
language = st.sidebar.selectbox("Select Language / Kies Taal", ["English", "Nederlands"])
text = get_translations(language)

st.title(text["title"])

# AI Model selection
ai_platform = st.sidebar.selectbox("Choose AI Platform", ["OpenAI", "Gemini"])

if ai_platform == "OpenAI":
    model_choice = st.sidebar.selectbox(text["model_label"], ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo-16k"])
    temperature = st.sidebar.slider(text["temperature_label"], 0.0, 1.2, 0.7, 0.1)
else:
    # Gemini models
    gemini_models = ["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro", "gemini-1.5-flash"] # Voeg 1.5 pro en flash toe.
    model_choice = st.sidebar.selectbox(text["model_label"], gemini_models)
    temperature = 1.0 # Gemini heeft geen temperature parameter op dezelfde manier als openai

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

# Define generate_description function
def generate_description(product_details, user_prompt, output_language, style_choice, model_choice, temperature, ai_platform):
    prompt = f"{user_prompt}\n\nProductdetails: {product_details}\n\nOutput language: {output_language}\nStyle: {style_choice}"
    if ai_platform == "OpenAI":
        response = client.chat.completions.create(
            model=model_choice,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        description = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        return description, tokens_used
    elif ai_platform == "Gemini":
        model = genai.GenerativeModel(model_choice)
        response = model.generate_content(prompt)
        description = response.text
        tokens_used = count_tokens(prompt + description) # Gemini geeft niet direct token gebruik.
        return description, tokens_used

# Manual input section
if input_method == text["input_option"]:
    manual_input = st.text_area(text["manual_input_label"])
    if st.button(text["generate_button"]) and manual_input:
        product_details = dict(zip(["Productdetails"], [manual_input]))
        with st.spinner(text["progress_message"]):
            description, tokens_used = generate_description(product_details, user_prompt, output_language, style_choice, model_choice, temperature, ai_platform)
        st.markdown(convert_html_to_markdown(description), unsafe_allow_html=True)
        st.sidebar.markdown(f"**{text['token_usage']}:** {tokens_used}")

# File upload
if input_method == text["file_option"]:
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
                results = df.apply(lambda row: generate_description(row.to
