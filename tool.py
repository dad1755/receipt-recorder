import streamlit as st
import pandas as pd
import os
from io import BytesIO
import openai
import pytesseract
from PIL import Image
import tiktoken

# Set up OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_text_response(extracted_text):
    """Get a response from OpenAI based on the extracted text."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Extract Store Name: /n, Item Purchase: /n, Price: /n. no other symbol. Show Store Name: only once"},
                {"role": "user", "content": extracted_text},
            ],
        )
        return response.choices[0].message['content']
    except Exception as e:
        st.error(f"Error getting response from OpenAI: {e}")
        return None

def calculate_token_count(messages):
    """Calculate the token count accurately."""
    enc = tiktoken.encoding_for_model("gpt-4o-mini")
    token_count = 0
    for message in messages:
        token_count += len(enc.encode(message['content']))
    return token_count

def save_to_excel(username, profile_name, data_to_save):
    """Save extracted data to an Excel file."""
    directory = os.path.join('profiles', username)
    os.makedirs(directory, exist_ok=True)
    excel_file = os.path.join(directory, f"{username}_{profile_name}_data.xlsx")
    df = pd.DataFrame(data_to_save)

    if os.path.exists(excel_file):
        existing_df = pd.read_excel(excel_file)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_excel(excel_file, index=False)
    else:
        df.to_excel(excel_file, index=False)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

def process_uploaded_file(uploaded_file, username, profile_name):
    """Process the uploaded file and extract text."""
    try:
        image = Image.open(uploaded_file)
        extracted_text = pytesseract.image_to_string(image)
        st.image(image, caption='Uploaded Image', use_column_width=True)

        response_data = get_text_response(extracted_text)
        st.subheader("Extracted Details:")
        st.write(response_data)

        if st.button("Save to Excel"):
            data_to_save = [{"Extracted Text": response_data}]
            save_to_excel(username, profile_name, data_to_save)
            st.success(f"Data saved to {username}_{profile_name}_data.xlsx successfully.")
            st.rerun()
    except Exception as e:
        st.error(f"Error processing uploaded file: {e}")

# Streamlit UI components
st.title("OCR and OpenAI Integration")

username = st.text_input("Enter your username:")
profile_name = st.text_input("Enter your profile name:")
uploaded_file = st.file_uploader("Upload an image file (JPEG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file and username and profile_name:
    process_uploaded_file(uploaded_file, username, profile_name)
