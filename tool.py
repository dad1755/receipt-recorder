import streamlit as st
import pandas as pd
import os
from io import BytesIO
import openai
from PIL import Image
import numpy as np
import easyocr
import tiktoken
import openai
# Set up OpenAI API key
openai.api_key = st.secrets["openai"]["api_key"]

# Initialize EasyOCR Reader (with English language support)
reader = easyocr.Reader(['en'], gpu=False)  # GPU is disabled for simplicity. Enable if necessary.

def get_text_response(extracted_text):
    """Get a response from OpenAI based on the extracted text."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Extract Store Name: /n, Item Purchase: /n, Price: /n. No other symbol. Show Store Name: only once."},
                {"role": "user", "content": extracted_text},
            ],
        )
        return response.choices[0].message['content']
    except Exception as e:
        st.error(f"Error getting response from OpenAI: {e}")
        return None

def calculate_token_count(messages):
    """Calculate the token count accurately."""
    try:
        enc = tiktoken.encoding_for_model("gpt-4o-mini")
        token_count = 0
        for message in messages:
            token_count += len(enc.encode(message['content']))
        return token_count
    except Exception as e:
        st.error(f"Error calculating token count: {e}")
        return 0

def extract_text_from_image(image):
    """Use EasyOCR to extract text from the image."""
    try:
        image_np = np.array(image)  # Convert PIL image to NumPy array
        result = reader.readtext(image_np)

        if result:
            extracted_text = "\n".join([detection[1] for detection in result])
            return extracted_text
        else:
            st.warning("No text detected. Please try another image.")
            return ""

    except Exception as e:
        st.error(f"Error extracting text from image: {e}")
        return ""

def process_uploaded_file(uploaded_file, username, profile_name):
    """Process the uploaded file and extract text."""
    try:
        image = Image.open(uploaded_file)
        extracted_text = extract_text_from_image(image)
        st.image(image, caption='Uploaded Image', use_column_width=True)

        response_data = get_text_response(extracted_text)
        st.subheader("Extracted Details:")
        st.write(response_data)

        if st.button("Save to Excel"):
            data_to_save = [{"Extracted Text": response_data}]
            output = save_to_excel(st.session_state["username"], profile_name, data_to_save)  # Pass username from session state
            if output:
                st.download_button(
                    label="Download Excel",
                    data=output,
                    file_name=f"{st.session_state['username']}_{profile_name}_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            st.success(f"Data saved to {st.session_state['username']}_{profile_name}_data.xlsx successfully.")
            st.rerun()
    except Exception as e:
        st.error(f"Error processing uploaded file: {e}")


# Streamlit UI components
st.title("OCR and OpenAI Integration")

# Collect user information
username = st.text_input("Enter your username:")
profile_name = st.text_input("Enter your profile name:")
uploaded_file = st.file_uploader("Upload an image file (JPEG/PNG)", type=["jpg", "jpeg", "png"])

# Ensure all inputs are provided before processing
if uploaded_file and username and profile_name:
    process_uploaded_file(uploaded_file, username, profile_name)
else:
    if not username:
        st.warning("Please enter your username.")
    if not profile_name:
        st.warning("Please enter your profile name.")
    if not uploaded_file:
        st.warning("Please upload an image file.")
