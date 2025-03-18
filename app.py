import streamlit as st
import pandas as pd
import html
import google.generativeai as genai

# Initialize Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

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

def clean_text(text):
    return text.encode('utf-8', 'ignore').decode('utf-8').strip()

def generate_description(product_details, user_prompt, output_language, style_choice, model_choice, temperature, ai_platform):
    prompt = f"{user_prompt}\n\nProductdetails: {product_details}\n\nOutput language: {output_language}\nStyle: {style_choice}"
    if ai_platform == "Gemini":
        model = genai.GenerativeModel(model_choice)
        response = model.generate_content(prompt)
        description = clean_text(response.text)
        return description, 0

# Load last used prompt
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# Interface language selection
language = st.sidebar.selectbox("Select Language / Kies Taal", ["English", "Nederlands"])
text = get_translations(language)

st.title(text["title"])

# AI Model selection
ai_platform = st.sidebar.selectbox("Choose AI Platform", ["Gemini"])
gemini_models = ["gemini-1.5-pro", "gemini-1.5-flash"]
model_choice = st.sidebar.selectbox(text["model_label"], gemini_models)
temperature = 1.0

# Choose input method
input_method = st.radio("", [text["file_option"], text["input_option"]])

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

# Manual input section
if input_method == text["input_option"]:
    manual_input = st.text_area(text["manual_input_label"])
    if st.button(text["generate_button"]) and manual_input:
        product_details = dict(zip(["Productdetails"], [manual_input]))
        with st.spinner(text["progress_message"]):
            description, tokens_used = generate_description(product_details, user_prompt, output_language, style_choice, model_choice, temperature, ai_platform)
        st.markdown(description)

# File upload
if input_method == text["file_option"]:
    uploaded_file = st.file_uploader(text["upload_label"], type=["xlsx", "xls", "csv"])

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
            results = []
            total_rows = len(df)
            progress_bar = st.progress(0)

            # Create a placeholder for the markdown display
            markdown_placeholder = st.empty()

            for index, row in df.iterrows():
                product_details = dict(row)
                try:
                    description, tokens_used = generate_description(product_details, user_prompt, output_language, style_choice, model_choice, temperature, ai_platform)
                    results.append(description)
                    # Update markdown display with each generated description
                    markdown_content = "\n".join(results[:10]) #show only the first 10 results
                    markdown_placeholder.markdown(markdown_content)
                except Exception as e:
                    st.error(f"Fout bij rij {index + 1}: {e}")
                    results.append(f"Fout bij genereren van beschrijving voor rij {index + 1}.")
                progress_bar.progress((index + 1) / total_rows)

            df["Generated Description"] = results
            st.dataframe(df)

            # Display generated descriptions in markdown format (only first 10)
            st.subheader(text["output_label"])
            # The markdown is already displayed live, no need to display it again.

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=text["download_button"],
                data=csv,
                file_name='generated_descriptions.csv',
                mime='text/csv',
            )
