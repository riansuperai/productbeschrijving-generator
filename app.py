# File upload
uploaded_file = st.file_uploader(text["upload_label"], type=["csv", "xlsx"])
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.write("### Uploaded File Preview:")
        st.dataframe(df)
        
        # Voeg de genereer-knop toe
        if st.button(text["generate_button"]):
            if "Productdetails" in df.columns:
                with st.spinner(text["progress_message"]):
                    descriptions = []
                    for _, row in df.iterrows():
                        product_details = row.to_dict()
                        description, tokens_used = generate_description(
                            product_details, user_prompt, output_language, style_choice, model_choice, temperature, ai_platform
                        )
                        descriptions.append(description)

                    df["Generated Description"] = descriptions
                    st.write("### " + text["output_label"])
                    st.dataframe(df)
                    
                    # Downloadoptie
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=text["download_button"],
                        data=csv,
                        file_name="generated_descriptions.csv",
                        mime="text/csv",
                    )
            else:
                st.error("Het geüploade bestand bevat geen kolom 'Productdetails'. Controleer het bestand en probeer opnieuw.")

    except Exception as e:
        st.error(f"Error reading file: {e}")
